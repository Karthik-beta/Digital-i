#!/bin/bash
set -e

# Start SQL Server
/opt/mssql/bin/sqlservr &

# Function to check if SQL Server is ready
function wait_for_sql() {
    for i in {1..60}; do
        # Check if SQL Server is responding
        if /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Digitali@password123 -Q "SELECT 1" &> /dev/null; then
            echo "SQL Server is ready"
            return 0
        fi
        echo "Waiting for SQL Server to start... ($i/60)"
        sleep 1
    done
    echo "Timeout waiting for SQL Server to start"
    return 1
}

# Wait for SQL Server to be ready
wait_for_sql

# Run initialization scripts
for f in /docker-entrypoint-initdb.d/*.sql
do
    echo "Running $f"
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Digitali@password123 -i $f
done

# Keep container running
tail -f /dev/null