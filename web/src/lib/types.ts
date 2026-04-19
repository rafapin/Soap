export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Alarm {
  id: number;
  external_alarm_id: string | null;
  source_system: string | null;
  tag: string;
  message: string | null;
  priority: number | null;
  criticality: string;
  state: string | null;
  plant: string | null;
  area: string | null;
  equipment: string | null;
  event_time: string;
  ack_time: string | null;
  clear_time: string | null;
  created_at: string;
  updated_at: string;
}

export interface TopTagItem {
  tag: string;
  alarm_count: number;
}

export interface TopTagsResponse {
  items: TopTagItem[];
  total_tags: number;
}

export interface MetricsSummary {
  total_alarms: number;
  by_criticality: Record<string, number>;
  by_state: Record<string, number>;
  latest_event_time: string | null;
}

export interface TimelineMetricItem {
  period: string;
  alarm_count: number;
}

export interface ChartMetricItem {
  value: string;
  alarm_count: number;
}

export interface ChartsMetricsResponse {
  timeline: TimelineMetricItem[];
  by_criticality: ChartMetricItem[];
  by_state: ChartMetricItem[];
  top_tags: ChartMetricItem[];
  by_plant: ChartMetricItem[];
  by_area: ChartMetricItem[];
  by_priority: ChartMetricItem[];
  by_source_system: ChartMetricItem[];
}

export interface DashboardFilters {
  start_time: string;
  end_time: string;
  criticality: string;
  tag: string;
  page: number;
  page_size: number;
}

export interface DashboardData {
  alarms: PaginatedResponse<Alarm> | null;
  topTags: TopTagsResponse | null;
  summary: MetricsSummary | null;
  error: string | null;
}

export interface ChartFilters {
  start_time: string;
  end_time: string;
  criticality: string;
  tag: string;
  bucket: 'day' | 'hour';
  limit: number;
}

export interface ChartsData {
  charts: ChartsMetricsResponse | null;
  error: string | null;
}
