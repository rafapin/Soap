<script lang="ts">
  import { displayDateValue } from '$lib/api';
  import type { ChartFilters, ChartMetricItem, ChartsData, TimelineMetricItem } from '$lib/types';
  import Alert from '$lib/components/ui/alert/alert.svelte';
  import Button from '$lib/components/ui/button/button.svelte';
  import EChart from '$lib/components/charts/EChart.svelte';
  import type { EChartsOption } from 'echarts';

  type Props = {
    filters: ChartFilters;
    data: ChartsData;
  };

  let { filters, data }: Props = $props();

  const palette = {
    cyan: '#67e8f9',
    blue: '#38bdf8',
    red: '#fb385d',
    amber: '#f59e0b',
    yellow: '#fbbf24',
    green: '#22c55e',
    teal: '#2dd4bf',
    slate: '#94a3b8',
    violet: '#a78bfa'
  };

  const chartGrid = {
    left: 48,
    right: 24,
    top: 36,
    bottom: 42
  };

  function countLabel(value: number) {
    return new Intl.NumberFormat('en-US').format(value);
  }

  function valueColor(value: string) {
    switch (value.toUpperCase()) {
      case 'HIGH':
        return palette.red;
      case 'MEDIUM':
        return palette.amber;
      case 'LOW':
        return palette.green;
      case 'ACTIVE':
        return palette.green;
      case 'ACKNOWLEDGED':
        return palette.blue;
      case 'SHELVED':
        return palette.yellow;
      case 'CLEARED':
        return palette.teal;
      case 'UNKNOWN':
        return palette.slate;
      default:
        return palette.cyan;
    }
  }

  function axisStyle() {
    return {
      axisLine: { lineStyle: { color: 'rgba(103, 232, 249, 0.28)' } },
      axisTick: { lineStyle: { color: 'rgba(103, 232, 249, 0.2)' } },
      axisLabel: { color: '#aab7c4', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(103, 232, 249, 0.08)' } }
    };
  }

  function tooltip() {
    return {
      backgroundColor: 'rgba(7, 13, 19, 0.96)',
      borderColor: 'rgba(103, 232, 249, 0.55)',
      borderWidth: 1,
      textStyle: { color: '#f3f8fb' }
    };
  }

  function timelineOption(items: TimelineMetricItem[]): EChartsOption {
    const periods = items.map((item) => item.period);
    const counts = items.map((item) => item.alarm_count);

    return {
      color: [palette.cyan, palette.blue],
      tooltip: { trigger: 'axis', ...tooltip() },
      grid: chartGrid,
      xAxis: { type: 'category', data: periods, ...axisStyle() },
      yAxis: { type: 'value', ...axisStyle() },
      series: [
        {
          name: 'Volume',
          type: 'bar',
          data: counts,
          barMaxWidth: 18,
          itemStyle: {
            color: 'rgba(56, 189, 248, 0.55)',
            borderColor: 'rgba(103, 232, 249, 0.85)',
            borderWidth: 1
          }
        },
        {
          name: 'Trend',
          type: 'line',
          data: counts,
          smooth: true,
          symbolSize: 7,
          lineStyle: { color: palette.cyan, width: 2 },
          itemStyle: { color: palette.cyan }
        }
      ]
    };
  }

  function donutOption(items: ChartMetricItem[], title: string): EChartsOption {
    return {
      color: items.map((item) => valueColor(item.value)),
      title: {
        text: title,
        left: 'center',
        top: 6,
        textStyle: { color: '#d8f8ff', fontSize: 12 }
      },
      tooltip: { trigger: 'item', ...tooltip() },
      legend: {
        bottom: 0,
        textStyle: { color: '#aab7c4', fontSize: 11 }
      },
      series: [
        {
          name: title,
          type: 'pie',
          radius: ['52%', '76%'],
          center: ['50%', '48%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderColor: '#071017',
            borderWidth: 2
          },
          label: {
            color: '#d8f8ff',
            formatter: '{b}: {c}'
          },
          data: items.map((item) => ({ name: item.value, value: item.alarm_count }))
        }
      ]
    };
  }

  function horizontalBarOption(items: ChartMetricItem[], name: string): EChartsOption {
    const ordered = [...items].sort((left, right) => left.alarm_count - right.alarm_count);

    return {
      color: [palette.cyan],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, ...tooltip() },
      grid: { left: 110, right: 24, top: 24, bottom: 28 },
      xAxis: { type: 'value', ...axisStyle() },
      yAxis: {
        type: 'category',
        data: ordered.map((item) => item.value),
        ...axisStyle()
      },
      series: [
        {
          name,
          type: 'bar',
          data: ordered.map((item) => ({
            value: item.alarm_count,
            itemStyle: { color: valueColor(item.value) }
          })),
          barMaxWidth: 18,
          label: {
            show: true,
            position: 'right',
            color: '#d8f8ff',
            formatter: ({ value }) => countLabel(Number(value))
          }
        }
      ]
    };
  }

  function treemapOption(plants: ChartMetricItem[], areas: ChartMetricItem[]): EChartsOption {
    return {
      tooltip: { ...tooltip() },
      series: [
        {
          name: 'Hotspots',
          type: 'treemap',
          roam: false,
          nodeClick: false,
          breadcrumb: { show: false },
          label: { color: '#f3f8fb', fontSize: 12 },
          upperLabel: { show: true, color: '#d8f8ff' },
          itemStyle: {
            borderColor: 'rgba(103, 232, 249, 0.42)',
            borderWidth: 1,
            gapWidth: 4
          },
          levels: [
            {
              itemStyle: {
                borderColor: 'rgba(103, 232, 249, 0.42)',
                borderWidth: 1,
                gapWidth: 4
              }
            }
          ],
          data: [
            {
              name: 'Plants',
              itemStyle: { color: 'rgba(56, 189, 248, 0.52)' },
              children: plants.map((item) => ({ name: item.value, value: item.alarm_count }))
            },
            {
              name: 'Areas',
              itemStyle: { color: 'rgba(45, 212, 191, 0.5)' },
              children: areas.map((item) => ({ name: item.value, value: item.alarm_count }))
            }
          ]
        }
      ]
    };
  }

  function priorityOption(items: ChartMetricItem[]): EChartsOption {
    const ordered = [...items].sort((left, right) => Number(left.value) - Number(right.value));

    return {
      color: [palette.violet],
      tooltip: { trigger: 'axis', ...tooltip() },
      grid: chartGrid,
      xAxis: { type: 'category', data: ordered.map((item) => item.value), ...axisStyle() },
      yAxis: { type: 'value', ...axisStyle() },
      series: [
        {
          name: 'Priority',
          type: 'bar',
          data: ordered.map((item) => item.alarm_count),
          barMaxWidth: 28,
          itemStyle: {
            color: 'rgba(167, 139, 250, 0.65)',
            borderColor: 'rgba(216, 180, 254, 0.82)',
            borderWidth: 1
          }
        }
      ]
    };
  }

