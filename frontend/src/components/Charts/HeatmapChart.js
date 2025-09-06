import React from 'react';

const HeatmapChart = ({ data = [[]], title, xLabel, yLabel, dayLabels = [] }) => {
  const chartData = data && data.length ? data : Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => Math.floor(Math.random() * 20)));
  const max = Math.max(...chartData.flat(), 1);

  const colorFor = (v) => {
    const t = v / max;
    const r = Math.floor(239 + (255 - 239) * t);
    const g = Math.floor(68 + (255 - 68) * t);
    const b = Math.floor(68 + (255 - 68) * t);
    return `rgb(${r}, ${g}, ${b})`;
  };

  return (
    <div>
      {title && <h3 className="text-lg font-medium text-gray-800 mb-4">{title}</h3>}
      <div className="overflow-x-auto">
        <div className="inline-block">
          {chartData.map((row, i) => (
            <div key={i} className="flex items-center mb-1">
              <div className="w-24 text-xs text-gray-600 pr-2 text-right">
                {dayLabels[i] || `Day ${i + 1}`}
              </div>
              {row.map((v, j) => (
                <div key={j} className="w-6 h-6 mr-1 rounded" title={`${v}`} style={{ backgroundColor: colorFor(v) }} />
              ))}
            </div>
          ))}
        </div>
      </div>
      <div className="flex justify-between text-xs text-gray-500 mt-2">
        <span>{yLabel}</span>
        <span>{xLabel}</span>
      </div>
    </div>
  );
};

export default HeatmapChart;


