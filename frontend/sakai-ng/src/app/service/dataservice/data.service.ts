import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  constructor() { }

  private _id: number = 0;

  get id(): number {
    return this._id;
  }

  set id(value: number) {
    this._id = value;
  }

}
