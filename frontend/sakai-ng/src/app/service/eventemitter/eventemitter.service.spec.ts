import { TestBed } from '@angular/core/testing';

import { EventemitterService } from './eventemitter.service';

describe('EventemitterService', () => {
  let service: EventemitterService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EventemitterService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
