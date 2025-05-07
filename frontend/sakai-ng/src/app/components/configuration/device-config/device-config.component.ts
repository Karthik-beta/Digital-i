import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/shared.service';
import { finalize } from 'rxjs/operators';
import { MessageService } from 'primeng/api';
import { LazyLoadEvent } from 'primeng/api';
import { Table } from 'primeng/table';

@Component({
    selector: 'app-device-config',
    templateUrl: './device-config.component.html',
    styleUrl: './device-config.component.scss'
})
export class DeviceConfigComponent implements OnInit {

    // Static data for dropdown
    databases: any[] = [
        { name: 'PostgreSQL', value: 'POSTGRESQL' },
        { name: 'Microsoft SQL Server', value: 'MS_SQL' }
    ];

    // Form data variables
    selectedDatabase: string = '';
    database_name: string = '';
    database_user: string = '';
    database_password: string = '';
    database_host: string = '';
    database_port: number = 0;
    table_name: string = '';
    id_field: string = '';
    employeeid_field: string = '';
    direction_field: string = '';
    shortname_field: string = '';
    serialno_field: string = '';
    log_datetime_field: string = '';

    // Internal state variables
    private credentialId: number | null = null;

    // UI state variables
    loading: boolean = false;
    testResult: string | null = null;

    biometricsDevices: any;
    totalRecords: number = 0;
    rows: number = 10;

    rangeDates: Date[];
    ModalTitle: string = "";
    display: boolean = false;

    constructor(private service: SharedService, private messageService: MessageService) { }

    ngOnInit() {
        // databases is already initialized above, no need to repeat here
        this.loadDatabaseCredentials();
        this.getBiometricsDevicesList();
    }

    getBiometricsDevicesList() {
        this.loading = true;

        console.log('LazyLoadEvent:', event); // Inspect the event object

        this.service.getBiometricsDevicesList().pipe(
            finalize(() => this.loading = false)
        ).subscribe(
            (response: any) => { // Assuming API returns an object with results and total
                if (response && Array.isArray(response.results) && response.totalRecords !== undefined) {
                    this.biometricsDevices = response.results; // Data for the current page
                    this.totalRecords = response.totalRecords; // Total count of ALL records
                    console.log(`Loaded ${this.biometricsDevices.length} devices, Total: ${this.totalRecords}`);
                } else {
                    console.warn('API response for devices list is not in expected format:', response);
                    this.biometricsDevices = [];
                    this.totalRecords = 0;
                }
            },
            (error: any) => {
                console.error('Error fetching biometrics devices list:', error);
                this.biometricsDevices = []; // Clear data on error
                this.totalRecords = 0;     // Reset total on error
            }
        );
    }

    loadDatabaseCredentials() {
        this.loading = true;
        this.testResult = null;

        this.service.getDatabaseCredentials().pipe(
            finalize(() => this.loading = false)
        ).subscribe(
            (data: any) => {
                // Assuming data is either a single object or an array with one object
                const credential = (Array.isArray(data) && data.length > 0) ? data[0] : data;

                if (credential && typeof credential === 'object') {
                    console.log('Mapping credentials from data:', credential);

                    this.credentialId = credential.id; // Store the ID
                    this.mapCredentialToForm(credential); // Use helper method

                } else {
                    console.warn('API response is empty or not in expected format:', data);
                    this.credentialId = null;
                    this.clearFormVariables(); // Clear form if no data loaded
                }
            },
            (error: any) => {
                console.error('Error fetching database credentials:', error);
                this.testResult = 'Failed to load existing configuration.';
                this.credentialId = null;
                this.clearFormVariables(); // Clear form on error
            }
        );
    }

    // Helper method to map credential object properties to form variables
    private mapCredentialToForm(credential: any) {
         this.selectedDatabase = credential.database_type || '';
         this.database_name = credential.name || '';
         this.database_user = credential.user || '';
         this.database_password = credential.password || '';
         this.database_host = credential.host || '';
         this.database_port = credential.port || 0;
         this.table_name = credential.table_name || '';
         this.id_field = credential.id_field || '';
         this.employeeid_field = credential.employeeid_field || '';
         this.direction_field = credential.direction_field || '';
         this.shortname_field = credential.shortname_field || '';
         this.serialno_field = credential.serialno_field || '';
         this.log_datetime_field = credential.log_datetime_field || '';
         console.log('Database credentials mapped to variables. ID:', this.credentialId);
    }

