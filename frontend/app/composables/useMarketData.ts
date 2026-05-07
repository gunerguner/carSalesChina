import { ref, watch } from "vue";
import { useFilterStore } from "~/stores/filter";
import { useApi } from "./useApi";

export function useMarketData() {
  const filter = useFilterStore();
  const api = useApi();

  const overview = ref<any>(null);
  const trend = ref<any[]>([]);
  const yearly = ref<any[]>([]);
  const compare = ref<any>(null);
  const byEnergy = ref<any[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchOverview() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/market/overview", {
        year: filter.selectedYear,
        month: filter.selectedMonth,
        energy_type: filter.energyType,
      });
      overview.value = res?.data ?? res;
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTrend() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/market/trend", {
        energy_type: filter.energyType,
        years: filter.yearsRange,
        granularity: filter.granularity,
      });
      trend.value = res?.data ?? res ?? [];
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchYearly() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/market/yearly", {
        year: filter.selectedYear,
        energy_type: filter.energyType,
      });
      yearly.value = res?.data ?? res ?? [];
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchCompare(sy: number, sm: number, ey: number, em: number) {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/market/compare", {
        energy_type: filter.energyType,
        start_year: sy, start_month: sm, end_year: ey, end_month: em,
      });
      compare.value = res?.data ?? res;
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchByEnergy() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/market/byEnergyType", {
        year: filter.selectedYear,
        month: filter.selectedMonth,
      });
      byEnergy.value = res?.data ?? res ?? [];
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  watch(
    () => [filter.selectedYear, filter.selectedMonth, filter.energyType, filter.yearsRange, filter.granularity],
    () => {
      fetchOverview();
      fetchTrend();
      fetchYearly();
      fetchByEnergy();
    },
    { immediate: true }
  );

  return { overview, trend, yearly, compare, byEnergy, loading, error, fetchCompare };
}