</script>

<div class="industrial-shell min-h-screen px-4 py-6 sm:px-6 lg:px-8">
  <div class="mx-auto flex w-full max-w-7xl flex-col gap-6">
    <header class="flex flex-col gap-4 border-b border-cyan-300/15 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div class="space-y-2">
        <div class="tech-label text-[11px] font-semibold text-cyan-200/85">SCADA ALARM GATEWAY</div>
        <h1 class="text-3xl font-semibold tracking-tight text-[var(--text-primary)] sm:text-4xl">
          Operational dashboard
        </h1>
        <p class="max-w-3xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
          Aggregated alarm intelligence rendered from server-side domain metrics. No paginated record sampling.
        </p>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row lg:items-center">
        <Button href="/" variant="outline" size="md" class="w-full justify-center lg:w-auto">Alarm List</Button>
        <Button
          href="http://localhost:8000/docs"
          variant="outline"
          size="md"
          class="w-full justify-center lg:w-auto"
          target="_blank"
          rel="noreferrer"
        >
          Open Swagger
        </Button>
      </div>
    </header>

    <section class="industrial-panel industrial-panel--overflow-visible rounded-[10px] px-4 py-4 sm:px-5">
      <form method="GET" class="relative z-[1] grid gap-4 xl:grid-cols-[1fr_auto] xl:items-end">
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <label class="space-y-2">
            <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Start date</span>
            <input class="tech-input h-11 w-full rounded-[6px] px-3 text-sm" type="date" name="start_time" value={displayDateValue(filters.start_time)} />
          </label>

          <label class="space-y-2">
            <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">End date</span>
            <input class="tech-input h-11 w-full rounded-[6px] px-3 text-sm" type="date" name="end_time" value={displayDateValue(filters.end_time)} />
          </label>

          <label class="space-y-2">
            <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Criticality</span>
            <select class="tech-select h-11 w-full rounded-[6px] px-3 text-sm" name="criticality" value={filters.criticality}>
              <option value="">All</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </label>

          <label class="space-y-2">
            <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Tag</span>
            <input class="tech-input h-11 w-full rounded-[6px] px-3 text-sm" type="text" name="tag" value={filters.tag} placeholder="TAG_A0001" />
          </label>

          <label class="space-y-2">
            <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Bucket</span>
            <select class="tech-select h-11 w-full rounded-[6px] px-3 text-sm" name="bucket" value={filters.bucket}>
              <option value="day">Day</option>
              <option value="hour">Hour</option>
            </select>
          </label>

          <label class="space-y-2">
            <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Limit</span>
            <input class="tech-input h-11 w-full rounded-[6px] px-3 text-sm" type="number" name="limit" min="1" max="50" value={filters.limit} />
          </label>
        </div>

        <div class="flex gap-2">
          <Button type="submit" class="h-11 flex-1 xl:flex-none">Apply filters</Button>
          <Button href="/dashboard" variant="ghost" class="h-11 flex-1 xl:flex-none">Reset</Button>
        </div>
      </form>
    </section>

    {#if data.error}
      <Alert variant="destructive" title="Unable to load chart metrics" description={data.error} />
    {:else if data.charts}
      <section class="grid gap-4 lg:grid-cols-12">
        <article class="industrial-panel panel-grid-line rounded-[10px] p-4 lg:col-span-12">
          <div class="relative z-[1] mb-3">
            <h2 class="tech-label text-sm font-semibold text-cyan-100">Alarm Volume Timeline</h2>
            <p class="mt-1 text-xs text-[var(--text-secondary)]">{filters.bucket.toUpperCase()} BUCKET</p>
          </div>
          <EChart option={timelineOption(data.charts.timeline)} ariaLabel="Alarm volume timeline chart" class="relative z-[1] h-80" />
        </article>

        <article class="industrial-panel rounded-[10px] p-4 lg:col-span-4">
          <EChart option={donutOption(data.charts.by_criticality, 'CRITICALITY')} ariaLabel="Criticality distribution chart" class="relative z-[1]" />
        </article>

        <article class="industrial-panel rounded-[10px] p-4 lg:col-span-4">
          <EChart option={horizontalBarOption(data.charts.by_state, 'State')} ariaLabel="State distribution chart" class="relative z-[1]" />
        </article>

        <article class="industrial-panel rounded-[10px] p-4 lg:col-span-4">
          <EChart option={donutOption(data.charts.by_source_system, 'SOURCE SYSTEM')} ariaLabel="Source system mix chart" class="relative z-[1]" />
        </article>

        <article class="industrial-panel rounded-[10px] p-4 lg:col-span-6">
          <div class="relative z-[1] mb-3">
            <h2 class="tech-label text-sm font-semibold text-cyan-100">Top Alarm Tags</h2>
            <p class="mt-1 text-xs text-[var(--text-secondary)]">Most frequent alarm points</p>
          </div>
          <EChart option={horizontalBarOption(data.charts.top_tags, 'Tags')} ariaLabel="Top alarm tags chart" class="relative z-[1] h-96" />
        </article>

        <article class="industrial-panel rounded-[10px] p-4 lg:col-span-6">
          <div class="relative z-[1] mb-3">
            <h2 class="tech-label text-sm font-semibold text-cyan-100">Plant / Area Hotspots</h2>
            <p class="mt-1 text-xs text-[var(--text-secondary)]">Spatial concentration by domain fields</p>
          </div>
          <EChart option={treemapOption(data.charts.by_plant, data.charts.by_area)} ariaLabel="Plant and area hotspots treemap" class="relative z-[1] h-96" />
        </article>

        <article class="industrial-panel rounded-[10px] p-4 lg:col-span-12">
          <div class="relative z-[1] mb-3 flex items-center justify-between gap-3">
            <div>
              <h2 class="tech-label text-sm font-semibold text-cyan-100">Priority Profile</h2>
              <p class="mt-1 text-xs text-[var(--text-secondary)]">Alarm load by normalized priority value</p>
            </div>
            <div class="text-right text-xs text-[var(--text-secondary)]">
              Total buckets: {data.charts.by_priority.length}
            </div>
          </div>
          <EChart option={priorityOption(data.charts.by_priority)} ariaLabel="Priority profile chart" class="relative z-[1] h-72" />
        </article>
      </section>
    {/if}
  </div>
</div>