    // Helper to clear form variables
    private clearFormVariables() {
        this.selectedDatabase = '';
        this.database_name = '';
        this.database_user = '';
        this.database_password = '';
        this.database_host = '';
        this.database_port = 0;
        this.table_name = '';
        this.id_field = '';
        this.employeeid_field = '';
        this.direction_field = '';
        this.shortname_field = '';
        this.serialno_field = '';
        this.log_datetime_field = '';
        console.log('Form variables cleared.');
    }

    // Method to test the database connection
    testDatabaseConnection() {
        this.loading = true;
        this.testResult = null;

        console.log('Testing database connection with the following details:', {
            database_type: this.selectedDatabase,
            host: this.database_host,
            port: this.database_port,
            name: this.database_name,
            user: this.database_user,
            password: this.database_password,

            table_name: this.table_name,
            id_field: this.id_field,
            employeeid_field: this.employeeid_field,
            direction_field: this.direction_field,
            shortname_field: this.shortname_field,
            serialno_field: this.serialno_field,
            log_datetime_field: this.log_datetime_field,
        });

        const connectionDetails = {
            database_type: this.selectedDatabase,
            host: this.database_host,
            port: this.database_port,
            name: this.database_name,
            user: this.database_user,
            password: this.database_password,

            table_name: this.table_name,
            id_field: this.id_field,
            employeeid_field: this.employeeid_field,
            direction_field: this.direction_field,
            shortname_field: this.shortname_field,
            serialno_field: this.serialno_field,
            log_datetime_field: this.log_datetime_field,
        };

        console.log('Testing connection...', connectionDetails);

        // Call the service method to test the connection
        // (Requires SharedService.testDatabaseConnection)
        this.service.testDatabaseConnection(connectionDetails).pipe(
             finalize(() => this.loading = false)
        )
        .subscribe(
            (response: any) => {
                console.log('Test connection response:', response);
                if (response && response.success) {
                    this.testResult = 'Connection Successful!';
                } else if (response && response.message) {
                     this.testResult = 'Connection Test: ' + response.message;
                } else {
                    this.testResult = 'Connection Test completed with unexpected response.';
                }
                this.messageService.add({severity: 'success', summary: 'Connection Sucessful', detail: 'Conection with the database was successful'});
            },
            (error: any) => {
                console.error('Error testing database connection:', error);
                this.testResult = 'Connection Failed: ' + (error.error?.message || error.message || 'An unexpected error occurred.');
                this.messageService.add({severity: 'error', summary: 'Connection Failed', detail: 'Conection with the database failed'});
            }
        );
    }

    // Method to update/save the database configuration
    updateDatabaseConfig() {
        this.loading = true;
        this.testResult = null;

        const configData = {
            id: this.credentialId, // Include ID for update/create logic on backend
            database_type: this.selectedDatabase,
            name: this.database_name,
            user: this.database_user,
            password: this.database_password,
            host: this.database_host,
            port: this.database_port,
            table_name: this.table_name,
            id_field: this.id_field,
            employeeid_field: this.employeeid_field,
            direction_field: this.direction_field,
            shortname_field: this.shortname_field,
            serialno_field: this.serialno_field,
            log_datetime_field: this.log_datetime_field,
        };

        console.log('Saving configuration...', configData);

        // Call the service method to save the configuration
        // (Requires SharedService.updateDatabaseCredentials)
         this.service.updateDatabaseCredentials(configData).pipe(
             finalize(() => this.loading = false)
         )
        .subscribe(
            (response: any) => {
                console.log('Save configuration response:', response);
                 if (response && (response.success || response.id)) {
                     this.testResult = 'Configuration saved successfully!';
                     // Update ID if a new one was created
                     if (response.id && this.credentialId === null) {
                         this.credentialId = response.id;
                         console.log('New configuration ID received:', this.credentialId);
                     }
                 } else if (response && response.message) {
                     this.testResult = 'Save Operation: ' + response.message;
                 } else {
                     this.testResult = 'Configuration saved, but response format unexpected.';
                }
                this.messageService.add({severity: 'success', summary: 'Configuration Saved', detail: 'Configuration was saved successfully'});
            },
            (error: any) => {
                console.error('Error saving configuration:', error);
                this.testResult = 'Failed to save configuration: ' + (error.error?.message || error.message || 'An unexpected error occurred.');
                this.messageService.add({severity: 'error', summary: 'Configuration Failed', detail: 'Configuration was not saved'});
            }
        );
    }
}
