import type { PageServerLoad } from './$types';
import { loadDashboard, parseDashboardFilters } from '$lib/api';

export const load: PageServerLoad = async ({ fetch, url }) => {
  const filters = parseDashboardFilters(url);
  const dashboard = await loadDashboard(fetch, filters, (process.env.PUBLIC_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, ''));

  return {
    filters,
    dashboard
  };
};
