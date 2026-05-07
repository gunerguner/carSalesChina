import { defineStore } from "pinia";
import { ref } from "vue";

export const useFilterStore = defineStore("filter", () => {
  const now = new Date();
  const selectedYear = ref(now.getFullYear());
  const selectedMonth = ref(now.getMonth() + 1);
  const yearsRange = ref(3);
  const granularity = ref<"monthly" | "yearly">("monthly");
  const energyType = ref("all");
  const selectedBrands = ref<string[]>([]);

  function updateFilters(partial: Record<string, any>) {
    Object.assign({ selectedYear, selectedMonth, yearsRange, granularity, energyType, selectedBrands }, partial);
  }

  return { selectedYear, selectedMonth, yearsRange, granularity, energyType, selectedBrands, updateFilters };
});