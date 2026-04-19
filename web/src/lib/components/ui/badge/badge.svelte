<script lang="ts">
  import { cn } from '$lib/utils';
  import type { Snippet } from 'svelte';

  type Props = {
    variant?: 'default' | 'success' | 'warning' | 'destructive' | 'muted';
    class?: string;
    children?: Snippet;
  };

  let { variant = 'default', class: className = '', children }: Props = $props();

  const variants = {
    default:
      'border-cyan-300/25 bg-[linear-gradient(180deg,rgba(15,25,33,0.96),rgba(9,15,21,0.96))] text-cyan-50 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]',
    success:
      'border-emerald-400/45 bg-[linear-gradient(180deg,rgba(13,54,38,0.96),rgba(7,22,16,0.96))] text-emerald-200 shadow-[0_0_18px_rgba(34,197,94,0.08)]',
    warning:
      'border-amber-300/50 bg-[linear-gradient(180deg,rgba(74,46,8,0.96),rgba(26,18,5,0.96))] text-amber-200 shadow-[0_0_18px_rgba(245,158,11,0.08)]',
    destructive:
      'border-rose-300/50 bg-[linear-gradient(180deg,rgba(82,20,33,0.96),rgba(31,11,17,0.96))] text-rose-200 shadow-[0_0_18px_rgba(244,63,94,0.08)]',
    muted:
      'border-slate-500/30 bg-[linear-gradient(180deg,rgba(10,17,24,0.96),rgba(6,10,15,0.96))] text-slate-200'
  } as const;
</script>

<span class={cn('inline-flex items-center gap-1.5 rounded-[6px] border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide leading-none', variants[variant], className)}>
  {@render children?.()}
</span>
