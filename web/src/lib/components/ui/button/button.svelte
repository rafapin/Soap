<script lang="ts">
  import { cn } from '$lib/utils';
  import type { Snippet } from 'svelte';

  type Props = {
    href?: string;
    variant?: 'default' | 'outline' | 'ghost' | 'destructive';
    size?: 'sm' | 'md';
    type?: 'button' | 'submit' | 'reset';
    class?: string;
    children?: Snippet;
  } & Record<string, unknown>;

  let {
    href,
    variant = 'default',
    size = 'md',
    type = 'button',
    class: className = '',
    children,
    ...rest
  }: Props = $props();

  const base =
    'inline-flex items-center justify-center gap-2 rounded-[6px] border text-sm font-medium tracking-wide transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-60';
  const variants = {
    default:
      'border-cyan-300/50 bg-[linear-gradient(180deg,rgba(56,189,248,0.18),rgba(7,12,18,0.96))] text-slate-50 shadow-[0_0_0_1px_rgba(103,232,249,0.12),0_0_18px_rgba(34,211,238,0.08)] hover:border-cyan-200 hover:text-white hover:shadow-[0_0_0_1px_rgba(103,232,249,0.24),0_0_24px_rgba(34,211,238,0.14)]',
    outline:
      'border-cyan-200/30 bg-[linear-gradient(180deg,rgba(8,16,22,0.98),rgba(9,14,21,0.98))] text-cyan-50 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] hover:border-cyan-200/60 hover:bg-[linear-gradient(180deg,rgba(14,24,32,0.98),rgba(7,12,18,0.98))] hover:text-white',
    ghost:
      'border-transparent bg-transparent text-slate-200 hover:border-cyan-300/20 hover:bg-cyan-300/10 hover:text-cyan-100',
    destructive:
      'border-rose-400/60 bg-[linear-gradient(180deg,rgba(244,63,94,0.86),rgba(98,17,33,0.98))] text-white shadow-[0_0_0_1px_rgba(244,63,94,0.16),0_0_18px_rgba(244,63,94,0.12)] hover:border-rose-300 hover:shadow-[0_0_0_1px_rgba(244,63,94,0.26),0_0_24px_rgba(244,63,94,0.18)]'
  } as const;
  const sizes = {
    sm: 'h-8 px-3',
    md: 'h-10 px-4'
  } as const;
</script>

{#if href}
  <a href={href} class={cn(base, variants[variant], sizes[size], className)} {...rest}>
    {@render children?.()}
  </a>
{:else}
  <button type={type} class={cn(base, variants[variant], sizes[size], className)} {...rest}>
    {@render children?.()}
  </button>
{/if}
