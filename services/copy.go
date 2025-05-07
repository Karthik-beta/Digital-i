package main

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/denisenkom/go-mssqldb"
	_ "github.com/lib/pq"
)

// Database connection settings
const (
	mssqlConnStr = "server=127.0.0.1;user id=Digitali;password=Digitali;database=biotime"
	pgConnStr    = "host=10.38.21.181 port=5432 user=postgres password=password123 dbname=casa sslmode=disable"
)

func fetchLatestIDFromPostgres() (int, error) {
	db, err := sql.Open("postgres", pgConnStr)
	if err != nil {
		return 0, err
	}
	defer db.Close()

	var latestID int
	err = db.QueryRow("SELECT COALESCE(MAX(id), 0) FROM public.logs").Scan(&latestID)
	if err != nil {
		return 0, err
	}
	return latestID, nil
}

func fetchNewRecordsFromMSSQL(latestID int) ([][6]interface{}, error) {
	db, err := sql.Open("sqlserver", mssqlConnStr)
	if err != nil {
		return nil, err
	}
	defer db.Close()

	query := `SELECT [id], [employeeid], [direction], [shortname], [serialno], [log_datetime] 
			  FROM [biotime].[dbo].[logs] WHERE [id] > @latestID`

	rows, err := db.Query(query, sql.Named("latestID", latestID))
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records [][6]interface{}
	for rows.Next() {
		var record [6]interface{}
		err := rows.Scan(&record[0], &record[1], &record[2], &record[3], &record[4], &record[5])
		if err != nil {
			return nil, err
		}
		records = append(records, record)
	}
	return records, nil
}

func insertRecordsIntoPostgres(records [][6]interface{}) error {
	db, err := sql.Open("postgres", pgConnStr)
	if err != nil {
		return err
	}
	defer db.Close()

	insertQuery := `
		INSERT INTO public.logs (id, employeeid, direction, shortname, serialno, log_datetime)
		VALUES ($1, $2, $3, $4, $5, $6)`

	tx, err := db.Begin()
	if err != nil {
		return err
	}

	stmt, err := tx.Prepare(insertQuery)
	if err != nil {
		tx.Rollback()
		return err
	}
	defer stmt.Close()

	for _, record := range records {
		_, err := stmt.Exec(record[0], record[1], record[2], record[3], record[4], record[5])
		if err != nil {
			tx.Rollback()
			return err
		}
	}

	err = tx.Commit()
	if err != nil {
		return err
	}
	return nil
}

func job() {
	latestID, err := fetchLatestIDFromPostgres()
	if err != nil {
		log.Printf("Error fetching latest ID: %v\n", err)
		return
	}

	newRecords, err := fetchNewRecordsFromMSSQL(latestID)
	if err != nil {
		log.Printf("Error fetching new records from MSSQL: %v\n", err)
		return
	}

	if len(newRecords) > 0 {
		err = insertRecordsIntoPostgres(newRecords)
		if err != nil {
			log.Printf("Error inserting records into PostgreSQL: %v\n", err)
			return
		}
		fmt.Printf("Inserted %d new records into PostgreSQL.\n", len(newRecords))
	} else {
		fmt.Println("No new records to insert.")
	}
}

func main() {
	for {
		job()
		time.Sleep(10 * time.Second)
	}
}
