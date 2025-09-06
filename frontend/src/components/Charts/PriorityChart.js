import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PriorityChart = ({ data = [] }) => {
  // Default data if none provided
  const chartData = data.length > 0 ? data : [
    { name: 'Urgent', value: 15, color: '#EF4444' },
    { name: 'High', value: 25, color: '#F97316' },
    { name: 'Normal', value: 45, color: '#3B82F6' },
    { name: 'Low', value: 15, color: '#9CA3AF' }
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const total = chartData.reduce((sum, item) => sum + item.value, 0);
      const percentage = ((data.value / total) * 100).toFixed(1);
      
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{label}</p>
          <p className="text-sm text-gray-600">
            Count: {data.value} ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomBar = (props) => {
    const { x, y, width, height, index } = props;
    const data = chartData[index];
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={data.color}
          rx={4}
          ry={4}
        />
        {/* Add a subtle gradient effect */}
        <rect
          x={x}
          y={y}
          width={width}
          height={height * 0.3}
          fill="url(#gradient)"
          rx={4}
          ry={4}
        />
        {/* Add value label on top of each bar */}
        <text
          x={x + width / 2}
          y={y - 8}
          textAnchor="middle"
          className="text-xs font-medium fill-gray-600"
        >
          {data.value}
        </text>
      </g>
    );
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          {/* Define gradient for bars */}
          <defs>
            <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(255,255,255,0.3)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0)" />
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="name" 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#6B7280' }}
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#6B7280' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="value" 
            shape={<CustomBar />}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      
      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-4 gap-4">
        {chartData.map((item, index) => (
          <div key={index} className="text-center">
            <div 
              className="w-3 h-3 rounded-full mx-auto mb-2"
              style={{ backgroundColor: item.color }}
            />
            <p className="text-lg font-bold text-gray-900">{item.value}</p>
            <p className="text-xs text-gray-500">{item.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PriorityChart;
