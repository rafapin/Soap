<script lang="ts">
  import { buildPageUrl, displayDateValue } from '$lib/api';
  import type { Alarm, DashboardData, DashboardFilters } from '$lib/types';
  import Alert from '$lib/components/ui/alert/alert.svelte';
  import Badge from '$lib/components/ui/badge/badge.svelte';
  import Button from '$lib/components/ui/button/button.svelte';
  import DatePicker from '$lib/components/ui/date-picker/date-picker.svelte';
  import Pagination from '$lib/components/ui/pagination/pagination.svelte';
  import Select, { type SelectOption } from '$lib/components/ui/select/select.svelte';
  import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';

  type Props = {
    filters: DashboardFilters;
    dashboard: DashboardData;
    loading?: boolean;
  };

  type BadgeTone = 'default' | 'success' | 'warning' | 'destructive' | 'muted';

  type BadgeMeta = {
    label: string;
    tone: BadgeTone;
    icon: 'warning' | 'caution' | 'check' | 'pulse' | 'sleep' | 'question';
  };

  let { filters, dashboard, loading = false }: Props = $props();

  const pageSizeOptions = [10, 20, 50, 100] as const;
  const criticalitySelectOptions: SelectOption[] = [
    { value: '', label: 'All' },
    { value: 'HIGH', label: 'HIGH' },
    { value: 'MEDIUM', label: 'MEDIUM' },
    { value: 'LOW', label: 'LOW' },
    { value: 'UNKNOWN', label: 'UNKNOWN' }
  ];
  const pageSizeSelectOptions: SelectOption[] = pageSizeOptions.map((option) => ({
    value: String(option),
    label: String(option)
  }));
  const numberFormat = new Intl.NumberFormat('en-US');
  const dateTimeFormat = new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });

  function formatDateTime(value: string | null | undefined) {
    if (!value) {
      return 'No data';
    }

    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }

    return dateTimeFormat.format(parsed);
  }

  function formatCount(value: number | null | undefined) {
    return numberFormat.format(value ?? 0);
  }

  function sortedEntries(record: Record<string, number> | null | undefined) {
    return Object.entries(record ?? {}).sort((left, right) => right[1] - left[1]);
  }

  function criticalityMeta(value: string | null | undefined): BadgeMeta {
    switch ((value ?? 'UNKNOWN').toUpperCase()) {
      case 'HIGH':
        return { label: 'HIGH', tone: 'destructive', icon: 'warning' };
      case 'MEDIUM':
        return { label: 'MEDIUM', tone: 'warning', icon: 'caution' };
      case 'LOW':
        return { label: 'LOW', tone: 'success', icon: 'check' };
      case 'UNKNOWN':
        return { label: 'UNKNOWN', tone: 'muted', icon: 'question' };
      default:
        return {
          label: (value ?? 'UNKNOWN').toUpperCase(),
          tone: 'default',
          icon: 'question'
        };
    }
  }

  function stateMeta(value: string | null | undefined): BadgeMeta {
    switch ((value ?? 'UNKNOWN').toUpperCase()) {
      case 'ACTIVE':
        return { label: 'ACTIVE', tone: 'success', icon: 'pulse' };
      case 'ACKNOWLEDGED':
        return { label: 'ACKNOWLEDGED', tone: 'default', icon: 'check' };
      case 'SHELVED':
        return { label: 'SHELVED', tone: 'warning', icon: 'sleep' };
      case 'CLEARED':
        return { label: 'CLEARED', tone: 'muted', icon: 'check' };
      case 'UNKNOWN':
        return { label: 'UNKNOWN', tone: 'muted', icon: 'question' };
      default:
        return {
          label: (value ?? 'UNKNOWN').toUpperCase(),
          tone: 'default',
          icon: 'question'
        };
    }
  }

  function topTagVariant(rank: number) {
    if (rank === 0) return 'default';
    if (rank === 1) return 'success';
    if (rank === 2) return 'warning';
    return 'muted';
  }

  function displayPriority(alarm: Alarm) {
    return alarm.priority != null ? formatCount(alarm.priority) : '-';
  }

  function summaryByCriticality() {
    return sortedEntries(dashboard.summary?.by_criticality).slice(0, 4);
  }

  function summaryByState() {
    return sortedEntries(dashboard.summary?.by_state).slice(0, 4);
  }
</script>

