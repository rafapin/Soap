import { describe, expect, it } from 'vitest';

import {
  buildFiltersQuery,
  buildPageUrl,
  parseDashboardFilters
} from './api';
import type { DashboardFilters } from '$lib/types';

describe('dashboard api helpers', () => {
  const filters: DashboardFilters = {
    start_time: '2024-01-01',
    end_time: '2024-01-02',
    criticality: 'HIGH',
    tag: 'TAG_A',
    page: 2,
    page_size: 50
  };

  it('builds api filter query parameters', () => {
    expect(buildFiltersQuery(filters)).toBe(
      'start_time=2024-01-01T00%3A00%3A00&end_time=2024-01-02T23%3A59%3A59&criticality=HIGH&tag=TAG_A&page=2&page_size=50'
    );
  });

  it('builds page urls while preserving filters', () => {
    expect(buildPageUrl(filters, 5)).toBe(
      '?start_time=2024-01-01T00%3A00%3A00&end_time=2024-01-02T23%3A59%3A59&criticality=HIGH&tag=TAG_A&page=5&page_size=50'
    );
  });

  it('parses query strings into dashboard filters', () => {
    const url = new URL(
      'http://localhost:3000/?start_time=2024-01-01T09%3A00%3A00&end_time=2024-01-02&criticality=medium&tag=TAG_B&page=3&page_size=999'
    );

    expect(parseDashboardFilters(url)).toEqual({
      start_time: '2024-01-01T09:00:00',
      end_time: '2024-01-02',
      criticality: 'MEDIUM',
      tag: 'TAG_B',
      page: 3,
      page_size: 100
    });
  });
});
