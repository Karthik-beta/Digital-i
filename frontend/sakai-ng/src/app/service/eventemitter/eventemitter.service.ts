import { Injectable, EventEmitter } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class EventemitterService {

  constructor() { }

  invokeGetUpdatedAtList = new EventEmitter();
}
