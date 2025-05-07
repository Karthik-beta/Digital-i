package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"
)

// Function to execute a command
func runDockerCommand(command []string) error {
	// Create a command object
	cmd := exec.Command(command[0], command[1:]...)
	// Run the command and capture output/errors
	out, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("error running command %v: %v", command, err)
	}
	fmt.Printf("Command output: %s\n", string(out))
	return nil
}

// Function to clear cache (dummy example, modify for your use case)
func clearCache() {
	cacheDir := "C:\\path\\to\\cache" // Replace with your actual cache directory
	err := os.RemoveAll(cacheDir)     // Deletes the cache directory and its contents
	if err != nil {
		log.Printf("Error clearing cache: %v\n", err)
	} else {
		log.Println("Cache cleared successfully.")
	}
}

func main() {
	// Run the loop indefinitely
	for {
		// First command: docker exec skf_mys-django-1 python manage.py absentees
		err := runDockerCommand([]string{"docker", "exec", "skf_mys-django-1", "python", "manage.py", "absentees"})
		if err != nil {
			log.Printf("Error running absentees command: %v\n", err)
		}

		// Second command: docker exec skf_mys-django-1 python manage.py task
		err = runDockerCommand([]string{"docker", "exec", "skf_mys-django-1", "python", "manage.py", "task"})
		if err != nil {
			log.Printf("Error running task command: %v\n", err)
		}

		// Clear cache (if applicable)
		clearCache()

		// Wait for 1 minute before running the loop again
		time.Sleep(1 * time.Minute)
	}
}