<div class="industrial-shell px-4 py-6 sm:px-6 lg:px-8">
  <div class="mx-auto flex w-full max-w-7xl flex-col gap-6">
    <header class="flex flex-col gap-4 border-b border-cyan-300/15 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div class="space-y-2">
        <div class="tech-label text-[11px] font-semibold text-cyan-200/85">SCADA ALARM GATEWAY</div>
        <h1 class="text-3xl font-semibold tracking-tight text-[var(--text-primary)] sm:text-4xl">
          Alarm dashboard
        </h1>
        <p class="max-w-2xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
          Industrial alarm monitoring with paginated records, filters and live aggregated metrics.
        </p>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row lg:items-center">
        <Button href="/dashboard" size="md" class="w-full justify-center lg:w-auto">
          <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path d="M4 19V5m4 14v-7m4 7V8m4 11v-4m4 4V3" />
            <path d="M3 19h18" />
          </svg>
          <span>Dashboard</span>
        </Button>

        <Button
          href="http://localhost:8000/docs"
          variant="outline"
          size="md"
          class="w-full justify-center lg:w-auto"
          target="_blank"
          rel="noreferrer"
          aria-label="Open Swagger documentation"
        >
          <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path
              d="M9.18 3.5h5.64l.76 2.16c.35.11.68.27.98.47l2.1-.91 2.82 4.88-1.86 1.53c.03.25.05.51.05.77s-.02.52-.05.77l1.86 1.53-2.82 4.88-2.1-.91c-.3.2-.63.36-.98.47l-.76 2.16H9.18l-.76-2.16a6.2 6.2 0 0 1-.98-.47l-2.1.91-2.82-4.88 1.86-1.53A6 6 0 0 1 4.33 12c0-.26.02-.52.05-.77L2.52 9.7l2.82-4.88 2.1.91c.3-.2.63-.36.98-.47l.76-2.16Z"
            />
            <circle cx="12" cy="12" r="2.75" />
          </svg>
          <span>Open Swagger</span>
        </Button>
      </div>
    </header>

    <section class="industrial-panel industrial-panel--overflow-visible rounded-[10px] px-4 py-4 sm:px-5">
      <form method="GET" class="relative z-[1]">
        <input type="hidden" name="page" value="1" />
        <div class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-end">
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <label class="space-y-2">
              <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Start date</span>
              <DatePicker
                name="start_time"
                value={displayDateValue(filters.start_time)}
                placeholder="dd/mm/aaaa"
                class="w-full"
                buttonClass="h-11"
              />
            </label>

            <label class="space-y-2">
              <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">End date</span>
              <DatePicker
                name="end_time"
                value={displayDateValue(filters.end_time)}
                placeholder="dd/mm/aaaa"
                class="w-full"
                buttonClass="h-11"
              />
            </label>

            <label class="space-y-2">
              <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Criticality</span>
              <Select
                name="criticality"
                value={filters.criticality}
                options={criticalitySelectOptions}
                placeholder="All"
                class="w-full"
                buttonClass="h-11"
                panelClass="w-full"
              />
            </label>

            <label class="space-y-2">
              <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Tag</span>
              <input
                type="text"
                name="tag"
                value={filters.tag}
                placeholder="TAG_A"
                class="tech-input h-11 w-full rounded-[8px] px-3 text-sm uppercase"
              />
            </label>

            <label class="space-y-2">
              <span class="tech-label block text-[10px] font-semibold text-cyan-100/70">Page size</span>
              <Select
                name="page_size"
                value={String(filters.page_size)}
                options={pageSizeSelectOptions}
                placeholder={String(filters.page_size)}
                class="w-full"
                buttonClass="h-11"
                panelClass="w-full"
              />
            </label>
          </div>

          <div class="flex flex-wrap items-center gap-3 xl:justify-end">
            <Button type="submit" variant="default" class="min-w-32 justify-center">
              Apply filters
            </Button>
            <Button href="/" variant="ghost" class="justify-center">
              Reset
            </Button>
            <div class="hidden items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-cyan-100/55 xl:flex">
              <svg viewBox="0 0 24 24" class="h-8 w-8 text-cyan-200/70" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                <path d="M4 18h16" />
                <path d="M6 14h12" />
                <path d="M8 10h8" />
                <path d="M10 6h4" />
                <path d="M12 18c2.5-2.5 4.5-4.7 4.5-7.5A4.5 4.5 0 0 0 12 6a4.5 4.5 0 0 0-4.5 4.5c0 2.8 2 5 4.5 7.5Z" />
              </svg>
              <span>Signal tower online</span>
            </div>
          </div>
        </div>
      </form>
    </section>

    {#if loading}
      <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {#each Array.from({ length: 4 }) as _, index (index)}
          <div class="industrial-panel rounded-[10px] p-4">
            <Skeleton class="h-4 w-28" />
            <Skeleton class="mt-4 h-10 w-20" />
            <Skeleton class="mt-4 h-3 w-full" />
          </div>
        {/each}
      </section>
      <section class="industrial-panel rounded-[10px] p-4">
        <Skeleton class="h-5 w-40" />
        <div class="mt-4 space-y-3">
          {#each Array.from({ length: 4 }) as _, index (index)}
            <Skeleton class="h-14 w-full" />
          {/each}
        </div>
      </section>
    {:else if dashboard.error}
      <Alert
        variant="destructive"
        title="Unable to load dashboard"
        description={dashboard.error}
        class="industrial-panel rounded-[10px] border-rose-400/50 bg-[linear-gradient(180deg,rgba(48,12,20,0.96),rgba(19,8,12,0.96))] text-rose-100"
      />
    {:else}
      {@const alarms = dashboard.alarms!}
      <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article class="industrial-panel rounded-[10px] p-4">
          <div class="tech-label text-[10px] font-semibold text-cyan-100/70">Total alarms</div>
          <div class="mt-3 text-3xl font-semibold text-white">{formatCount(dashboard.summary?.total_alarms ?? dashboard.alarms?.total ?? 0)}</div>
          <div class="mt-3 text-sm text-[var(--text-secondary)]">Paginated records returned by the API.</div>
        </article>

        <article class="industrial-panel rounded-[10px] p-4">
          <div class="tech-label text-[10px] font-semibold text-cyan-100/70">By criticality</div>
          <div class="mt-3 flex flex-wrap gap-2">
            {#each summaryByCriticality() as [criticality, count] (criticality)}
              {@const meta = criticalityMeta(criticality)}
              <Badge variant={meta.tone}>
                <span class="inline-flex items-center gap-1.5">
                  <span>{meta.label}</span>
                  <span class="text-[10px] opacity-70">{formatCount(count)}</span>
                </span>
              </Badge>
            {/each}
            {#if summaryByCriticality().length === 0}
              <span class="text-sm text-[var(--text-muted)]">No criticality data</span>
            {/if}
          </div>
        </article>

        <article class="industrial-panel rounded-[10px] p-4">
          <div class="tech-label text-[10px] font-semibold text-cyan-100/70">By state</div>
          <div class="mt-3 flex flex-wrap gap-2">
            {#each summaryByState() as [state, count] (state)}
              {@const meta = stateMeta(state)}
              <Badge variant={meta.tone}>
                <span class="inline-flex items-center gap-1.5">
                  <span>{meta.label}</span>
                  <span class="text-[10px] opacity-70">{formatCount(count)}</span>
                </span>
              </Badge>
            {/each}
            {#if summaryByState().length === 0}
              <span class="text-sm text-[var(--text-muted)]">No state data</span>
            {/if}
          </div>
        </article>

        <article class="industrial-panel rounded-[10px] p-4">
          <div class="tech-label text-[10px] font-semibold text-cyan-100/70">Latest event</div>
          <div class="mt-3 text-2xl font-semibold text-white">
            {formatDateTime(dashboard.summary?.latest_event_time)}
          </div>
          <div class="mt-3 text-sm text-[var(--text-secondary)]">
            The freshest timestamp in the current dataset slice.
          </div>
        </article>
      </section>

      <section class="grid gap-4">
        <div class="industrial-panel rounded-[10px] p-4">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h2 class="text-lg font-semibold text-white">Top tags</h2>
              <p class="mt-1 text-sm text-[var(--text-secondary)]">
                Highest-volume tags inside the current filtered window.
              </p>
            </div>
            <Badge variant="muted">{dashboard.topTags?.total_tags ?? 0} tags</Badge>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {#each dashboard.topTags?.items ?? [] as item, index (item.tag)}
              <div class="flex items-center justify-between rounded-[8px] border border-cyan-300/15 bg-[rgba(7,12,18,0.62)] px-3 py-2">
                <div class="min-w-0 flex items-center gap-3">
                  <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-[6px] border border-cyan-300/15 bg-cyan-300/10 text-xs font-semibold text-cyan-100">
                    {index + 1}
                  </span>
                  <div class="min-w-0">
                    <div class="truncate text-sm font-medium text-white">{item.tag}</div>
                    <div class="text-xs text-[var(--text-muted)]">Alarm frequency</div>
                  </div>
                </div>
                <Badge variant={topTagVariant(index)} class="shrink-0">{formatCount(item.alarm_count)}</Badge>
              </div>
            {/each}
            {#if (dashboard.topTags?.items ?? []).length === 0}
              <div class="rounded-[8px] border border-dashed border-cyan-300/20 bg-[rgba(7,12,18,0.62)] px-4 py-5 text-sm text-[var(--text-muted)]">
                No tags matched the current filters.
              </div>
            {/if}
          </div>
        </div>

        <div class="industrial-panel rounded-[10px] p-4">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h2 class="text-lg font-semibold text-white">Alarm list</h2>
              <p class="mt-1 text-sm text-[var(--text-secondary)]">
                Paginated alarm records returned by the API.
              </p>
            </div>
            <Badge variant="default">{formatCount(dashboard.alarms?.total ?? 0)} records</Badge>
          </div>

          {#if (dashboard.alarms?.items ?? []).length > 0}
            <div class="metal-scrollbar mt-4 overflow-x-auto">
              <table class="min-w-[980px] w-full border-separate border-spacing-0">
                <thead>
                  <tr class="text-left text-[10px] uppercase tracking-[0.24em] text-cyan-100/60">
                    <th class="border-b border-cyan-300/15 px-3 py-3 font-semibold">Alarm</th>
                    <th class="border-b border-cyan-300/15 px-3 py-3 font-semibold">Asset</th>
                    <th class="border-b border-cyan-300/15 px-3 py-3 font-semibold">Criticality</th>
                    <th class="border-b border-cyan-300/15 px-3 py-3 font-semibold">State</th>
                    <th class="border-b border-cyan-300/15 px-3 py-3 font-semibold">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {#each alarms.items as alarm (alarm.id)}
                    {@const criticality = criticalityMeta(alarm.criticality)}
                    {@const state = stateMeta(alarm.state)}
                    <tr class="group align-top text-sm text-slate-100/90 transition-colors hover:bg-cyan-300/5">
                      <td class="border-b border-cyan-300/10 px-3 py-4">
                        <div class="space-y-2">
                          <div class="flex flex-wrap items-center gap-2">
                            <span class="font-semibold text-white">
                              {alarm.external_alarm_id ?? `Alarm ${alarm.id}`}
                            </span>
                            <Badge variant="muted" class="text-[10px]">P{displayPriority(alarm)}</Badge>
                          </div>
                          <div class="max-w-[24rem] text-sm leading-6 text-[var(--text-secondary)]">
                            {alarm.message ?? 'No message available'}
                          </div>
                        </div>
                      </td>
                      <td class="border-b border-cyan-300/10 px-3 py-4">
                        <div class="space-y-1">
                          <div class="text-white">{alarm.tag}</div>
                          <div class="text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">
                            {alarm.source_system ?? 'UNKNOWN SOURCE'}
                          </div>
                          <div class="text-xs text-[var(--text-muted)]">
                            {#if alarm.plant}{alarm.plant}{/if}
                            {#if alarm.area}<span class="mx-1">/</span>{alarm.area}{/if}
                            {#if alarm.equipment}<span class="mx-1">/</span>{alarm.equipment}{/if}
                            {#if !alarm.plant && !alarm.area && !alarm.equipment}No asset data{/if}
                          </div>
                        </div>
                      </td>
                      <td class="border-b border-cyan-300/10 px-3 py-4">
                        <Badge variant={criticality.tone}>{criticality.label}</Badge>
                      </td>
                      <td class="border-b border-cyan-300/10 px-3 py-4">
                        <Badge variant={state.tone}>{state.label}</Badge>
                      </td>
                      <td class="border-b border-cyan-300/10 px-3 py-4">
                        <div class="space-y-1">
                          <div class="text-white">{formatDateTime(alarm.event_time)}</div>
                          <div class="text-xs text-[var(--text-muted)]">
                            Ack {formatDateTime(alarm.ack_time)} / Clear {formatDateTime(alarm.clear_time)}
                          </div>
                        </div>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>

            <div class="mt-4 flex flex-col gap-3 border-t border-cyan-300/10 pt-4 sm:flex-row sm:items-center sm:justify-between">
              <div class="text-sm text-[var(--text-secondary)]">
                Page {alarms.page} of {alarms.pages} / {formatCount(alarms.total)} total alarms
              </div>
              <Pagination
                page={alarms.page}
                pages={alarms.pages}
                buildPageUrl={(page) => buildPageUrl(filters, page)}
                class="justify-start sm:justify-end"
              />
            </div>
          {:else}
            <div class="mt-4 rounded-[10px] border border-dashed border-cyan-300/20 bg-[rgba(7,12,18,0.62)] px-4 py-8 text-sm text-[var(--text-muted)]">
              No alarms matched the current filters.
            </div>
          {/if}
        </div>
      </section>
    {/if}
  </div>
</div>
