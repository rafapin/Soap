<script lang="ts">
  import DashboardCharts from '$lib/components/DashboardCharts.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<svelte:head>
  <title>SCADA Alarm Gateway | Dashboard</title>
  <meta
    name="description"
    content="Industrial chart dashboard for aggregated SCADA alarm metrics."
  />
</svelte:head>

<DashboardCharts filters={data.filters} data={data.charts} />
