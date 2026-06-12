import { ref } from 'vue';

export const LOAD_FAILED_I18N_KEY = 'pages.common.loadFailed';

/**
 * Dedupes in-flight work and optionally skips after first successful run.
 * Used by data composables that load once per session unless `force` is true.
 */
export function createFetchOnceController() {
  const loading = ref(false);
  const error = ref<null | string>(null);
  let hasFetched = false;
  let pending: null | Promise<void> = null;

  function clearError() {
    error.value = null;
  }

  async function execute(
    force: boolean,
    task: () => Promise<void>,
  ): Promise<void> {
    if (!force && hasFetched) {
      return;
    }
    if (pending) {
      return pending;
    }

    pending = (async () => {
      loading.value = true;
      clearError();
      try {
        await task();
        hasFetched = true;
      } catch (error_) {
        error.value = LOAD_FAILED_I18N_KEY;
        console.error('[createFetchOnceController] execute failed', error_);
      } finally {
        loading.value = false;
        pending = null;
      }
    })();

    return pending;
  }

  return { error, execute, loading };
}

export interface KeyedFetchControllerOptions<T> {
  fetch: (key: string) => Promise<T>;
  getKey: () => string;
  isEmptyKey?: (key: string) => boolean;
}

/**
 * Parameterized fetch with generation-based stale-response guard and per-key cache.
 */
export function createKeyedFetchController<T>(
  options: KeyedFetchControllerOptions<T>,
) {
  const loading = ref(false);
  const error = ref<null | string>(null);
  const data = ref<null | T>(null) as { value: null | T };
  const cache = new Map<string, T>();
  let gen = 0;

  function clearError() {
    error.value = null;
  }

  async function execute(force = false): Promise<void> {
    const key = options.getKey();

    if (options.isEmptyKey?.(key)) {
      gen += 1;
      clearError();
      data.value = null;
      loading.value = false;
      return;
    }

    if (!force) {
      const cached = cache.get(key);
      if (cached !== undefined) {
        clearError();
        data.value = cached;
        return;
      }
    }

    const requestId = ++gen;
    const requestKey = key;
    loading.value = true;
    clearError();

    try {
      const result = await options.fetch(requestKey);
      if (requestId !== gen || requestKey !== options.getKey()) {
        return;
      }
      data.value = result;
      cache.set(requestKey, result);
    } catch (error_) {
      if (requestId !== gen) {
        return;
      }
      error.value = LOAD_FAILED_I18N_KEY;
      console.error('[createKeyedFetchController] execute failed', error_);
      data.value = null;
    } finally {
      if (requestId === gen) {
        loading.value = false;
      }
    }
  }

  return { data, error, execute, loading };
}
