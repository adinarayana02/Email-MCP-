import React, { useEffect, useState } from 'react';
import {
  Mail, 
  BarChart3, 
  Settings, 
  Users, 
  FileText, 
  Archive,
  Clock,
  CheckCircle,
  AlertTriangle,
  MessageSquare,
  X
} from 'lucide-react';
import { emailAPI } from '../../services/api';

const Sidebar = ({ isOpen, activeTab, onTabChange, onClose }) => {
  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: BarChart3,
      description: 'Overview and analytics'
    },
    {
      id: 'emails',
      label: 'Email Management',
      icon: Mail,
      description: 'View and manage emails'
    },
    {
      id: 'responses',
      label: 'Response Editor',
      icon: MessageSquare,
      description: 'Edit and send responses'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      description: 'Detailed insights and reports'
    },
    {
      id: 'templates',
      label: 'Templates',
      icon: FileText,
      description: 'Response templates'
    },
    {
      id: 'users',
      label: 'Team Management',
      icon: Users,
      description: 'Manage team members'
    },
    {
      id: 'archive',
      label: 'Archive',
      icon: Archive,
      description: 'Archived emails'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      description: 'Application configuration'
    }
  ];

  const [quickStats, setQuickStats] = useState([
    { label: 'Pending', count: 0, icon: Clock, color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { label: 'In Progress', count: 0, icon: AlertTriangle, color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { label: 'Resolved', count: 0, icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' }
  ]);
  const [urgentCount, setUrgentCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await emailAPI.getEmails();
        const emails = res.emails || [];
        setTotalCount(emails.length);
        const pending = emails.filter(e => (e.status || 'pending') === 'pending').length;
        const inProgress = emails.filter(e => e.status === 'in_progress').length;
        const resolved = emails.filter(e => e.status === 'resolved').length;
        const urgent = emails.filter(e => e.priority === 'urgent').length;
        setUrgentCount(urgent);
        setQuickStats([
          { label: 'Pending', count: pending, icon: Clock, color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
          { label: 'In Progress', count: inProgress, icon: AlertTriangle, color: 'text-blue-600', bgColor: 'bg-blue-100' },
          { label: 'Resolved', count: resolved, icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' }
        ]);
      } catch (e) {
        // keep defaults on failure
      }
    };
    load();
  }, []);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-72 bg-white shadow-lg border-r border-gray-200 h-screen overflow-y-auto transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}>
        <div className="p-6">
          {/* Mobile close button */}
          <div className="flex items-center justify-between mb-6 lg:hidden">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-md">
                <Mail className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">EmailAI Assistant</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Menu */}

          {/* Navigation Menu */}
          <nav className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onTabChange(item.id);
                    // Close sidebar on mobile after selection
                    if (window.innerWidth < 1024) {
                      onClose();
                    }
                  }}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${
                    isActive ? 'text-blue-600' : 'text-gray-400'
                  }`} />
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${
                      isActive ? 'text-blue-700' : 'text-gray-900'
                    }`}>
                      {item.label}
                    </p>
                    <p className={`text-xs ${
                      isActive ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {item.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </nav>

          {/* Recent Activity */}
          <div className="mt-8">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Recent Activity</h3>
            <div className="space-y-2">
              <div className="text-xs text-gray-500">
                <p>• Email processed 2 min ago</p>
                <p>• Response sent 5 min ago</p>
                <p>• Priority updated 10 min ago</p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
