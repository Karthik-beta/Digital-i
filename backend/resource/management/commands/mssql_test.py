# management/commands/check_mssql.py
from django.core.management.base import BaseCommand
import pyodbc
import os

# Load the correct environment file
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

class Command(BaseCommand):
    help = 'Check MSSQL connection and query logs table'

    def get_database_settings(self):
        return {
            'ENGINE': 'mssql',
            'NAME': os.getenv('MSSQL_DATABASE_NAME'),
            'USER': os.getenv('MSSQL_DATABASE_USER'),
            'PASSWORD': os.getenv('MSSQL_DATABASE_PASSWORD'),
            'HOST': os.getenv('MSSQL_DATABASE_HOST'),
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        }

    def get_connection_string(self):
        settings = self.get_database_settings()
        return f"DRIVER={{{settings['OPTIONS']['driver']}}};" \
               f"SERVER={settings['HOST']};" \
               f"DATABASE={settings['NAME']};" \
               f"UID={settings['USER']};" \
               f"PWD={settings['PASSWORD']};"

    def handle(self, *args, **options):
        try:
            # Create connection using pyodbc directly
            conn_str = self.get_connection_string()
            connection = pyodbc.connect(conn_str)
            cursor = connection.cursor()
            
            self.stdout.write(
                self.style.SUCCESS('Successfully connected to MSSQL database')
            )

            # Query the logs table
            cursor.execute('SELECT TOP 5 * FROM [biotime].[dbo].[logs]')
            rows = cursor.fetchall()
            
            if rows:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully queried logs table. Found {len(rows)} records')
                )
                # Print column names
                columns = [column[0] for column in cursor.description]
                self.stdout.write(f"Columns: {', '.join(columns)}")
                
                # Print first 5 rows
                self.stdout.write("\nFirst 5 records:")
                for row in rows:
                    self.stdout.write(str(row))
            else:
                self.stdout.write(
                    self.style.WARNING('No records found in logs table')
                )

            # Clean up
            cursor.close()
            connection.close()

        except pyodbc.Error as e:
            self.stdout.write(
                self.style.ERROR(f'ODBC Error: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {str(e)}')
            )