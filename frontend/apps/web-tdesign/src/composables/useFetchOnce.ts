import { ref } from 'vue';

/**
 * Dedupes in-flight work and optionally skips after first successful run (until `invalidate()`).
 * Used by sales data composables that load once per session unless `force` is true.
 */
export function createFetchOnceController() {
  const loading = ref(false);
  let hasFetched = false;
  let pending: null | Promise<void> = null;

  async function execute(force: boolean, task: () => Promise<void>): Promise<void> {
    if (!force && hasFetched) {
      return;
    }
    if (pending) {
      return pending;
    }

    pending = (async () => {
      loading.value = true;
      try {
        await task();
        hasFetched = true;
      } catch {
        // keep hasFetched false so callers can retry (matches previous per-feature behavior)
      } finally {
        loading.value = false;
        pending = null;
      }
    })();

    return pending;
  }

  function invalidate() {
    hasFetched = false;
  }

  return { execute, invalidate, loading };
}

/**
 * Monotonic id for request coalescing (e.g. brand fetch: ignore stale responses after filters change).
 */
export function createGenerationTracker() {
  let gen = 0;
  return {
    matches(id: number): boolean {
      return id === gen;
    },
    next(): number {
      return ++gen;
    },
  };
}
