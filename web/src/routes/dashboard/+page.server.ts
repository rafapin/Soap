import type { PageServerLoad } from './$types';
import { loadCharts, parseChartFilters } from '$lib/api';

export const load: PageServerLoad = async ({ fetch, url }) => {
  const filters = parseChartFilters(url);
  const charts = await loadCharts(
    fetch,
    filters,
    (process.env.PUBLIC_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '')
  );

  return {
    filters,
    charts
  };
};
