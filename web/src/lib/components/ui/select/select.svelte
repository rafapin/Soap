<script lang="ts">
  import { onMount } from 'svelte';
  import { cn } from '$lib/utils';
  import Button from '$lib/components/ui/button/button.svelte';

  export type SelectOption = {
    value: string;
    label: string;
    disabled?: boolean;
  };

  type Props = {
    name?: string;
    options: SelectOption[];
    placeholder?: string;
    class?: string;
    buttonClass?: string;
    panelClass?: string;
    value?: string;
    onChange?: (value: string) => void;
  };

  let {
    name,
    options,
    placeholder = 'Select an option',
    class: className = '',
    buttonClass = '',
    panelClass = '',
    value = $bindable(''),
    onChange
  }: Props = $props();

  let open = $state(false);
  let root: HTMLDivElement | null = null;

  const selectedLabel = $derived(options.find((option) => option.value === value)?.label ?? placeholder);

  function choose(option: SelectOption) {
    if (option.disabled) return;
    value = option.value;
    onChange?.(option.value);
    open = false;
  }

  onMount(() => {
    const handlePointerDown = (event: MouseEvent) => {
      if (!root) return;
      if (!root.contains(event.target as Node)) {
        open = false;
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        open = false;
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
    aria-haspopup="listbox"
    aria-expanded={open}
    aria-label={placeholder}
    onclick={() => (open = !open)}
  >
    <span class={cn('min-w-0 truncate', !value && 'text-[var(--text-muted)]')}>
      {selectedLabel}
    </span>
    <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0 text-cyan-200/80" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <path d="M6 9l6 6 6-6" />
    </svg>
  </Button>

  {#if open}
    <div
      role="listbox"
      class={cn(
        'absolute left-0 top-[calc(100%+0.5rem)] z-50 w-full overflow-hidden rounded-[10px] border border-cyan-200/45 bg-[rgba(4,10,15,0.99)] shadow-[0_18px_40px_rgba(0,0,0,0.7)] backdrop-blur-md',
        panelClass
      )}
    >
      <div class="max-h-64 overflow-auto p-1 metal-scrollbar">
        {#each options as option (option.value)}
          <button
            type="button"
            class={cn(
              'flex w-full items-center justify-between rounded-[8px] px-3 py-2 text-left text-sm transition-colors',
              option.disabled
                ? 'cursor-not-allowed text-[var(--text-muted)] opacity-50'
                : 'text-slate-100 hover:bg-cyan-300/14 hover:text-white',
              option.value === value && 'bg-cyan-300/18 text-cyan-50 ring-1 ring-cyan-200/30'
            )}
            data-selected={option.value === value}
            disabled={option.disabled}
            onclick={() => choose(option)}
          >
            <span class="truncate">{option.label}</span>
            {#if option.value === value}
              <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0 text-cyan-200" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M20 6 9 17l-5-5" />
              </svg>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>
