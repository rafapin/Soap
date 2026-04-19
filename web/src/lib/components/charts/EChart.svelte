<script lang="ts">
  import { cn } from '$lib/utils';
  import type { EChartsOption, EChartsType } from 'echarts';

  type Props = {
    option: EChartsOption;
    ariaLabel: string;
    class?: string;
  };

  let { option, ariaLabel, class: className = '' }: Props = $props();
  let chartElement = $state<HTMLDivElement>();

  $effect(() => {
    const target = chartElement;
    const currentOption = option;
    if (!target) return;

    let disposed = false;
    let chart: EChartsType | null = null;
    let observer: ResizeObserver | null = null;

    void import('echarts').then((echarts) => {
      if (disposed) return;

      chart = echarts.init(target, undefined, { renderer: 'canvas' });
      chart.setOption(currentOption, true);

      observer = new ResizeObserver(() => chart?.resize());
      observer.observe(target);
      requestAnimationFrame(() => chart?.resize());
    });

    return () => {
      disposed = true;
      observer?.disconnect();
      chart?.dispose();
    };
  });
</script>

<div
  bind:this={chartElement}
  class={cn('h-72 w-full min-w-0', className)}
  role="img"
  aria-label={ariaLabel}
></div>
