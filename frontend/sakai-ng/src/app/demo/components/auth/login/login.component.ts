import { Component } from '@angular/core';
import { LayoutService } from 'src/app/layout/service/app.layout.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { AuthService } from 'src/app/service/auth-service/auth.service';
import * as CryptoJS from 'crypto-js';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styles: [`
        :host ::ng-deep .pi-eye,
        :host ::ng-deep .pi-eye-slash {
            transform:scale(1.6);
            margin-right: 1rem;
            color: var(--primary-color) !important;
        }
    `]
})
export class LoginComponent {

    valCheck: string[] = ['remember'];

    username!: string;

    password!: string;

    rememberMe: boolean = false;

    private encryptionKey: string = '80lfYUY1VFWeFHVYAvsrBTPmPKQzpHf3';

    constructor(
        public layoutService: LayoutService,
        private messageService: MessageService,
        private router: Router,
        private authService: AuthService
    ) { }

    ngOnInit(): void {
        this.loadCredentials();
    }

    navigateIfMatch(): void {
        if (this.authService.login(this.username, this.password)) {
            if (this.rememberMe) {
                this.saveCredentials();
            } else {
                this.clearCredentials();
            }
            this.router.navigate(['/']);
        }
        else {
            console.log('Login failed');
            this.messageService.add({ severity: 'error', summary: 'Login Failed', detail: 'Invalid username or password' });
        }
    }

    saveCredentials(): void {
        const encryptedUsername = CryptoJS.AES.encrypt(this.username, this.encryptionKey).toString();
        localStorage.setItem('username', encryptedUsername);
        const encryptedPassword = CryptoJS.AES.encrypt(this.password, this.encryptionKey).toString();
        localStorage.setItem('password', encryptedPassword);
    }

    loadCredentials(): void {
        const savedUsername = localStorage.getItem('username');
        const savedPassword = localStorage.getItem('password');
        if (savedUsername && savedPassword) {
            // Decrypt and retrieve the stored username
            const usernameBytes = CryptoJS.AES.decrypt(savedUsername, this.encryptionKey);
            this.username = usernameBytes.toString(CryptoJS.enc.Utf8);

            // Decrypt and retrieve the stored password
            const passwordBytes = CryptoJS.AES.decrypt(savedPassword, this.encryptionKey);
            this.password = passwordBytes.toString(CryptoJS.enc.Utf8);

            this.rememberMe = true;
        }
    }

    clearCredentials(): void {
        localStorage.removeItem('username');
        localStorage.removeItem('password');
    }

}
