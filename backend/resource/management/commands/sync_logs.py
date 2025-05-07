# management/commands/sync_logs.py
from django.core.management.base import BaseCommand
import psycopg2
import pyodbc
from datetime import datetime
import sys
import os
from typing import List, Tuple, Optional
from django.core.exceptions import ObjectDoesNotExist
from resource.models import ExternalDatabaseCredential

class Command(BaseCommand):
    help = 'Sync logs from an external database (MSSQL/PostgreSQL) to PostgreSQL with batch processing'

    # Batch size for processing records
    BATCH_SIZE = 100000

    def get_external_database_credential(self) -> Optional[ExternalDatabaseCredential]:
        """
        Fetch the ExternalDatabaseCredential record from the database.
        If no record exists, return None.
        """
        try:
            # Assuming only one record should exist
            credential = ExternalDatabaseCredential.objects.get()
            return credential
        except ObjectDoesNotExist:
            self.stderr.write(self.style.ERROR("No external database credentials found. Sync aborted."))
            return None

    # def get_mssql_connection(self, credential: ExternalDatabaseCredential) -> pyodbc.Connection:
    #     """
    #     Establish connection to MSSQL database using credentials from the ExternalDatabaseCredential model.
    #     """
    #     try:
    #         conn_str = f"DRIVER={credential.database_type};SERVER={credential.host};PORT={credential.port};DATABASE={credential.name};UID={credential.user};PWD={credential.password}"
    #         self.stdout.write(f"Connecting to MSSQL at {credential.host}")
    #         conn = pyodbc.connect(conn_str, timeout=30)
    #         cursor = conn.cursor()
    #         cursor.execute(f"SELECT TOP 1 * FROM [{credential.name}].[dbo].[{credential.table_name}]")
    #         cursor.fetchone()
    #         self.stdout.write(self.style.SUCCESS("Successfully connected to MSSQL"))
    #         return conn
    #     except pyodbc.Error as e:
    #         self.stderr.write(self.style.ERROR(f"MSSQL Connection Error: {str(e)}"))
    #         raise

    def get_mssql_connection(self, credential: ExternalDatabaseCredential) -> pyodbc.Connection:
        """
        Establish connection to MSSQL database using credentials from the ExternalDatabaseCredential model.
        """
        try:
            # Construct a valid ODBC connection string
            conn_dict = {
                "DRIVER": "ODBC Driver 17 for SQL Server",  # 17 or 18 
                "SERVER": f"{credential.host},{credential.port}",
                "DATABASE": credential.name,
                "UID": credential.user,
                "PWD": credential.password,
                "TrustServerCertificate": "Yes",
            }
            conn_str = ';'.join(f"{k}={v}" for k, v in conn_dict.items() if v is not None)

            self.stdout.write(f"Connecting to MSSQL at {credential.host}:{credential.port}")
            conn = pyodbc.connect(conn_str, timeout=30)

            # Test query to validate connection
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP 1 * FROM [{credential.name}].[dbo].[{credential.table_name}]")
            cursor.fetchone()

            self.stdout.write(self.style.SUCCESS("Successfully connected to MSSQL"))
            return conn

        except pyodbc.Error as e:
            self.stderr.write(self.style.ERROR(f"MSSQL Connection Error: {str(e)}"))
            raise


    def get_postgresql_connection(self) -> psycopg2.extensions.connection:
        """
        Establish connection to PostgreSQL database with error handling
        """
        try:
            pg_config = {
                'dbname': os.getenv('DATABASE_NAME'),
                'user': os.getenv('DATABASE_USER'),
                'password': os.getenv('DATABASE_PASSWORD'),
                'host': os.getenv('DATABASE_HOST'),
                'port': os.getenv('DATABASE_PORT')
            }
            self.stdout.write(f"Connecting to PostgreSQL at {pg_config['host']}")
            conn = psycopg2.connect(**pg_config)
            conn.autocommit = True
            # Test connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("Successfully connected to PostgreSQL"))
            return conn
        except psycopg2.Error as e:
            self.stderr.write(self.style.ERROR(f"PostgreSQL Connection Error: {str(e)}"))
            raise

    def get_mssql_table_info(self, ms_cursor, credential: ExternalDatabaseCredential) -> tuple:
        """
        Get information about existing records for efficient syncing from MSSQL
        """
        try:
            ms_cursor.execute(f"""
                SELECT COALESCE(MAX([id]), 0), COUNT(*)
                FROM [{credential.name}].[dbo].[{credential.table_name}]
            """)
            max_id, total_count = ms_cursor.fetchone()
            return max_id, total_count or 0
        except pyodbc.Error as e:
            self.stderr.write(self.style.ERROR(f"Error getting MSSQL table info: {str(e)}"))
            raise

    def get_postgresql_table_info(self, pg_cursor) -> tuple:
        """
        Get information about existing records for efficient syncing from PostgreSQL
        """
        try:
            pg_cursor.execute("""
                SELECT COALESCE(MAX(id), 0), COUNT(*)
                FROM public.logs
            """)
            max_id, total_count = pg_cursor.fetchone()
            return max_id, total_count or 0
        except psycopg2.Error as e:
            self.stderr.write(self.style.ERROR(f"Error getting PostgreSQL table info: {str(e)}"))
            raise

    def fetch_mssql_batch(self, ms_cursor, last_id: int, credential: ExternalDatabaseCredential) -> List[Tuple]:
        """
        Fetch a batch of records from MSSQL based on the credential provided.
        """
        query = f"""
            SELECT DISTINCT TOP (?)
                [{credential.id_field}], [{credential.employeeid_field}], [{credential.direction_field}], 
                [{credential.shortname_field}], [{credential.serialno_field}], [{credential.log_datetime_field}]
            FROM [{credential.name}].[dbo].[{credential.table_name}]
            WHERE [{credential.id_field}] > ?
            ORDER BY [{credential.id_field}]
        """
        try:
            ms_cursor.execute(query, (self.BATCH_SIZE, last_id))
            return ms_cursor.fetchall()
        except pyodbc.Error as e:
            self.stderr.write(self.style.ERROR(f"Error fetching from MSSQL: {str(e)}"))
            raise

    def fetch_postgresql_batch(self, pg_cursor, last_id: int, credential: ExternalDatabaseCredential) -> List[Tuple]:
        """
        Fetch a batch of records from PostgreSQL based on the credential provided.
        """
        query = f"""
            SELECT DISTINCT
                {credential.id_field}, {credential.employeeid_field}, {credential.direction_field}, 
                {credential.shortname_field}, {credential.serialno_field}, {credential.log_datetime_field}
            FROM {credential.table_name}
            WHERE {credential.id_field} > %s
            ORDER BY {credential.id_field}
            LIMIT %s
        """
        try:
            pg_cursor.execute(query, (last_id, self.BATCH_SIZE))
            return pg_cursor.fetchall()
        except psycopg2.Error as e:
            self.stderr.write(self.style.ERROR(f"Error fetching from PostgreSQL: {str(e)}"))
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
            # Fetch database credentials from ExternalDatabaseCredential model
            credential = self.get_external_database_credential()
            if not credential:
                return  # Exit if no credentials found

            # Establish database connections based on the credential type
            if credential.database_type == 'MS_SQL':
                ms_conn = self.get_mssql_connection(credential)
                ms_cursor = ms_conn.cursor()
                external_last_id, external_count = self.get_mssql_table_info(ms_cursor, credential)
            elif credential.database_type == 'POSTGRESQL':
                pg_conn = self.get_postgresql_connection()
                pg_cursor = pg_conn.cursor()
                external_last_id, external_count = self.get_postgresql_table_info(pg_cursor)
            else:
                self.stdout.write(self.style.ERROR(f"Unsupported database type: {credential.database_type}. Sync aborted."))
                return  # Exit if database type is unsupported
            
            # Always fetch the last_id from the internal PostgreSQL database
            if not pg_conn:
                pg_conn = self.get_postgresql_connection()
            pg_cursor = pg_conn.cursor()
            internal_last_id, internal_count = self.get_postgresql_table_info(pg_cursor)

            # Determine the starting last_id for syncing
            last_id = internal_last_id

            self.stdout.write(f"Starting sync from ID: {last_id}")
            self.stdout.write(f"Existing records in the external database: {external_count}")
            self.stdout.write(f"Existing records in the internal database: {internal_count}")

            while True:
                try:
                    if credential.database_type == 'MS_SQL':
                        # Fetch batch from MSSQL
                        records = self.fetch_mssql_batch(ms_cursor, last_id, credential)
                    elif credential.database_type == 'POSTGRESQL':
                        # Fetch batch from PostgreSQL
                        records = self.fetch_postgresql_batch(pg_cursor, last_id, credential)
                    
                    if not records:
                        self.stdout.write("No more records to process")
                        break

                    # Start transaction for batch processing
                    pg_conn.autocommit = False
                    
                    # Insert batch in PostgreSQL
                    inserted_count = self.insert_postgresql_batch(pg_cursor, records)
                    # Manually trigger the signal logic
                    # trigger_all_logs_update(records)
                    
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