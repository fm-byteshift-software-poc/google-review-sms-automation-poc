import api from "@/lib/api";
import type { Item, ItemCreate, ItemUpdate } from "@/types/item";

export const itemService = {
  getAll: async (): Promise<Item[]> => {
    const { data } = await api.get<Item[]>("/items");
    return data;
  },

  getById: async (id: string): Promise<Item> => {
    const { data } = await api.get<Item>(`/items/${id}`);
    return data;
  },

  create: async (payload: ItemCreate): Promise<Item> => {
    const { data } = await api.post<Item>("/items", payload);
    return data;
  },

  update: async (id: string, payload: ItemUpdate): Promise<Item> => {
    const { data } = await api.patch<Item>(`/items/${id}`, payload);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/items/${id}`);
  },
};
