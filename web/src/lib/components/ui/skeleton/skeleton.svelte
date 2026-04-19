<script lang="ts">
  import { cn } from '$lib/utils';

  type Props = {
    class?: string;
  };

  let { class: className = '' }: Props = $props();
</script>

<div class={cn('animate-pulse rounded-md bg-neutral-200', className)} aria-hidden="true"></div>
