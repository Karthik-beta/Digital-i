import { Component, OnInit, ViewChild } from '@angular/core';
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

    @ViewChild('dt') dt: Table;

    // Static data for dropdown
    databases: any[] = [
        { name: 'PostgreSQL', value: 'POSTGRESQL' },
        { name: 'Microsoft SQL Server', value: 'MS_SQL' }
    ];

    directions: any[] = [
        { name: 'IN', value: 'IN' },
        { name: 'OUT', value: 'OUT' },
        { name: 'BOTH', value: 'BOTH' }
    ]

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
    rowsPerPageOptions: number[] = [10, 20, 30, 50];
    rows: number = this.rowsPerPageOptions[0];

    rangeDates: Date[];
    ModalTitle: string = "";
    display: boolean = false;
    searchQuery: string = '';

    id: number | null = null;
    device_no: string = '';
    serial_number: string = '';
    selectedDirection: string = '';
    direction_of_use: string = '';
    purpose_of_device: string = '';
    ip_address: string = '';
    company: number | null = null;
    location: number | null = null;

    selectedCompany: any = null;
    selectedLocation: any = null;

    companies: any[] = [];
    locations: any[] = [];

    constructor(private service: SharedService, private messageService: MessageService) { }

    ngOnInit() {
        // databases is already initialized above, no need to repeat here
        this.loadDatabaseCredentials();
        this.getCompaniesList();
        this.getLocationsList();
    }

    getCompaniesList(): void {

        const params: any = {
            page: 1,
            page_size: 1000,
            sortField: '',
            ordering: '',
        };

        this.service.getCompanies(params).pipe(
            finalize(() => this.loading = false)
        ).subscribe(
            (response: any) => {
                if (response && Array.isArray(response.results)) {
                    this.companies = response.results; // Data for the current page
                    console.log('Loaded', this.companies);
                } else {
                    console.warn('API response for companies list is not in expected format:', response);
                    this.companies = [];
                }
            },
            (error: any) => {
                console.error('Error fetching companies list:', error);
                this.companies = []; // Clear data on error
            }
        );
    }

    getLocationsList(): void {

        const params: any = {
            page: 1,
            page_size: 1000,
            sortField: '',
            ordering: '',
        };

        this.service.getLocations(params).pipe(
            finalize(() => this.loading = false)
        ).subscribe(
            (response: any) => {
                if (response && Array.isArray(response.results)) {
                    this.locations = response.results; // Data for the current page
                    console.log(`Loaded ${this.locations.length} locations`);
                } else {
                    console.warn('API response for locations list is not in expected format:', response);
                    this.locations = [];
                }
            },
            (error: any) => {
                console.error('Error fetching locations list:', error);
                this.locations = []; // Clear data on error
            }
        );
    }

    onSearchChange(query: string): void {
        this.searchQuery = query;
        this.dt.filterGlobal(query, 'contains');
    }

    getBiometricsDevicesList(event: LazyLoadEvent) {
        this.loading = true;

        const params: any = {
            page: ((event.first || 0) / (event.rows || 5) + 1).toString(),
            page_size: (event.rows || 10).toString(),
            sortField: 'id',
            sortOrder: 1,
            search: this.searchQuery || '',
        };

        this.service.getBiometricsDevicesList(params).pipe(
            finalize(() => this.loading = false)
        ).subscribe(
            (response: any) => {
                if (response && Array.isArray(response.results) && response.count !== undefined) {
                    this.biometricsDevices = response.results; // Data for the current page
                    this.totalRecords = response.count; // Total count of ALL records
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
                    // console.log('Mapping credentials from data:', credential);

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

    addClick() {
        this.ModalTitle = "Add Device Configuration";
        this.display = true;
        this.id = null;
        this.device_no = '';
        this.serial_number = '';
        this.selectedDirection = '';
        this.direction_of_use = '';
        this.purpose_of_device = '';
        this.ip_address = '';
        this.selectedCompany = null;
        this.selectedLocation = null;
    }

    editClick(item: any) {
        this.ModalTitle = "Edit Device Configuration";
        this.display = true;
        console.log('Edit clicked for item:', item);
        this.id = item.id;
        this.device_no = item.device_no;
        this.serial_number = item.serial_number;
        this.selectedDirection = item.direction_of_use;
        this.purpose_of_device = item.purpose_of_device;
        this.ip_address = item.ip_address;
        // Find and assign the full company and location objects
        this.selectedCompany = this.companies.find(company => company.id === item.company) || null;
        this.selectedLocation = this.locations.find(location => location.id === item.location) || null;

        console.log('Edit form populated with:', {
            selectedCompany: this.selectedCompany,
            selectedLocation: this.selectedLocation
        });
    }

    addDevice() {
        const deviceData = {
            device_no: this.device_no,
            serial_number: this.serial_number,
            direction_of_use: this.selectedDirection,
            purpose_of_device: this.purpose_of_device,
            ip_address: this.ip_address,
            company: this.company,
            location: this.location
        };

        console.log('Adding device with data:', deviceData);

        this.service.addBiometricsDevice(deviceData).subscribe(
            (response: any) => {
                console.log('Add device response:', response);
                if (response && response.success) {
                    // this.messageService.add({severity: 'success', summary: 'Device Added', detail: 'Device was added successfully'});

                } else {
                    // this.messageService.add({severity: 'error', summary: 'Error', detail: 'Failed to add device'});
                }
                this.messageService.add({severity: 'success', summary: 'Device Added', detail: 'Device was added successfully'});
                this.getBiometricsDevicesList({ first: 0, rows: this.rows });
                this.display = false;
            },
            (error: any) => {
                console.error('Error adding device:', error);
                this.messageService.add({severity: 'error', summary: 'Error', detail: 'Failed to add device'});
            }
        );
    }

    assignCompanyId(selectedCompany: any) {
        this.company = selectedCompany ? selectedCompany.id : null;
        console.log("Selected Company:", selectedCompany);
        console.log("Selected Company ID:", this.company);
    }

    assignLocationId(selectedLocation: any) {
        this.location = selectedLocation ? selectedLocation.id : null;
    }

    updateDevice() {
        const deviceData = {
            id: this.id,
            device_no: this.device_no,
            serial_number: this.serial_number,
            direction_of_use: this.selectedDirection,
            purpose_of_device: this.purpose_of_device,
            ip_address: this.ip_address,
            company: this.company,
            location: this.location
        };

        console.log('Updating device with data:', deviceData);

        this.service.updateBiometricsDevice(this.id, deviceData).subscribe(
            (response: any) => {
                console.log('Update device response:', response);
                if (response && response.success) {
                    this.messageService.add({severity: 'success', summary: 'Device Updated', detail: 'Device was updated successfully'});
                    this.getBiometricsDevicesList({ first: 0, rows: this.rows });
                    this.display = false;
                } else {
                    this.messageService.add({severity: 'error', summary: 'Error', detail: 'Failed to update device'});
                }
            },
            (error: any) => {
                console.error('Error updating device:', error);
                this.messageService.add({severity: 'error', summary: 'Error', detail: 'Failed to update device'});
            }
        );
    }

    deleteDevice(item: any) {
        this.service.deleteBiometricsDevice(item.id).subscribe(
            (response: any) => {
                console.log('Delete device response:', response);
                if (response && response.success) {
                    // this.messageService.add({severity: 'success', summary: 'Device Deleted', detail: 'Device was deleted successfully'});
                    // this.getBiometricsDevicesList({ first: 0, rows: this.rows });
                } else {
                    // this.messageService.add({severity: 'error', summary: 'Error', detail: 'Failed to delete device'});
                }
                this.messageService.add({severity: 'success', summary: 'Device Deleted', detail: 'Device was deleted successfully'});
                this.getBiometricsDevicesList({ first: 0, rows: this.rows });
            },
            (error: any) => {
                console.error('Error deleting device:', error);
                this.messageService.add({severity: 'error', summary: 'Error', detail: 'Failed to delete device'});
            }
        );
    }
}
