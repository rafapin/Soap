<script lang="ts">
  import { onMount } from 'svelte';
  import { cn } from '$lib/utils';
  import Button from '$lib/components/ui/button/button.svelte';
  import Select, { type SelectOption } from '$lib/components/ui/select/select.svelte';

  type Props = {
    name?: string;
    placeholder?: string;
    class?: string;
    buttonClass?: string;
    panelClass?: string;
    min?: string;
    max?: string;
    value?: string;
  };

  let {
    name,
    placeholder = 'Select date',
    class: className = '',
    buttonClass = '',
    panelClass = '',
    min,
    max,
    value = $bindable('')
  }: Props = $props();

  type CalendarCell = {
    iso: string;
    date: Date;
    inMonth: boolean;
    disabled: boolean;
    today: boolean;
    selected: boolean;
  };

  let open = $state(false);
  let root: HTMLDivElement | null = null;
  let activeMonth = $state(startOfMonth(parseDateValue(value) ?? new Date()));

  const monthFormatter = new Intl.DateTimeFormat('es-CO', {
    month: 'long',
    year: 'numeric'
  });
  const triggerFormatter = new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });

  const selectedDate = $derived(parseDateValue(value));
  const days = $derived(buildCalendar(activeMonth, selectedDate));
  const monthLabels = Array.from({ length: 12 }, (_, index) => {
    const label = new Intl.DateTimeFormat('es-CO', { month: 'long' }).format(new Date(2026, index, 1));
    return label.charAt(0).toUpperCase() + label.slice(1);
  });
  const monthOptions: SelectOption[] = monthLabels.map((label, index) => ({
    value: String(index),
    label
  }));
  let monthValue = $state('');
  let yearValue = $state('');
  function pad(value: number) {
    return String(value).padStart(2, '0');
  }

  function formatIso(date: Date) {
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
  }

  function parseDateValue(dateValue: string | null | undefined) {
    if (!dateValue) return null;
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateValue.slice(0, 10));
    if (!match) return null;
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const parsed = new Date(year, month - 1, day);
    if (Number.isNaN(parsed.getTime())) {
      return null;
    }
    return parsed;
  }

  function startOfMonth(date: Date) {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  }

  function startOfToday() {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }

  function sameDay(left: Date, right: Date) {
    return (
      left.getFullYear() === right.getFullYear() &&
      left.getMonth() === right.getMonth() &&
      left.getDate() === right.getDate()
    );
  }

  function sameMonth(left: Date, right: Date) {
    return left.getFullYear() === right.getFullYear() && left.getMonth() === right.getMonth();
  }

  function isBefore(left: Date, right: Date) {
    return left.getTime() < right.getTime() && !sameDay(left, right);
  }

  function isAfter(left: Date, right: Date) {
    return left.getTime() > right.getTime() && !sameDay(left, right);
  }

  function isDisabled(date: Date) {
    const minDate = parseDateValue(min);
    const maxDate = parseDateValue(max);
    if (minDate && isBefore(date, minDate)) return true;
    if (maxDate && isAfter(date, maxDate)) return true;
    return false;
  }

  function buildCalendar(month: Date, selection: Date | null): CalendarCell[] {
    const normalizedMonth = startOfMonth(month);
    const currentDay = startOfToday();
    const mondayOffset = (normalizedMonth.getDay() + 6) % 7;
    const firstVisible = new Date(
      normalizedMonth.getFullYear(),
      normalizedMonth.getMonth(),
      1 - mondayOffset
    );

    return Array.from({ length: 42 }, (_, index) => {
      const date = new Date(
        firstVisible.getFullYear(),
        firstVisible.getMonth(),
        firstVisible.getDate() + index
      );
      return {
        iso: formatIso(date),
        date,
        inMonth: sameMonth(date, normalizedMonth),
        disabled: isDisabled(date),
        today: sameDay(date, currentDay),
        selected: Boolean(selection && sameDay(date, selection))
      };
    });
  }

  function formattedValue(dateValue: string) {
    const parsed = parseDateValue(dateValue);
    return parsed ? triggerFormatter.format(parsed) : '';
  }

  function syncPickerValues() {
    monthValue = String(activeMonth.getMonth());
    yearValue = String(activeMonth.getFullYear());
  }

  function openCalendar() {
    activeMonth = startOfMonth(selectedDate ?? new Date());
    syncPickerValues();
    open = !open;
  }

  function closeCalendar() {
    open = false;
  }

  function selectDate(date: Date) {
    value = formatIso(date);
    activeMonth = startOfMonth(date);
    syncPickerValues();
    closeCalendar();
  }

  function shiftMonth(delta: number) {
    activeMonth = new Date(activeMonth.getFullYear(), activeMonth.getMonth() + delta, 1);
    syncPickerValues();
  }

  function setMonth(monthIndex: number) {
    activeMonth = new Date(activeMonth.getFullYear(), monthIndex, 1);
    syncPickerValues();
  }

  function setYear(year: number) {
    activeMonth = new Date(year, activeMonth.getMonth(), 1);
    syncPickerValues();
  }

  function yearOptions() {
    const currentYear = new Date().getFullYear();
    const minYear = parseDateValue(min)?.getFullYear() ?? currentYear - 10;
    const maxYear = parseDateValue(max)?.getFullYear() ?? currentYear + 10;
    const start = Math.min(minYear, currentYear - 10);
    const end = Math.max(maxYear, currentYear + 10);

    return Array.from({ length: end - start + 1 }, (_, index) => {
      const year = start + index;
      return {
        value: String(year),
        label: String(year)
      };
    });
  }

  function clearDate() {
    value = '';
    activeMonth = startOfMonth(new Date());
    syncPickerValues();
    closeCalendar();
  }

  function selectToday() {
    selectDate(startOfToday());
  }

  syncPickerValues();

  onMount(() => {
    const handlePointerDown = (event: MouseEvent) => {
      if (!root) return;
      if (!root.contains(event.target as Node)) {
        closeCalendar();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeCalendar();
      }
    };

    document.addEventListener('mousedown', handlePointerDown);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handlePointerDown);
      document.removeEventListener('keydown', handleEscape);
    };
  });
