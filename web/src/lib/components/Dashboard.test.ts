import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';

import Dashboard from './Dashboard.svelte';
import type { DashboardData, DashboardFilters } from '$lib/types';

const filters: DashboardFilters = {
  start_time: '',
  end_time: '',
  criticality: '',
  tag: '',
  page: 1,
  page_size: 20
};

const emptyDashboard: DashboardData = {
  alarms: {
    items: [],
    total: 0,
    page: 1,
    page_size: 20,
    pages: 0
  },
  topTags: {
    items: [],
    total_tags: 0
  },
  summary: {
    total_alarms: 0,
    by_criticality: {},
    by_state: {},
    latest_event_time: null
  },
  error: null
};

const dataDashboard: DashboardData = {
  alarms: {
    items: [
      {
        id: 1,
        external_alarm_id: 'ALM-001',
        source_system: 'SCADA',
        tag: 'TAG_A',
        message: 'Pressure high',
        priority: 1,
        criticality: 'HIGH',
        state: 'ACTIVE',
        plant: 'PLANT_A',
        area: 'AREA_1',
        equipment: 'EQ-1',
        event_time: '2024-01-01T10:00:00Z',
        ack_time: null,
        clear_time: null,
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-01T10:00:00Z'
      }
    ],
    total: 1,
    page: 1,
    page_size: 20,
    pages: 1
  },
  topTags: {
    items: [{ tag: 'TAG_A', alarm_count: 1 }],
    total_tags: 1
  },
  summary: {
    total_alarms: 1,
    by_criticality: { HIGH: 1 },
    by_state: { ACTIVE: 1 },
    latest_event_time: '2024-01-01T10:00:00Z'
  },
  error: null
};

describe('Dashboard component', () => {
  it('renders loading state', () => {
    render(Dashboard, { props: { filters, dashboard: emptyDashboard, loading: true } });
    expect(screen.queryByText('Top tags')).not.toBeInTheDocument();
    expect(screen.queryByText('Alarm list')).not.toBeInTheDocument();
  });

  it('renders error state', () => {
    render(Dashboard, {
      props: {
        filters,
        dashboard: { ...emptyDashboard, error: 'backend unavailable' }
      }
    });
    expect(screen.getByText('Unable to load dashboard')).toBeInTheDocument();
    expect(screen.getByText('backend unavailable')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(Dashboard, { props: { filters, dashboard: emptyDashboard } });
    expect(screen.getByText('No alarms matched the current filters.')).toBeInTheDocument();
  });

  it('renders data state', () => {
    render(Dashboard, { props: { filters, dashboard: dataDashboard } });
    expect(screen.getByRole('heading', { name: 'Alarm dashboard' })).toBeInTheDocument();
    expect(screen.getAllByText('TAG_A')).toHaveLength(2);
    expect(screen.getByText('Pressure high')).toBeInTheDocument();
    expect(screen.getByText('Total alarms')).toBeInTheDocument();
    expect(screen.getByText('Top tags')).toBeInTheDocument();
  });
});
