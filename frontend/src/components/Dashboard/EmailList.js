import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc, 
  RefreshCw, 
  MoreVertical,
  Star,
  StarOff,
  Archive,
  Trash2,
  Eye,
  Reply,
  Clock,
  AlertTriangle,
  CheckCircle,
  Mail,
  FileSearch,
  X
} from 'lucide-react';
import EmailCard from './EmailCard';
import EmailExtractedInfo from './EmailExtractedInfo';
import LoadingSpinner from '../common/LoadingSpinner';
import { emailAPI, extractionAPI } from '../../services/api';

const EmailList = ({ onEmailSelect }) => {
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilters, setSelectedFilters] = useState({
    priority: 'all',
    sentiment: 'all',
    status: 'all',
    category: 'all'
  });
  const [sortBy, setSortBy] = useState('received_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState('list'); // list, grid, compact
  const [selectedEmails, setSelectedEmails] = useState([]);
  const [bulkActions, setBulkActions] = useState(false);
  const [extractedInfo, setExtractedInfo] = useState(null);
  const [extractingInfo, setExtractingInfo] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);

  useEffect(() => {
    loadEmails();
  }, []);

  useEffect(() => {
    filterAndSortEmails();
  }, [emails, searchQuery, selectedFilters, sortBy, sortOrder]);

  const loadEmails = async () => {
    try {
      setLoading(true);
      const response = await emailAPI.getEmails();
      setEmails(response.emails || []);
    } catch (error) {
      console.error('Failed to load emails:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortEmails = () => {
    let filtered = [...emails];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(email =>
        email.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.sender?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.body?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply category filters
    if (selectedFilters.priority !== 'all') {
      filtered = filtered.filter(email => email.priority === selectedFilters.priority);
    }
    if (selectedFilters.sentiment !== 'all') {
      filtered = filtered.filter(email => email.sentiment === selectedFilters.sentiment);
    }
    if (selectedFilters.status !== 'all') {
      filtered = filtered.filter(email => email.status === selectedFilters.status);
    }
    if (selectedFilters.category !== 'all') {
      filtered = filtered.filter(email => email.category === selectedFilters.category);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      if (sortBy === 'received_at') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredEmails(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSortChange = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const handleEmailSelection = (emailId, selected) => {
    if (selected) {
      setSelectedEmails(prev => [...prev, emailId]);
    } else {
      setSelectedEmails(prev => prev.filter(id => id !== emailId));
    }
  };

  const handleEmailSelect = (email, action) => {
    setSelectedEmail(email);
    
    if (action === 'extract') {
      handleExtractInfo(email);
    } else if (onEmailSelect) {
      onEmailSelect(email);
    }
  };
  
  const handleExtractInfo = async (email) => {
    try {
      setExtractingInfo(true);
      setExtractedInfo(null);
      
      const { extracted_info } = await extractionAPI.extractEmailInfo(email.id);
      setExtractedInfo(extracted_info);
    } catch (error) {
      console.error('Error extracting email information:', error);
      // Show error message
    } finally {
      setExtractingInfo(false);
    }
  };
  
  const closeExtractedInfo = () => {
    setExtractedInfo(null);
    setSelectedEmail(null);
  };

  const handleBulkAction = async (action) => {
    if (selectedEmails.length === 0) return;

    try {
      if (action === 'extract') {
        await handleBatchExtract();
      } else {
        // Implement bulk actions
        console.log(`Performing ${action} on ${selectedEmails.length} emails`);
        
        // Reload emails
        await loadEmails();
      }
      
      // Clear selection after action
      setSelectedEmails([]);
      setBulkActions(false);
    } catch (error) {
      console.error(`Bulk action failed:`, error);
    }
  };
  
  const handleBatchExtract = async () => {
    try {
      setExtractingInfo(true);
      setExtractedInfo(null);
      
      // Get the first selected email to display in the panel
      const firstEmailId = selectedEmails[0];
      const firstEmail = emails.find(email => email.id === firstEmailId);
      setSelectedEmail(firstEmail);
      
      // Batch extract information
      const result = await extractionAPI.batchExtractEmails(selectedEmails);
      
      // Show the first result in the panel
      if (result.results && result.results.length > 0) {
        const firstResult = result.results.find(r => r.status === 'success');
        if (firstResult) {
          setExtractedInfo(firstResult.extracted_info);
        }
      }
      
      // Show success message
      console.log(`Successfully extracted information from ${result.successful} out of ${result.total} emails`);
    } catch (error) {
      console.error('Error batch extracting email information:', error);
    } finally {
      setExtractingInfo(false);
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'urgent':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      default:
        return <Clock className="w-4 h-4 text-blue-500" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'resolved':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading emails..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email Management</h1>
          <p className="text-gray-600 mt-1">
            {filteredEmails.length} of {emails.length} emails
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadEmails}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search emails..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Priority Filter */}
          <div>
            <select
              value={selectedFilters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={selectedFilters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>

        {/* Additional Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {/* Sentiment Filter */}
          <div>
            <select
              value={selectedFilters.sentiment}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={selectedFilters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Categories</option>
              <option value="technical_support">Technical Support</option>
              <option value="billing">Billing</option>
              <option value="complaint">Complaint</option>
              <option value="general_inquiry">General Inquiry</option>
              <option value="feature_request">Feature Request</option>
            </select>
          </div>

          {/* View Mode */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">View:</span>
            <div className="flex bg-gray-100 rounded-lg p-1">
              {['list', 'grid', 'compact'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                    viewMode === mode
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Extracted Information Panel */}
      {(extractedInfo || extractingInfo) && selectedEmail && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6 relative">
          <div className="absolute top-4 right-4">
            <button 
              onClick={closeExtractedInfo}
              className="p-1 rounded-full bg-gray-200 hover:bg-gray-300 focus:outline-none"
            >
              <X className="w-4 h-4 text-gray-600" />
            </button>
          </div>
          
          <div className="flex items-center mb-4">
            <FileSearch className="w-5 h-5 text-blue-500 mr-2" />
            <h3 className="text-lg font-medium">Email Analysis</h3>
          </div>
          
          {extractingInfo ? (
            <div className="flex justify-center items-center py-8">
              <LoadingSpinner size="md" />
              <span className="ml-3 text-gray-600">Analyzing email content...</span>
            </div>
          ) : (
            <EmailExtractedInfo extractedInfo={extractedInfo} />
          )}
        </div>
      )}

      {/* Bulk Actions */}
      {selectedEmails.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-blue-900">
                {selectedEmails.length} email(s) selected
              </span>
              <div className="flex space-x-2">
                <button
                onClick={() => handleBulkAction('extract')}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                Extract Info
              </button>
              <button
                onClick={() => handleBulkAction('mark_resolved')}
                className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
              >
                Mark Resolved
              </button>
              <button
                onClick={() => handleBulkAction('archive')}
                className="px-3 py-1 bg-gray-600 text-white text-sm rounded-lg hover:bg-gray-700 transition-colors"
              >
                Archive
              </button>
              <button
                onClick={() => handleBulkAction('delete')}
                className="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
              </div>
            </div>
            <button
              onClick={() => setSelectedEmails([])}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}

      {/* Email List */}
      <div className="space-y-4">
        {filteredEmails.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No emails found</h3>
            <p className="text-gray-600">
              Try adjusting your search or filters to find what you're looking for.
            </p>
          </div>
        ) : (
          filteredEmails.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              onSelect={handleEmailSelect}
              onSelectionChange={(selected) => handleEmailSelection(email.id, selected)}
              isSelected={selectedEmails.includes(email.id)}
              viewMode={viewMode}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default EmailList;
