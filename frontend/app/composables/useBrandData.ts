import { ref } from "vue";
import { useFilterStore } from "~/stores/filter";
import { useApi } from "./useApi";

export function useBrandData() {
  const filter = useFilterStore();
  const api = useApi();

  const ranking = ref<any>({ data: [], total: 0 });
  const yearlyRanking = ref<any>({ data: [], total: 0 });
  const detail = ref<any>(null);
  const trend = ref<any[]>([]);
  const compareResult = ref<any[]>([]);
  const compareTrend = ref<any[]>([]);
  const loading = ref(false);

  async function fetchRanking(nevOnly?: number) {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/brands/ranking", {
        year: filter.selectedYear,
        month: filter.selectedMonth,
        page: 1,
        pageSize: 50,
        is_nev: nevOnly,
      });
      ranking.value = res?.data ?? res ?? { data: [], total: 0 };
    } finally {
      loading.value = false;
    }
  }

  async function fetchYearlyRanking() {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/brands/ranking/yearly", {
        year: filter.selectedYear,
      });
      yearlyRanking.value = res?.data ?? res ?? { data: [], total: 0 };
    } finally {
      loading.value = false;
    }
  }

  async function fetchDetail(brandId: number) {
    loading.value = true;
    try {
      const res: any = await api.get(`/api/v1/brands/${brandId}/detail`, {
        year: filter.selectedYear,
        month: filter.selectedMonth,
      });
      detail.value = res?.data ?? res;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTrend(brandId: number) {
    loading.value = true;
    try {
      const res: any = await api.get(`/api/v1/brands/${brandId}/trend`, {
        years: filter.yearsRange,
        granularity: filter.granularity,
      });
      trend.value = res?.data ?? res ?? [];
    } finally {
      loading.value = false;
    }
  }

  async function fetchCompare(brandIds: string) {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/brands/compare", {
        brand_ids: brandIds,
        year: filter.selectedYear,
        month: filter.selectedMonth,
      });
      compareResult.value = res?.data ?? res ?? [];
    } finally {
      loading.value = false;
    }
  }

  async function fetchCompareTrend(brandIds: string) {
    loading.value = true;
    try {
      const res: any = await api.get("/api/v1/brands/compare/trend", {
        brand_ids: brandIds,
        years: filter.yearsRange,
        granularity: filter.granularity,
      });
      compareTrend.value = res?.data ?? res ?? [];
    } finally {
      loading.value = false;
    }
  }

  return { ranking, yearlyRanking, detail, trend, compareResult, compareTrend, loading, fetchRanking, fetchYearlyRanking, fetchDetail, fetchTrend, fetchCompare, fetchCompareTrend };
}