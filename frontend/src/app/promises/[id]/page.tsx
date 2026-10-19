'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { DetailedCivicRecord } from '../../../lib/types';
import { fetchPromiseDetail } from '../../../lib/api';
import { RecordDetailLayout } from '../../../components/RecordDetailLayout';

export default function PromiseDetailPage() {
  const params = useParams();
  const id = typeof params?.id === 'string' ? params.id : Array.isArray(params?.id) ? params.id[0] : '';
  const [record, setRecord] = useState<DetailedCivicRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPromiseDetail(id);
      setRecord(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to retrieve election promise details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  return (
    <RecordDetailLayout
      record={record}
      loading={loading}
      error={error}
      onRetry={loadData}
      parentRoute="/promises"
      parentLabel="Promises & Progress"
    />
  );
}
