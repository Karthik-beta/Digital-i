// machine.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MachineService {
    private readonly baseUrl = 'http://127.0.0.1:8000';
    private readonly machine = '/machine';
    private readonly shopfloor = '/shopfloor';
    private readonly shift = '/shift';
    private readonly skill = '/skillmatrix';
    private readonly machineTransaction = '/machine-transaction';
  
    constructor(private http: HttpClient) { }
  
    // Machine-related methods
    getMachines(): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.machine}`);
    }
    
    getMachine(id: string): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.machine}/${id}`);
    }
  
    // Shopfloor-related methods
    getShopfloors(): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.shopfloor}`);
    }
    
    getShopfloor(id: string): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.shopfloor}/${id}`);
    }

    getShifts(): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.shift}`);
    }
    
    getShift(id: string): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.shift}/${id}`);
    }
    getSkillMatrixs(): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.skill}`);
    }
    
    getSkillMatrix(id: string): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.skill}/${id}`);
    }

    getMachineTransactions(): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.machineTransaction}`);
    }
    
    getMachineTransaction(id: string): Observable<any> {
      return this.http.get(`${this.baseUrl}${this.machineTransaction}/${id}`);
    }

    createMachineTransaction(transactionData: any): Observable<any> {
      return this.http.post(`${this.baseUrl}${this.machineTransaction}/`, transactionData);
    }
    
    updateMachineTransaction(id: string, transactionData: any): Observable<any> {
      return this.http.put(`${this.baseUrl}${this.machineTransaction}/${id}`, transactionData);
    }
    
    // Optional: DELETE method
    deleteMachineTransaction(id: string): Observable<any> {
      return this.http.delete(`${this.baseUrl}${this.machineTransaction}/${id}`);
    }
}