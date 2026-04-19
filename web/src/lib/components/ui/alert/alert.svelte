<script lang="ts">
  import { cn } from '$lib/utils';
  import type { Snippet } from 'svelte';

  type Props = {
    variant?: 'default' | 'destructive';
    title: string;
    description?: string;
    class?: string;
    children?: Snippet;
  };

  let { variant = 'default', title, description = '', class: className = '', children }: Props = $props();

  const variants = {
    default: 'border-neutral-200 bg-white text-neutral-900',
    destructive: 'border-rose-200 bg-rose-50 text-rose-900'
  } as const;
</script>

<div class={cn('rounded-md border px-4 py-3', variants[variant], className)} role="alert">
  <div class="text-sm font-semibold">{title}</div>
  {#if description}
    <div class="mt-1 text-sm leading-6 text-neutral-700">{description}</div>
  {/if}
  {@render children?.()}
</div>
