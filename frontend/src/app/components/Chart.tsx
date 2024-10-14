import React, { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import { EChartsOption } from "echarts";

const Chart = ({ option }: { option: EChartsOption }) => {
  const [error, setError] = useState<string | null>(null);
  const [chartOption, setChartOption] = useState<EChartsOption | null>(null);

  useEffect(() => {
    try {
      const { legend, series, title, tooltip, xAxis, yAxis } = option;
      
      // Check for required properties
      if (!series || !xAxis || !yAxis) {
        throw new Error("缺少必要的图表参数");
      }

      const newOption = {
        legend: {
          ...(legend || {}),
          left: "right",
        },
        series,
        title,
        tooltip,
        xAxis,
        yAxis,
      };

      setChartOption(newOption);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "图表参数错误");
      setChartOption(null);
    }
  }, [option]);

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center text-red-500">
        <p>图表加载失败: {error}</p>
      </div>
    );
  }

  if (!chartOption) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <p>正在加载图表...</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <ReactECharts
        option={chartOption}
        style={{ width: "100%", height: "500px" }}
      />
    </div>
  );
};

export default Chart;