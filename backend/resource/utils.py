import pyodbc
import psycopg2

def test_connection(database_type, host, port, user, password, database_name, table_name, fields):
    """
    Test the connection to the specified external database and validate the table and its fields.
    """

    if database_type == 'MS_SQL':
        try:
            # Connect to the MS SQL database
            conn = pyodbc.connect(
                driver='{ODBC Driver 17 for SQL Server}',  # Or the appropriate driver for your system
                server=host,
                port=port,
                database=database_name,
                user=user,
                password=password
            )
            cursor = conn.cursor()

            # Check if the table exists
            cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", table_name)
            if cursor.fetchone() is None:
                return f"Table '{table_name}' does not exist in the database."

            # Check if all required fields exist in the table
            for field in fields:
                cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? AND COLUMN_NAME = ?", table_name, field)
                if cursor.fetchone() is None:
                    return f"Field '{field}' does not exist in table '{table_name}'."

            conn.close()
            return True  # Connection and table/field validation successful
        except pyodbc.Error as e:
            return f"Connection failed: {str(e)}"

    elif database_type == 'POSTGRESQL':
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=database_name
            )
            cursor = conn.cursor()

            # Check if the table exists
            cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
            if not cursor.fetchone()[0]:
                return f"Table '{table_name}' does not exist in the database."

            # Check if all required fields exist in the table
            for field in fields:
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name = %s", (table_name, field))
                if not cursor.fetchone():
                    return f"Field '{field}' does not exist in table '{table_name}'."

            conn.close()
            return True  # Connection and table/field validation successful
        except psycopg2.Error as e:
            return f"Connection failed: {str(e)}"

    else:
        return "Unsupported database type"
