import type { EChartsOption } from "echarts";

export function useChartData() {
  function makeLineOption(data: any[], xField: string, yField: string, name: string): EChartsOption {
    return {
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: data.map((d) => d[xField]) },
      yAxis: { type: "value", name: "万辆" },
      series: [{ name, type: "line", data: data.map((d) => d[yField]), smooth: true }],
    };
  }

  function makeMultiLineOption(seriesList: { name: string; data: number[] }[], categories: string[]): EChartsOption {
    return {
      tooltip: { trigger: "axis" },
      legend: { bottom: 0 },
      xAxis: { type: "category", data: categories },
      yAxis: { type: "value", name: "万辆" },
      series: seriesList.map((s) => ({
        name: s.name,
        type: "line",
        data: s.data,
        smooth: true,
      })),
    };
  }

  function makePieOption(data: { name: string; value: number }[]): EChartsOption {
    return {
      tooltip: { trigger: "item" },
      legend: { bottom: 0 },
      series: [
        {
          type: "pie",
          radius: ["45%", "70%"],
          data,
          label: { formatter: "{b}\n{d}%" },
        },
      ],
    };
  }

  function makeBarOption(data: any[], xField: string, yField: string): EChartsOption {
    return {
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: data.map((d) => d[xField]) },
      yAxis: { type: "value", name: "万辆" },
      series: [{ type: "bar", data: data.map((d) => d[yField]) }],
    };
  }

  return { makeLineOption, makeMultiLineOption, makePieOption, makeBarOption };
}