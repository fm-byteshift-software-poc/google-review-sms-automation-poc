export interface Item {
  id: string;
  name: string;
  description?: string;
  price: number;
  created_at: string;
  updated_at: string;
}

export interface ItemCreate {
  name: string;
  description?: string;
  price: number;
}

export interface ItemUpdate {
  name?: string;
  description?: string;
  price?: number;
}
