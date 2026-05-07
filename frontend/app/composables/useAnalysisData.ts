import { ref, watch } from "vue";
import { useFilterStore } from "~/stores/filter";
import { useApi } from "./useApi";

export function useAnalysisData() {
  const filter = useFilterStore();
  const api = useApi();

  const nevShareTrend = ref<any[]>([]);
  const nevShareOverview = ref<any>(null);
  const nevBreakdown = ref<any[]>([]);
  const nevBreakdownDetail = ref<any>(null);
  const loading = ref(false);

  async function fetchNevShareTrend() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/analysis/nev-share/trend", {
        years: filter.yearsRange,
        granularity: filter.granularity,
      });
      nevShareTrend.value = res?.data ?? res ?? [];
    } finally {
      loading.value = false;
    }
  }

  async function fetchNevShareOverview() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/analysis/nev-share/overview", {
        year: filter.selectedYear,
        month: filter.selectedMonth,
      });
      nevShareOverview.value = res?.data ?? res;
    } finally {
      loading.value = false;
    }
  }

  async function fetchNevBreakdown() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/analysis/nev-breakdown", {
        years: filter.yearsRange,
        granularity: filter.granularity,
      });
      nevBreakdown.value = res?.data ?? res ?? [];
    } finally {
      loading.value = false;
    }
  }

  async function fetchNevBreakdownDetail() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/analysis/nev-breakdown/detail", {
        year: filter.selectedYear,
        month: filter.selectedMonth,
      });
      nevBreakdownDetail.value = res?.data ?? res;
    } finally {
      loading.value = false;
    }
  }

  watch(
    () => [filter.selectedYear, filter.selectedMonth, filter.yearsRange, filter.granularity],
    () => {
      fetchNevShareTrend();
      fetchNevShareOverview();
      fetchNevBreakdown();
      fetchNevBreakdownDetail();
    },
    { immediate: true }
  );

  return { nevShareTrend, nevShareOverview, nevBreakdown, nevBreakdownDetail, loading };
}