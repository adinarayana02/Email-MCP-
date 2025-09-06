import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Email API endpoints
export const emailAPI = {
  // Get all emails with optional filtering
  getEmails: async (params = {}) => {
    const response = await api.get('/emails/', { params });
    return response.data;
  },

  // Get specific email by ID
  getEmail: async (emailId) => {
    // With CSV backend, we'll get the email from the list with filtering
    const response = await api.get('/emails/', { 
      params: { search: emailId }
    });
    return response.data.length > 0 ? response.data[0] : null;
  },

  // Get urgent emails
  getUrgentEmails: async () => {
    // Use the filter parameter to get urgent emails
    const response = await api.get('/emails/', { 
      params: { priority: 'urgent' }
    });
    return response.data;
  },

  // Get today's emails
  getTodayEmails: async () => {
    // Use the advanced fetch endpoint with days=1
    const response = await api.get('/emails/fetch/advanced', {
      params: { days: 1 }
    });
    return response.data;
  },

  // Get priority queue (urgent first)
  getPriorityQueue: async () => {
    // Use the filter parameter to get emails sorted by priority
    const response = await api.get('/emails/', {
      params: { sort_by: 'priority' }
    });
    return response.data;
  },

  // Generate and send response to email
  sendResponse: async (emailId, responseText = null) => {
    // Use the context-aware response endpoint
    const response = await api.post(`/emails/${emailId}/generate-context-aware-response`);
    return response.data;
  },

  // Update email (including response)
  updateResponse: async (emailId, responseText) => {
    const response = await api.put(`/emails/${emailId}`, {
      response: responseText,
      status: 'responded'
    });
    return response.data;
  },

  // Update email status or other fields
  updateEmail: async (emailId, updateData) => {
    const response = await api.put(`/emails/${emailId}`, updateData);
    return response.data;
  },

  // Bulk update emails
  bulkUpdateEmails: async (updates) => {
    const response = await api.post('/emails/bulk-update', { updates });
    return response.data;
  },

  // Refresh emails from CSV
  refreshEmails: async () => {
    const response = await api.get('/emails/fetch');
    return response.data;
  }
};

// Analytics API endpoints
export const analyticsAPI = {
  // Get dashboard statistics
  getDashboardStats: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },

  // Get sentiment analysis
  getSentimentAnalysis: async (days = 7) => {
    const response = await api.get('/analytics/sentiment-analysis', { 
      params: { days } 
    });
    return response.data;
  },

  // Get priority analysis
  getPriorityAnalysis: async () => {
    const response = await api.get('/analytics/priority-analysis');
    return response.data;
  },

  // Get category breakdown - use dashboard data
  getCategoryBreakdown: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data.category_distribution;
  },

  // Get performance metrics - use dashboard data
  getPerformanceMetrics: async () => {
    const response = await api.get('/analytics/dashboard');
    return {
      total_emails: response.data.total_emails,
      response_rate: response.data.response_rate,
      avg_response_time: response.data.avg_response_time
    };
  },

  // Get historical analytics - use dashboard data
  getHistoricalAnalytics: async (days = 30) => {
    const response = await api.get('/analytics/dashboard');
    return {
      daily_volume: response.data.daily_volume,
      sentiment_trend: response.data.sentiment_trend
    };
  },

  // Get category analysis - use dashboard data
  getCategoryAnalysis: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data.category_distribution;
  },

  // Get time series data - use dashboard data
  getTimeSeriesData: async (timeRange = '30') => {
    const response = await api.get('/analytics/dashboard');
    return response.data.daily_volume;
  },

  // Get response time metrics - use dashboard data
  getResponseTimeMetrics: async () => {
    const response = await api.get('/analytics/dashboard');
    return {
      avg_response_time: response.data.avg_response_time,
      response_time_distribution: response.data.response_time_distribution || []
    };
  },

  // Get email volume - use dashboard data
  getEmailVolume: async () => {
    const response = await api.get('/analytics/dashboard');
    return {
      total_emails: response.data.total_emails,
      daily_volume: response.data.daily_volume
    };
  },

  // Get top keywords - simplified version using dashboard data
  getTopKeywords: async (limit = 10) => {
    const response = await api.get('/analytics/dashboard');
    return response.data.top_keywords || [];
  },

  // Get email distribution - use dashboard data
  getEmailDistribution: async (type = 'hourly') => {
    const response = await api.get('/analytics/dashboard');
    return type === 'hourly' ? 
      response.data.hourly_distribution || [] : 
      response.data.daily_volume || [];
  }
};

// Email extraction API
export const extractionAPI = {
  // Extract information from a specific email
  extractEmailInfo: async (emailId) => {
    try {
      const response = await api.get(`/emails/${emailId}/extract-info`);
      return response.data;
    } catch (error) {
      console.error('Error extracting email information:', error);
      throw error;
    }
  },
  
  // Batch extract information from multiple emails
  batchExtractEmails: async (emailIds) => {
    try {
      const response = await api.post(`/emails/batch-extract`, { email_ids: emailIds });
      return response.data;
    } catch (error) {
      console.error('Error batch extracting email information:', error);
      throw error;
    }
  },

  // Generate context-aware response for an email
  generateContextAwareResponse: async (emailId) => {
    try {
      const response = await api.post(`/emails/${emailId}/generate-context-aware-response`);
      return response.data;
    } catch (error) {
      console.error('Error generating context-aware response:', error);
      throw error;
    }
  }
};

// System API endpoints
export const systemAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Trigger manual email processing
  processEmails: async () => {
    const response = await api.post('/process-emails');
    return response.data;
  },

  // System status
  getSystemStatus: async () => {
    const response = await api.get('/system/status');
    return response.data;
  }
};

// Utility functions
export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};

export const formatRelativeTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
  return `${Math.ceil(diffDays / 30)} months ago`;
};

export const getSentimentColor = (sentiment) => {
  const colors = {
    positive: 'text-green-600 bg-green-100',
    negative: 'text-red-600 bg-red-100',
    neutral: 'text-gray-600 bg-gray-100'
  };
  return colors[sentiment] || colors.neutral;
};

export const getPriorityColor = (priority) => {
  const colors = {
    urgent: 'text-red-600 bg-red-100',
    normal: 'text-blue-600 bg-blue-100'
  };
  return colors[priority] || colors.normal;
};

export const getCategoryColor = (category) => {
  const colors = {
    'technical_support': 'text-purple-600 bg-purple-100',
    'billing': 'text-green-600 bg-green-100',
    'complaint': 'text-red-600 bg-red-100',
    'general_inquiry': 'text-blue-600 bg-blue-100',
    'feature_request': 'text-indigo-600 bg-indigo-100',
    'account_management': 'text-yellow-600 bg-yellow-100'
  };
  return colors[category] || 'text-gray-600 bg-gray-100';
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'text-green-600';
  if (score >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
};

export const formatConfidence = (score) => {
  return `${Math.round(score * 100)}%`;
};

export default api;