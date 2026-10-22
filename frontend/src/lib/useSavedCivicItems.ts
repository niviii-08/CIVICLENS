'use client';

import { useState, useEffect, useCallback } from 'react';

export interface SavedCivicRecord {
  record_type: 'promise' | 'scheme' | 'representative' | 'claim' | 'civic';
  record_id: string;
  title: string;
  detail_url: string;
  last_known_status: string;
  saved_at: string;
}

export interface TrackingUpdateEvent {
  change_type: string;
  change_date: string;
  change_source: string;
  change_description: string;
  previous_status?: string;
  new_status?: string;
}

export interface TrackedItemStatus {
  record_type: string;
  record_id: string;
  is_valid: boolean;
  has_update: boolean;
  update_event?: TrackingUpdateEvent | null;
  current_record?: {
    title: string;
    current_status: string;
    detail_url: string;
    last_updated_at?: string;
    error_message?: string;
  };
}

const STORAGE_KEY = 'civiclens_saved_records';
const PREFS_KEY = 'civiclens_tracking_preferences';

export function useSavedCivicItems() {
  const [savedItems, setSavedItems] = useState<SavedCivicRecord[]>([]);
  const [liveStatuses, setLiveStatuses] = useState<Record<string, TrackedItemStatus>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [highlightUpdates, setHighlightUpdates] = useState<boolean>(true);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setSavedItems(parsed);
        }
      }

      const storedPrefs = localStorage.getItem(PREFS_KEY);
      if (storedPrefs) {
        const parsedPrefs = JSON.parse(storedPrefs);
        if (typeof parsedPrefs.highlightUpdates === 'boolean') {
          setHighlightUpdates(parsedPrefs.highlightUpdates);
        }
      }
    } catch (err) {
      console.error('Failed to load saved civic records from local storage:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Sync to localStorage whenever savedItems change
  const persistItems = useCallback((items: SavedCivicRecord[]) => {
    setSavedItems(items);
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
      } catch (err) {
        console.error('Failed to persist saved civic records:', err);
      }
    }
  }, []);

  // Save/Track a record (preventing duplicates)
  const saveRecord = useCallback(
    (record: {
      record_type: 'promise' | 'scheme' | 'representative' | 'claim' | 'civic';
      record_id: string;
      title: string;
      detail_url: string;
      current_status?: string;
    }) => {
      const existing = savedItems.find(
        (item) => item.record_type === record.record_type && item.record_id === record.record_id
      );

      if (existing) {
        return; // Prevent duplicate saves
      }

      const newItem: SavedCivicRecord = {
        record_type: record.record_type,
        record_id: record.record_id,
        title: record.title,
        detail_url: record.detail_url,
        last_known_status: record.current_status || 'TRACKED',
        saved_at: new Date().toISOString(),
      };

      const updated = [newItem, ...savedItems];
      persistItems(updated);
    },
    [savedItems, persistItems]
  );

  // Remove/Untrack a record
  const removeRecord = useCallback(
    (record_type: string, record_id: string) => {
      const filtered = savedItems.filter(
        (item) => !(item.record_type === record_type && item.record_id === record_id)
      );
      persistItems(filtered);

      // Clean up liveStatuses map
      const key = `${record_type}:${record_id}`;
      setLiveStatuses((prev) => {
        const copy = { ...prev };
        delete copy[key];
        return copy;
      });
    },
    [savedItems, persistItems]
  );

  // Check if a specific record is saved
  const isSaved = useCallback(
    (record_type: string, record_id: string): boolean => {
      return savedItems.some(
        (item) => item.record_type === record_type && item.record_id === record_id
      );
    },
    [savedItems]
  );

  // Clear all saved items
  const clearAll = useCallback(() => {
    persistItems([]);
    setLiveStatuses({});
  }, [persistItems]);

  // Toggle update highlighting preference
  const toggleHighlightUpdates = useCallback(() => {
    setHighlightUpdates((prev) => {
      const next = !prev;
      if (typeof window !== 'undefined') {
        localStorage.setItem(PREFS_KEY, JSON.stringify({ highlightUpdates: next }));
      }
      return next;
    });
  }, []);

  // Check live status & updates from backend
  const checkUpdates = useCallback(async () => {
    if (savedItems.length === 0) return;

    try {
      const res = await fetch('/api/tracking/check-updates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: savedItems.map((item) => ({
            record_type: item.record_type,
            record_id: item.record_id,
            last_known_status: item.last_known_status,
            saved_at: item.saved_at,
          })),
        }),
      });

      if (res.ok) {
        const json = await res.json();
        const results: TrackedItemStatus[] = json.data?.results || [];
        const statusMap: Record<string, TrackedItemStatus> = {};
        results.forEach((r) => {
          statusMap[`${r.record_type}:${r.record_id}`] = r;
        });
        setLiveStatuses(statusMap);
      }
    } catch (err) {
      console.warn('Live tracking update check encountered network issue:', err);
    }
  }, [savedItems]);

  // Automatically check updates once savedItems are loaded
  useEffect(() => {
    if (savedItems.length > 0) {
      checkUpdates();
    }
  }, [savedItems.length]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    savedItems,
    liveStatuses,
    loading,
    highlightUpdates,
    saveRecord,
    removeRecord,
    isSaved,
    clearAll,
    toggleHighlightUpdates,
    refreshUpdates: checkUpdates,
  };
}
