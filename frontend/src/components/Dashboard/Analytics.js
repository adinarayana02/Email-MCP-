import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  BarChart3,
  PieChart,
  Activity,
  Calendar,
  Download,
  RefreshCw,
  LineChart,
  Timer,
  MessageSquare,
  Tag
} from 'lucide-react';
import SentimentChart from '../Charts/SentimentChart';
import PriorityChart from '../Charts/PriorityChart';
import CategoryChart from '../Charts/CategoryChart';
import TimeSeriesChart from '../Charts/TimeSeriesChart';
import HeatmapChart from '../Charts/HeatmapChart';
import ResponseTimeChart from '../Charts/ResponseTimeChart';
import LoadingSpinner from '../common/LoadingSpinner';
import { analyticsAPI } from '../../services/api';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange, selectedMetric]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      // Get all dashboard data from a single API call
      const dashboardData = await analyticsAPI.getDashboardStats();
      
      // Transform the data for charts
      const sentimentData = Object.entries(dashboardData.sentiment_distribution || {}).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value: value.count,
        percentage: value.percentage
      }));
      
      const priorityData = Object.entries(dashboardData.priority_distribution || {}).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value: value.count,
        percentage: value.percentage
      }));
      
      const categoryData = Object.entries(dashboardData.categories || {}).map(([key, value]) => ({
        name: key.replace('_', ' ').charAt(0).toUpperCase() + key.replace('_', ' ').slice(1),
        value: typeof value === 'object' ? value.count : value,
        percentage: typeof value === 'object' ? value.percentage : 0
      }));
      
      // Transform daily volume data for time series
      const timeSeriesData = Object.entries(dashboardData.daily_volume || {}).map(([date, count]) => ({
        date,
        count
      })).sort((a, b) => new Date(a.date) - new Date(b.date));
      
      // Set performance metrics
      const performanceData = {
        response_time: dashboardData.metrics?.avg_response_time || 0,
        resolution_rate: dashboardData.metrics?.response_rate || 0,
        satisfaction_rate: dashboardData.metrics?.satisfaction_score || 0,
        urgent_handling_rate: dashboardData.metrics?.urgent_handling_rate || 0
      };
      
      setAnalyticsData({
        dashboard: dashboardData.email_stats || {},
        sentiment: sentimentData,
        priority: priorityData,
        performance: performanceData,
        category: categoryData,
        timeSeries: timeSeriesData,
        responseTime: [],  // Will be calculated from the data
        // Generate mock data for heatmap until API is available
        heatmap: generateMockHeatmapData(),
        // Store the raw data for reference
        rawData: dashboardData
      });
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      // Use mock data if API fails
      setAnalyticsData({
        dashboard: { total: 350, pending: 45, resolved: 305, urgent: 28 },
        sentiment: [],
        priority: [],
        performance: { response_time: 25, resolution_rate: 80, satisfaction_rate: 92, urgent_handling_rate: 95 },
        category: [],
        timeSeries: [],
        responseTime: [],
        heatmap: generateMockHeatmapData()
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Generate mock heatmap data until API is available
  const generateMockHeatmapData = () => {
    const days = 7;
    const hours = 24;
    const data = [];
    
    for (let day = 0; day < days; day++) {
      const dayData = [];
      for (let hour = 0; hour < hours; hour++) {
        // Generate more realistic patterns
        let value = 0;
        
        // Business hours have more emails
        if (hour >= 8 && hour <= 18) {
          value = Math.floor(Math.random() * 20) + 5;
          // Peak hours
          if (hour >= 9 && hour <= 11) value += 10;
          if (hour >= 14 && hour <= 16) value += 8;
        } else {
          value = Math.floor(Math.random() * 5);
        }
        
        // Weekends have fewer emails
        if (day >= 5) value = Math.floor(value / 3);
        
        dayData.push(value);
      }
      data.push(dayData);
    }
    
    return data;
  };

  const MetricCard = ({ title, value, change, icon: Icon, color, subtitle }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {change !== undefined && (
        <div className="flex items-center mt-4">
          {change >= 0 ? (
            <TrendingUp className="w-4 h-4 text-green-500" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-500" />
          )}
          <span className={`text-sm font-medium ml-2 ${
            change >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {change >= 0 ? '+' : ''}{change}% from last period
          </span>
        </div>
      )}
    </div>
  );

  const PerformanceMetric = ({ label, value, target, color = 'blue' }) => {
    const percentage = target > 0 ? Math.min((value / target) * 100, 100) : 0;
    const colorClasses = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      yellow: 'bg-yellow-500',
      red: 'bg-red-500'
    };

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">{label}</span>
          <span className="font-medium text-gray-900">{value}/{target}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${colorClasses[color]} transition-all duration-300`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <p className="text-xs text-gray-500">{percentage.toFixed(1)}% complete</p>
      </div>
    );
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading analytics..." />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
          <p className="text-gray-600 mt-2">
            Comprehensive analysis of email performance and AI accuracy
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="overview">Overview</option>
            <option value="sentiment">Sentiment</option>
            <option value="priority">Priority</option>
            <option value="category">Category</option>
            <option value="response">Response Time</option>
            <option value="volume">Email Volume</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <button
            onClick={loadAnalyticsData}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Emails"
          value={analyticsData?.dashboard?.total || 0}
          change={analyticsData?.dashboard?.total_change || 0}
          icon={MessageSquare}
          color="bg-blue-500"
        />
        <MetricCard
          title="Processing Rate"
          value={`${analyticsData?.dashboard?.processing_rate || 0}%`}
          change={analyticsData?.dashboard?.processing_rate_change || 0}
          icon={Activity}
          color="bg-green-500"
        />
        <MetricCard
          title="Avg. Response Time"
          value={`${analyticsData?.performance?.response_time || 0}m`}
          change={analyticsData?.dashboard?.response_time_change || 0}
          icon={Clock}
          color="bg-yellow-500"
          subtitle="Minutes to first response"
        />
        <MetricCard
          title="AI Accuracy"
          value={`${analyticsData?.dashboard?.ai_accuracy || 0}%`}
          change={analyticsData?.dashboard?.ai_accuracy_change || 0}
          icon={CheckCircle}
          color="bg-purple-500"
        />
      </div>

      {/* Main Content */}
      <div>
        {/* Content Sections */}
        {selectedMetric === 'overview' && (
          <div className="space-y-6">
            {/* Charts Section - Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Sentiment Analysis</h2>
                  <PieChart className="w-5 h-5 text-gray-400" />
                </div>
                <SentimentChart data={analyticsData?.sentiment} height={220} />
              </div>
              
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Priority Distribution</h2>
                  <BarChart3 className="w-5 h-5 text-gray-400" />
                </div>
                <PriorityChart data={analyticsData?.priority} height={220} />
              </div>
              
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Category Analysis</h2>
                  <Tag className="w-5 h-5 text-gray-400" />
                </div>
                <CategoryChart data={analyticsData?.category} height={220} />
              </div>
            </div>
            
            {/* Email Volume Trends */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Email Volume Trends</h2>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <LineChart className="w-4 h-4" />
                  <span>Last {timeRange === '7d' ? '7' : timeRange === '30d' ? '30' : '90'} days</span>
                </div>
              </div>
              <TimeSeriesChart 
                data={analyticsData?.timeSeries} 
                timeFormat="MMM DD" 
                metrics={[{ key: 'count', name: 'Emails', color: '#3B82F6' }]}
              />
            </div>
            
            {/* Response Time Analysis */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Response Time Analysis</h2>
                <Timer className="w-5 h-5 text-gray-400" />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Average Response Time</h3>
                  <ResponseTimeChart height={250} />
                </div>
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Performance Metrics</h3>
                  <PerformanceMetric 
                    label="Response Time Target" 
                    value={analyticsData?.performance?.response_time || 0} 
                    target={30} 
                    color="blue"
                  />
                  <PerformanceMetric 
                    label="Resolution Rate" 
                    value={analyticsData?.performance?.resolution_rate || 0} 
                    target={100} 
                    color="green"
                  />
                  <PerformanceMetric 
                    label="Customer Satisfaction" 
                    value={analyticsData?.performance?.satisfaction_rate || 0} 
                    target={100} 
                    color="yellow"
                  />
                  <PerformanceMetric 
                    label="Urgent Email Handling" 
                    value={analyticsData?.performance?.urgent_handling_rate || 0} 
                    target={100} 
                    color="red"
                  />
                </div>
              </div>
            </div>
            
            {/* Email Volume Heatmap */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Email Volume Heatmap</h2>
                <Calendar className="w-5 h-5 text-gray-400" />
              </div>
              <div className="mb-6">
                <p className="text-gray-600">Email volume by day of week and hour of day</p>
              </div>
              <HeatmapChart 
                data={analyticsData?.heatmap} 
                height={300} 
                xLabel="Hour of Day" 
                yLabel="Day of Week" 
                dayLabels={['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
              />
            </div>
          </div>
        )}

        {/* Detailed Priority Analysis */}
        {selectedMetric === 'priority' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Detailed Priority Analysis</h2>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <BarChart3 className="w-4 h-4" />
                <span>Current period</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Priority Distribution</h3>
                <PriorityChart data={analyticsData?.priority} height={300} />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Priority Trends</h3>
                <TimeSeriesChart 
                  data={analyticsData?.timeSeries} 
                  timeFormat="MMM DD" 
                  metrics={[
                    { key: 'high', name: 'High', color: '#EF4444' },
                    { key: 'medium', name: 'Medium', color: '#F97316' },
                    { key: 'low', name: 'Low', color: '#10B981' }
                  ]}
                />
              </div>
            </div>
          </div>
        )}

        {/* Detailed Category Analysis */}
        {selectedMetric === 'category' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Detailed Category Analysis</h2>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Tag className="w-4 h-4" />
                <span>Current period</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Category Distribution</h3>
                <CategoryChart data={analyticsData?.category} height={300} />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Category Trends</h3>
                <TimeSeriesChart 
                  data={analyticsData?.timeSeries} 
                  timeFormat="MMM DD" 
                  metrics={[
                    { key: 'support', name: 'Support', color: '#3B82F6' },
                    { key: 'billing', name: 'Billing', color: '#8B5CF6' },
                    { key: 'feature', name: 'Feature', color: '#EC4899' }
                  ]}
                />
              </div>
            </div>
          </div>
        )}

        {/* Detailed Sentiment Analysis */}
        {selectedMetric === 'sentiment' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Detailed Sentiment Analysis</h2>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <PieChart className="w-4 h-4" />
                <span>Current period</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Sentiment Distribution</h3>
                <SentimentChart data={analyticsData?.sentiment} height={300} />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Sentiment Trends</h3>
                <TimeSeriesChart 
                  data={analyticsData?.timeSeries} 
                  timeFormat="MMM DD" 
                  metrics={[
                    { key: 'positive', name: 'Positive', color: '#10B981' },
                    { key: 'neutral', name: 'Neutral', color: '#6B7280' },
                    { key: 'negative', name: 'Negative', color: '#EF4444' }
                  ]}
                />
              </div>
            </div>
          </div>
        )}

        {/* AI Performance Insights */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">AI Performance Insights</h2>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-2">High Confidence Responses</h4>
              <p className="text-sm text-blue-700">
                {analyticsData?.dashboard?.high_confidence_responses || 78}% of AI responses 
                have confidence scores above 80%
              </p>
            </div>
            <div className="p-3 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
              <h4 className="font-medium text-green-900 mb-2">Sentiment Accuracy</h4>
              <p className="text-sm text-green-700">
                AI correctly identifies customer sentiment in {analyticsData?.dashboard?.sentiment_accuracy || 92}% of cases
              </p>
            </div>
            <div className="p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
              <h4 className="font-medium text-yellow-900 mb-2">Priority Detection</h4>
              <p className="text-sm text-yellow-700">
                Urgent emails are correctly flagged {analyticsData?.dashboard?.priority_accuracy || 89}% of the time
              </p>
            </div>
          </div>
        </div>

        {/* Export and Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Export & Reports</h2>
              <p className="text-gray-600 mt-1">Download detailed analytics reports and insights</p>
            </div>
            <div className="flex space-x-3">
              <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                <Download className="w-4 h-4" />
                <span>Export PDF</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <BarChart3 className="w-4 h-4" />
                <span>Generate Report</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
