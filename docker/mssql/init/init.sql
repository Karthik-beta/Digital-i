-- Create the database
CREATE DATABASE biotime;
GO

-- Switch to the new database
USE biotime;
GO

-- Create your tables
CREATE TABLE logs (
    id BIGINT PRIMARY KEY,
    employeeid NVARCHAR(255),
    direction NVARCHAR(255),
    shortname NVARCHAR(255),
    serialno NVARCHAR(255),
    log_datetime DATETIME
);
GO

-- Add any initial data if needed
-- INSERT INTO logs (id, employeeid, direction, shortname, serialno, log_datetime)
-- VALUES (1, 'EMP001', 'IN', 'John', 'DEV123', GETDATE());
-- GO