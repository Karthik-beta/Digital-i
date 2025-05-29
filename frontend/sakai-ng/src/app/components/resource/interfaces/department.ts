export interface Shift {
  name: string;
  planned: number;
  checkIn: number;
}

export interface Department {
  name: string;
  active: number;
  present: number;
  absent: number;
  shifts: Shift[];
}
