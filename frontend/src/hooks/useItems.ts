import { useState, useEffect, useCallback } from "react";
import { itemService } from "@/services/itemService";
import type { Item, ItemCreate, ItemUpdate } from "@/types/item";

interface UseItemsReturn {
  items: Item[];
  loading: boolean;
  error: string | null;
  createItem: (payload: ItemCreate) => Promise<void>;
  updateItem: (id: string, payload: ItemUpdate) => Promise<void>;
  deleteItem: (id: string) => Promise<void>;
  refetch: () => Promise<void>;
}

export function useItems(): UseItemsReturn {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await itemService.getAll();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch items");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const createItem = async (payload: ItemCreate) => {
    const newItem = await itemService.create(payload);
    setItems((prev) => [...prev, newItem]);
  };

  const updateItem = async (id: string, payload: ItemUpdate) => {
    const updated = await itemService.update(id, payload);
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
  };

  const deleteItem = async (id: string) => {
    await itemService.delete(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  return {
    items,
    loading,
    error,
    createItem,
    updateItem,
    deleteItem,
    refetch: fetchItems,
  };
}
