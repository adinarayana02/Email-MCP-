import React from 'react';
import { LineChart as RLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const TimeSeriesChart = ({ data = [], metrics = [], timeFormat = 'MMM DD', height = 300 }) => {
  const chartData = data.length > 0 ? data : [
    { date: 'Day 1', total: 50, resolved: 35, pending: 15 },
    { date: 'Day 2', total: 60, resolved: 42, pending: 18 },
    { date: 'Day 3', total: 55, resolved: 40, pending: 15 },
    { date: 'Day 4', total: 70, resolved: 50, pending: 20 }
  ];

  const defaultMetrics = metrics.length > 0 ? metrics : [
    { key: 'total', name: 'Total', color: '#3B82F6' },
    { key: 'resolved', name: 'Resolved', color: '#10B981' },
    { key: 'pending', name: 'Pending', color: '#F97316' }
  ];

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RLineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#6B7280' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 12, fill: '#6B7280' }} axisLine={false} tickLine={false} />
          <Tooltip />
          <Legend />
          {defaultMetrics.map((m) => (
            <Line key={m.key} type="monotone" dataKey={m.key} name={m.name} stroke={m.color} dot={false} strokeWidth={2} />
          ))}
        </RLineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TimeSeriesChart;


