<script lang="ts">
  import Dashboard from '$lib/components/Dashboard.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<svelte:head>
  <title>SCADA Alarm Gateway</title>
  <meta
    name="description"
    content="Dashboard for paginated SCADA alarms, aggregated metrics and top tags."
  />
</svelte:head>

<Dashboard
  filters={data.filters}
  dashboard={data.dashboard}
/>
