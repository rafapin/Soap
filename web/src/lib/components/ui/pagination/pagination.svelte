<script lang="ts">
  import Button from '$lib/components/ui/button/button.svelte';

  type Props = {
    page: number;
    pages: number;
    buildPageUrl: (page: number) => string;
    class?: string;
  };

  let { page, pages, buildPageUrl, class: className = '' }: Props = $props();

  function windowPages(current: number, total: number) {
    if (total <= 7) {
      return Array.from({ length: total }, (_, index) => index + 1);
    }

    const result = new Set<number>([1, total, current - 1, current, current + 1]);
    return Array.from(result)
      .filter((value) => value >= 1 && value <= total)
      .sort((a, b) => a - b);
  }

  let visiblePages = $derived(windowPages(page, pages));
</script>

<nav class={className} aria-label="Pagination">
  <div class="flex flex-wrap items-center gap-2">
    <Button
      href={page > 1 ? buildPageUrl(page - 1) : undefined}
      variant="outline"
      size="sm"
      disabled={page <= 1}
      aria-label="Previous page"
      class="min-w-9 px-2"
    >
      <span aria-hidden="true" class="text-sm leading-none">&larr;</span>
    </Button>

    {#each visiblePages as item, index (item)}
      {#if index > 0 && item - visiblePages[index - 1] > 1}
        <span class="px-1 text-sm text-cyan-100/50" aria-hidden="true">...</span>
      {/if}
      <Button
        href={buildPageUrl(item)}
        variant={item === page ? 'default' : 'outline'}
        size="sm"
        aria-current={item === page ? 'page' : undefined}
        aria-label={`Page ${item}`}
        class="min-w-9 px-3"
      >
        {item}
      </Button>
    {/each}

    <Button
      href={page < pages ? buildPageUrl(page + 1) : undefined}
      variant="outline"
      size="sm"
      disabled={page >= pages}
      aria-label="Next page"
      class="min-w-9 px-2"
    >
      <span aria-hidden="true" class="text-sm leading-none">&rarr;</span>
    </Button>
  </div>
</nav>