</script>

<div bind:this={root} class={cn('relative', className)}>
  {#if name}
    <input type="hidden" {name} value={value} />
  {/if}

  <Button
    type="button"
    variant="outline"
    class={cn('w-full justify-between gap-3 text-left', buttonClass)}
    aria-haspopup="dialog"
    aria-expanded={open}
    aria-label={placeholder}
    onclick={openCalendar}
  >
    <span class={cn('min-w-0 truncate', !value && 'text-[var(--text-muted)]')}>
      {value ? formattedValue(value) : placeholder}
    </span>
    <svg
      viewBox="0 0 24 24"
      class="h-4 w-4 shrink-0 text-cyan-200/80"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      aria-hidden="true"
    >
      <rect x="4" y="5" width="16" height="15" rx="2.5" />
      <path d="M8 3v4M16 3v4M4 10h16" />
    </svg>
  </Button>

  {#if open}
    <div
      role="dialog"
      class={cn(
        'absolute left-0 top-[calc(100%+0.5rem)] z-50 w-[min(22rem,calc(100vw-2rem))] overflow-visible rounded-[10px] border border-cyan-200/45 bg-[rgba(4,10,15,0.99)] shadow-[0_18px_40px_rgba(0,0,0,0.7)] backdrop-blur-md',
        panelClass
      )}
    >
      <div class="border-b border-cyan-300/15 px-3 py-3">
        <div class="flex items-center justify-between gap-3">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            class="h-8 px-2 text-cyan-100 hover:bg-cyan-300/10"
            aria-label="Previous month"
            onclick={() => shiftMonth(-1)}
          >
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="m15 18-6-6 6-6" />
            </svg>
          </Button>

          <div class="text-center">
            <div class="tech-label text-[10px] font-semibold text-cyan-100/65">Calendar</div>
            <div class="mt-1 text-sm font-semibold text-white">
              {monthFormatter.format(activeMonth)}
            </div>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            class="h-8 px-2 text-cyan-100 hover:bg-cyan-300/10"
            aria-label="Next month"
            onclick={() => shiftMonth(1)}
          >
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="m9 18 6-6-6-6" />
            </svg>
          </Button>
        </div>

        <div class="mt-3 grid grid-cols-2 gap-2">
          <label class="space-y-1">
            <span class="tech-label block text-[9px] font-semibold text-cyan-100/55">Month</span>
            <Select
              bind:value={monthValue}
              options={monthOptions}
              placeholder="Month"
              class="w-full"
              buttonClass="h-9"
              panelClass="w-full"
              onChange={(selected) => setMonth(Number(selected))}
            />
          </label>

          <label class="space-y-1">
            <span class="tech-label block text-[9px] font-semibold text-cyan-100/55">Year</span>
            <Select
              bind:value={yearValue}
              options={yearOptions()}
              placeholder="Year"
              class="w-full"
              buttonClass="h-9"
              panelClass="w-full"
              onChange={(selected) => setYear(Number(selected))}
            />
          </label>
        </div>
      </div>

      <div class="px-3 py-3">
        <div class="grid grid-cols-7 gap-1 text-[10px] uppercase tracking-[0.22em] text-cyan-100/55">
          <div class="text-center">Mo</div>
          <div class="text-center">Tu</div>
          <div class="text-center">We</div>
          <div class="text-center">Th</div>
          <div class="text-center">Fr</div>
          <div class="text-center">Sa</div>
          <div class="text-center">Su</div>
        </div>

        <div class="mt-2 grid gap-1">
          {#each Array.from({ length: 6 }) as _, weekIndex (weekIndex)}
            <div class="grid grid-cols-7 gap-1">
              {#each days.slice(weekIndex * 7, weekIndex * 7 + 7) as day (day.iso)}
                <button
                  type="button"
                  class={cn(
                    'flex h-9 items-center justify-center rounded-[6px] border text-sm font-medium transition-all',
                    day.inMonth
                      ? 'border-cyan-300/15 text-slate-100 hover:border-cyan-200/45 hover:bg-cyan-300/12 hover:text-white'
                      : 'border-transparent text-slate-500/55',
                    day.today && 'ring-1 ring-cyan-200/30',
                    day.selected && 'border-cyan-200/60 bg-cyan-300/18 text-white shadow-[0_0_18px_rgba(34,211,238,0.12)]',
                    day.disabled && 'pointer-events-none cursor-not-allowed opacity-35'
                  )}
                  aria-label={day.iso}
                  aria-pressed={day.selected}
                  disabled={day.disabled}
                  onclick={() => selectDate(day.date)}
                >
                  {day.date.getDate()}
                </button>
              {/each}
            </div>
          {/each}
        </div>

        <div class="mt-3 flex items-center justify-between gap-2 border-t border-cyan-300/10 pt-3">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            class="h-8 px-3 text-slate-300 hover:bg-cyan-300/10 hover:text-white"
            onclick={clearDate}
          >
            Clear
          </Button>

          <div class="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              class="h-8 px-3 text-cyan-100 hover:bg-cyan-300/10"
              onclick={selectToday}
            >
              Today
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              class="h-8 px-3 text-cyan-100 hover:bg-cyan-300/10"
              onclick={closeCalendar}
            >
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
