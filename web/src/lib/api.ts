import type {
  Alarm,
  ChartFilters,
  ChartsData,
  ChartsMetricsResponse,
  DashboardData,
  DashboardFilters,
  MetricsSummary,
  PaginatedResponse,
  TopTagsResponse
} from '$lib/types';

export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100] as const;
export const DEFAULT_PAGE_SIZE = 20;
export const TOP_TAGS_LIMIT = 8;

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

export function normalizeText(value: string | null | undefined) {
  return (value ?? '').trim();
}

export function formatDateTimeForApi(value: string, kind: 'start' | 'end') {
  if (!value) return '';
  if (value.length === 10) {
    return `${value}T${kind === 'start' ? '00:00:00' : '23:59:59'}`;
  }
  return value;
}

export function displayDateValue(value: string) {
  return value ? value.slice(0, 10) : '';
}

export function parseDashboardFilters(url: URL): DashboardFilters {
  const page = Number.parseInt(url.searchParams.get('page') ?? '', 10);
  const pageSize = Number.parseInt(url.searchParams.get('page_size') ?? '', 10);
  return {
    start_time: normalizeText(url.searchParams.get('start_time')),
    end_time: normalizeText(url.searchParams.get('end_time')),
    criticality: normalizeText(url.searchParams.get('criticality')).toUpperCase(),
    tag: normalizeText(url.searchParams.get('tag')),
    page: Number.isFinite(page) && page > 0 ? page : 1,
    page_size: Number.isFinite(pageSize) && pageSize > 0 ? Math.min(pageSize, 100) : DEFAULT_PAGE_SIZE
  };
}

export function parseChartFilters(url: URL): ChartFilters {
  const limit = Number.parseInt(url.searchParams.get('limit') ?? '', 10);
  const rawBucket = normalizeText(url.searchParams.get('bucket')).toLowerCase();
  const bucket = rawBucket === 'hour' ? 'hour' : 'day';

  return {
    start_time: normalizeText(url.searchParams.get('start_time')),
    end_time: normalizeText(url.searchParams.get('end_time')),
    criticality: normalizeText(url.searchParams.get('criticality')).toUpperCase(),
    tag: normalizeText(url.searchParams.get('tag')),
    bucket,
    limit: Number.isFinite(limit) && limit > 0 ? Math.min(limit, 50) : 10
  };
}

export function buildFiltersQuery(filters: DashboardFilters, pageOverride?: number) {
  const params = new URLSearchParams();
  const page = pageOverride ?? filters.page;

  if (filters.start_time) {
    params.set('start_time', formatDateTimeForApi(filters.start_time, 'start'));
  }
  if (filters.end_time) {
    params.set('end_time', formatDateTimeForApi(filters.end_time, 'end'));
  }
  if (filters.criticality) {
    params.set('criticality', filters.criticality);
  }
  if (filters.tag) {
    params.set('tag', filters.tag);
  }

  params.set('page', String(page));
  params.set('page_size', String(filters.page_size));
  return params.toString();
}

export function buildPageUrl(filters: DashboardFilters, page: number) {
  const query = buildFiltersQuery(filters, page);
  return query ? `?${query}` : '?';
}

export function buildChartsQuery(filters: ChartFilters) {
  const params = new URLSearchParams();

  if (filters.start_time) {
    params.set('start_time', formatDateTimeForApi(filters.start_time, 'start'));
  }
  if (filters.end_time) {
    params.set('end_time', formatDateTimeForApi(filters.end_time, 'end'));
  }
  if (filters.criticality) {
    params.set('criticality', filters.criticality);
  }
  if (filters.tag) {
    params.set('tag', filters.tag);
  }

  params.set('bucket', filters.bucket);
  params.set('limit', String(filters.limit));
  return params.toString();
}

function parseApiError(payload: unknown, fallback: string) {
  if (payload && typeof payload === 'object' && 'message' in payload && typeof payload.message === 'string') {
    return payload.message;
  }
  return fallback;
}

async function readJson<T>(response: Response): Promise<T> {
  return (await response.json()) as T;
}

async function getJson<T>(fetcher: typeof fetch, baseUrl: string, path: string, query: string): Promise<T> {
  const url = `${baseUrl.replace(/\/$/, '')}${path}${query ? `?${query}` : ''}`;
  const response = await fetcher(url);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(parseApiError(payload, `Request failed with status ${response.status}`));
  }
  return readJson<T>(response);
}

export async function loadDashboard(
  fetcher: typeof fetch,
  filters: DashboardFilters,
  baseUrl = DEFAULT_API_BASE_URL
): Promise<DashboardData> {
  const alarmsQuery = buildFiltersQuery(filters);
  const sharedQuery = new URLSearchParams();

  if (filters.start_time) {
    sharedQuery.set('start_time', formatDateTimeForApi(filters.start_time, 'start'));
  }
  if (filters.end_time) {
    sharedQuery.set('end_time', formatDateTimeForApi(filters.end_time, 'end'));
  }
  if (filters.tag) {
    sharedQuery.set('tag', filters.tag);
  }

  try {
    const [alarms, topTags, summary] = await Promise.all([
      getJson<PaginatedResponse<Alarm>>(fetcher, baseUrl, '/api/v1/alarms', alarmsQuery),
      getJson<TopTagsResponse>(
        fetcher,
        baseUrl,
        '/api/v1/metrics/top-tags',
        `${sharedQuery.toString()}${sharedQuery.size ? '&' : ''}limit=${TOP_TAGS_LIMIT}`
      ),
      getJson<MetricsSummary>(fetcher, baseUrl, '/api/v1/metrics/summary', sharedQuery.toString())
    ]);

    return {
      alarms,
      topTags,
      summary,
      error: null
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to load dashboard data';
    return {
      alarms: null,
      topTags: null,
      summary: null,
      error: message
    };
  }
}

export async function loadCharts(
  fetcher: typeof fetch,
  filters: ChartFilters,
  baseUrl = DEFAULT_API_BASE_URL
): Promise<ChartsData> {
  try {
    const charts = await getJson<ChartsMetricsResponse>(
      fetcher,
      baseUrl,
      '/api/v1/metrics/charts',
      buildChartsQuery(filters)
    );

    return {
      charts,
      error: null
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to load chart metrics';
    return {
      charts: null,
      error: message
    };
  }
}
