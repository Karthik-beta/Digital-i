# management/commands/sync_logs.py
from django.core.management.base import BaseCommand
import psycopg2
import pyodbc
from datetime import datetime
import sys
import os
from typing import List, Tuple, Optional

class Command(BaseCommand):
    help = 'Sync logs from MSSQL to PostgreSQL with batch processing'

    # Database credentials and configurations
    MSSQL_CONFIG = {
        'ENGINE': 'mssql',
        'driver': '{ODBC Driver 17 for SQL Server}',
        'server': os.getenv('MSSQL_DATABASE_HOST'),
        'database': os.getenv('MSSQL_DATABASE_NAME'),
        'uid': os.getenv('MSSQL_DATABASE_USER'),
        'pwd': os.getenv('MSSQL_DATABASE_PASSWORD')
    }

    POSTGRESQL_CONFIG = {
        'ENGINE': 'django.db.backends.postgresql',
        'dbname': os.getenv('DATABASE_NAME'),
        'user': os.getenv('DATABASE_USER'),
        'password': os.getenv('DATABASE_PASSWORD'),
        'host': os.getenv('DATABASE_HOST'),
        'port': os.getenv('DATABASE_PORT')
    }

    # Batch size for processing records
    BATCH_SIZE = 100000

    def get_mssql_connection(self) -> pyodbc.Connection:
        """
        Establish connection to MSSQL database with detailed error handling
        """
        try:
            conn_str = ';'.join([f"{k}={v}" for k, v in self.MSSQL_CONFIG.items() 
                               if k not in ['ENGINE'] and v is not None])
            
            self.stdout.write(f"Connecting to MSSQL at {self.MSSQL_CONFIG['server']}")
            conn = pyodbc.connect(conn_str, timeout=30)
            
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP 1 * FROM [{self.MSSQL_CONFIG['database']}].[dbo].[logs]")
            cursor.fetchone()
            self.stdout.write(self.style.SUCCESS("Successfully connected to MSSQL"))
            
            return conn

        except pyodbc.Error as e:
            error_msg = f"MSSQL Connection Error: {str(e)}"
            self.stderr.write(self.style.ERROR(error_msg))
            raise

    def get_postgresql_connection(self) -> psycopg2.extensions.connection:
        """
        Establish connection to PostgreSQL database with error handling
        """
        try:
            # Remove ENGINE from connection parameters
            pg_config = {k: v for k, v in self.POSTGRESQL_CONFIG.items() 
                        if k != 'ENGINE' and v is not None}
            
            self.stdout.write(f"Connecting to PostgreSQL at {pg_config['host']}")
            conn = psycopg2.connect(**pg_config)
            conn.autocommit = True  # Set autocommit initially
            
            # Test connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("Successfully connected to PostgreSQL"))
            
            return conn

        except psycopg2.Error as e:
            error_msg = f"PostgreSQL Connection Error: {str(e)}"
            self.stderr.write(self.style.ERROR(error_msg))
            raise

    def get_table_info(self, pg_cursor) -> tuple:
        """
        Get information about existing records for efficient syncing
        """
        try:
            pg_cursor.execute("""
                SELECT COALESCE(MAX(id), 0), COUNT(*)
                FROM public.logs
            """)
            max_id, total_count = pg_cursor.fetchone()
            return max_id, total_count or 0
        except psycopg2.Error as e:
            self.stderr.write(self.style.ERROR(f"Error getting table info: {str(e)}"))
            raise

    def fetch_mssql_batch(self, ms_cursor, last_id: int) -> List[Tuple]:
        """
        Fetch a batch of records from MSSQL
        """
        query = f"""
            SELECT DISTINCT TOP (?)
                [id], [employeeid], [direction], [shortname], [serialno], [log_datetime]
            FROM [{self.MSSQL_CONFIG['database']}].[dbo].[logs]
            WHERE [id] > ?
            ORDER BY [id]
        """
        try:
            ms_cursor.execute(query, (self.BATCH_SIZE, last_id))
            return ms_cursor.fetchall()
        except pyodbc.Error as e:
            self.stderr.write(self.style.ERROR(f"Error fetching from MSSQL: {str(e)}"))
            raise

    def insert_postgresql_batch(self, pg_cursor, records: List[Tuple]) -> int:
        """
        Insert a batch of records into PostgreSQL, skipping duplicates
        """
        insert_query = """
            INSERT INTO public.logs 
                (id, employeeid, direction, shortname, serialno, log_datetime)
            VALUES 
                (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE 
            SET 
                employeeid = EXCLUDED.employeeid,
                direction = EXCLUDED.direction,
                shortname = EXCLUDED.shortname,
                serialno = EXCLUDED.serialno,
                log_datetime = EXCLUDED.log_datetime
            WHERE 
                logs.log_datetime < EXCLUDED.log_datetime
        """
        try:
            # Execute batch insert
            pg_cursor.executemany(insert_query, records)
            return len(records)
        except psycopg2.Error as e:
            self.stderr.write(self.style.ERROR(f"Error inserting into PostgreSQL: {str(e)}"))
            raise

    def handle(self, *args, **options):
        start_time = datetime.now()
        total_records = 0
        ms_conn = None
        pg_conn = None

        try:
            # Establish database connections
            ms_conn = self.get_mssql_connection()
            pg_conn = self.get_postgresql_connection()
            
            ms_cursor = ms_conn.cursor()
            pg_cursor = pg_conn.cursor()

            # Get current state of PostgreSQL table
            last_id, existing_count = self.get_table_info(pg_cursor)
            self.stdout.write(f"Starting sync from ID: {last_id}")
            self.stdout.write(f"Existing records in PostgreSQL: {existing_count}")

            while True:
                try:
                    # Fetch batch from MSSQL
                    records = self.fetch_mssql_batch(ms_cursor, last_id)
                    
                    if not records:
                        self.stdout.write("No more records to process")
                        break

                    # Start transaction for batch processing
                    pg_conn.autocommit = False
                    
                    # Insert batch in PostgreSQL
                    inserted_count = self.insert_postgresql_batch(pg_cursor, records)
                    
                    # Commit the transaction
                    pg_conn.commit()
                    
                    # Reset autocommit to True after transaction
                    pg_conn.autocommit = True
                    
                    # Update last processed ID and counts
                    last_id = records[-1][0]
                    total_records += inserted_count
                    
                    self.stdout.write(
                        f"Processed batch: Records={inserted_count}, "
                        f"Total processed={total_records}, "
                        f"Last ID={last_id}"
                    )

                except Exception as e:
                    if not pg_conn.autocommit:
                        pg_conn.rollback()
                        pg_conn.autocommit = True
                    self.stderr.write(self.style.ERROR(f"Error processing batch: {str(e)}"))
                    raise

            # Log summary
            duration = datetime.now() - start_time
            self.stdout.write(self.style.SUCCESS(
                f"\nSync completed successfully!"
                f"\nTotal records processed: {total_records}"
                f"\nTime taken: {duration}"
                f"\nAverage rate: {total_records / duration.total_seconds():.2f} records/second"
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error occurred: {str(e)}"))
            sys.exit(1)

        finally:
            # Close database connections
            for conn in [ms_conn, pg_conn]:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass