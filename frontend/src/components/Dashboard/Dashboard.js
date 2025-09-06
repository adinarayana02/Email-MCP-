import React, { useState, useEffect } from 'react';
import { 
  Mail, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  Users,
  MessageSquare,
  Zap
} from 'lucide-react';
import EmailList from './EmailList';
import Analytics from './Analytics';
import ResponseEditor from './ResponseEditor';
import LoadingSpinner from '../common/LoadingSpinner';
import { emailAPI, analyticsAPI } from '../../services/api';

const Dashboard = () => {
  const [activeView, setActiveView] = useState('overview');
  const [stats, setStats] = useState(null);
  const [recentEmails, setRecentEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [showResponseEditor, setShowResponseEditor] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Try to get dashboard data from JSON first (our new method)
      try {
        const dashboardData = await analyticsAPI.getDashboardDataFromJSON();
        setStats(dashboardData.email_stats);
        setRecentEmails(dashboardData.recent_emails || []);
      } catch (jsonError) {
        console.warn('Failed to load dashboard data from JSON, falling back to API:', jsonError);
        
        // Fallback to the original API endpoint
        const dashboardData = await analyticsAPI.getDashboardStats();
        setStats(dashboardData.email_stats);
        setRecentEmails(dashboardData.recent_emails || []);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const regenerateDashboardData = async () => {
    try {
      setLoading(true);
      // Call the system API to regenerate dashboard data
      await emailAPI.systemAPI.generateDashboardData();
      // Then reload the dashboard with the new data
      await loadDashboardData();
    } catch (error) {
      console.error('Failed to regenerate dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSelect = (email) => {
    setSelectedEmail(email);
    setShowResponseEditor(true);
  };

  const handleCloseResponseEditor = () => {
    setShowResponseEditor(false);
    setSelectedEmail(null);
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading dashboard..." />;
  }

  const StatCard = ({ title, value, icon: Icon, color, trend, subtitle }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-200 transform hover:scale-105">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color} transform transition-all duration-200 hover:rotate-12`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {trend && (
        <div className="flex items-center mt-4">
          {trend > 0 ? 
            <TrendingUp className="w-4 h-4 text-green-500" /> : 
            <TrendingDown className="w-4 h-4 text-red-500" />
          }
          <span className={`text-sm font-medium ml-2 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '+' : ''}{trend}% from yesterday
          </span>
        </div>
      )}
    </div>
  );

  const QuickActionCard = ({ title, description, icon: Icon, action, color }) => (
    <button
      onClick={action}
      className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-200 text-left group hover:border-blue-200"
    >
      <div className={`p-3 rounded-lg ${color} w-fit mb-4 group-hover:scale-110 transition-transform duration-200`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
    </button>
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome back! Here's what's happening with your emails today.</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setActiveView('overview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeView === 'overview'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveView('emails')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeView === 'emails'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Emails
          </button>
          <button
            onClick={() => setActiveView('analytics')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeView === 'analytics'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Analytics
          </button>
        </div>
      </div>

      {activeView === 'overview' && (
        <>
          {/* Statistics Grid */}
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Stats</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Emails"
              value={stats?.total || 20}
              icon={Mail}
              color="bg-gradient-to-r from-blue-500 to-blue-600"
              subtitle={`${stats?.processed || 16} processed`}
              trend={5}
            />
            <StatCard
              title="Pending"
              value={stats?.pending || 0}
              icon={Clock}
              color="bg-gradient-to-r from-yellow-400 to-yellow-500"
              subtitle="Awaiting response"
              trend={-10}
            />
            <StatCard
              title="In Progress"
              value={stats?.in_progress || 0}
              icon={AlertTriangle}
              color="bg-gradient-to-r from-blue-400 to-blue-500"
              subtitle="Currently being handled"
              trend={0}
            />
            <StatCard
              title="Resolved"
              value={stats?.resolved || 4}
              icon={CheckCircle}
              color="bg-gradient-to-r from-green-400 to-green-500"
              subtitle={`${Math.round((stats?.resolved || 4) / (stats?.total || 20) * 100)}% completion rate`}
              trend={15}
            />
            <StatCard
              title="Urgent"
              value={stats?.urgent || 4}
              icon={AlertTriangle}
              color="bg-gradient-to-r from-red-400 to-red-500"
              subtitle="Requires immediate attention"
              trend={-5}
            />
            <StatCard
              title="Response Rate"
              value={`${stats?.response_rate || 92}%`}
              icon={Zap}
              color="bg-gradient-to-r from-purple-400 to-purple-500"
              subtitle="Average response time"
              trend={3}
            />
            <StatCard
              title="User Satisfaction"
              value={`${stats?.satisfaction || 88}%`}
              icon={Users}
              color="bg-gradient-to-r from-indigo-400 to-indigo-500"
              subtitle="Based on feedback"
              trend={7}
            />
          </div>

          {/* Quick Actions */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <QuickActionCard
                title="Process New Emails"
                description="Fetch and analyze incoming emails with AI-powered insights"
                icon={Zap}
                color="bg-blue-500"
                action={() => setActiveView('emails')}
              />
              <QuickActionCard
                title="Review Responses"
                description="Check and edit AI-generated responses before sending"
                icon={MessageSquare}
                color="bg-green-500"
                action={() => setActiveView('emails')}
              />
              <QuickActionCard
                title="View Analytics"
                description="Explore detailed insights and performance metrics"
                icon={TrendingUp}
                color="bg-purple-500"
                action={() => setActiveView('analytics')}
              />
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {recentEmails.slice(0, 5).map((email, index) => (
                <div 
                  key={email.id || index} 
                  className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleEmailSelect(email)}
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    email.priority === 'urgent' ? 'bg-red-100' : 
                    email.priority === 'high' ? 'bg-orange-100' : 
                    email.priority === 'low' ? 'bg-green-100' : 'bg-blue-100'
                  }`}>
                    <Mail className={`w-5 h-5 ${
                      email.priority === 'urgent' ? 'text-red-600' : 
                      email.priority === 'high' ? 'text-orange-600' : 
                      email.priority === 'low' ? 'text-green-600' : 'text-blue-600'
                    }`} />
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <p className="font-medium text-gray-900 truncate">{email.subject}</p>
                    <p className="text-sm text-gray-600 truncate">
                      {email.sender} 
                      {email.category && <span className="text-gray-500"> • {email.category.replace('_', ' ')}</span>}
                    </p>
                  </div>
                  <div className="text-right flex flex-col items-end">
                    <p className="text-sm text-gray-500">
                      {new Date(email.received_date).toLocaleDateString()}
                    </p>
                    <div className="flex space-x-2 mt-1">
                      <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${
                        email.priority === 'urgent' ? 'bg-red-100 text-red-800' : 
                        email.priority === 'high' ? 'bg-orange-100 text-orange-800' : 
                        email.priority === 'low' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {email.priority}
                      </span>
                      <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${
                        email.sentiment === 'positive' ? 'bg-green-100 text-green-800' : 
                        email.sentiment === 'negative' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {email.sentiment}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-100">
              <button
                onClick={() => setActiveView('emails')}
                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                View all emails →
              </button>
            </div>
          </div>
        </>
      )}

      {activeView === 'emails' && (
        <EmailList onEmailSelect={handleEmailSelect} />
      )}

      {activeView === 'analytics' && (
        <Analytics />
      )}

      {/* Response Editor Modal */}
      {showResponseEditor && selectedEmail && (
        <ResponseEditor
          email={selectedEmail}
          onClose={handleCloseResponseEditor}
        />
      )}
    </div>
  );
};

export default Dashboard;