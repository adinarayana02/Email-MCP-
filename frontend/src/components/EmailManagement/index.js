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
import LoadingSpinner from '../common/LoadingSpinner';
import { emailAPI, filterCSVData, sortCSVData } from '../../services/api';

const EmailManagement = () => {
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilters, setSelectedFilters] = useState({
    priority: 'all',
    sentiment: 'all',
    status: 'all',
    category: 'all',
    date: 'all'
  });
  
  const dateFilterOptions = [
    { value: 'all', label: 'All Dates' },
    { value: 'today', label: 'Today' },
    { value: 'yesterday', label: 'Yesterday' },
    { value: 'last7days', label: 'Last 7 Days' },
    { value: 'last30days', label: 'Last 30 Days' },
    { value: 'thisMonth', label: 'This Month' },
    { value: 'lastMonth', label: 'Last Month' }
  ];
  const [sortBy, setSortBy] = useState('sent_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState('list'); // list, grid, compact
  const [selectedEmails, setSelectedEmails] = useState([]);
  const [bulkActions, setBulkActions] = useState(false);
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
      // Try to fetch emails from the backend API
      try {
        const response = await emailAPI.getEmails();
        if (response && response.emails && response.emails.length > 0) {
          const processedEmails = response.emails.map((email, index) => ({
            ...email,
            id: email.id || index,
            priority: email.priority || getPriority(email.subject),
            sentiment: email.sentiment || getSentiment(email.body),
            status: email.status || 'pending',
            category: email.category || getCategory(email.subject, email.body)
          }));
          setEmails(processedEmails);
          return;
        }
      } catch (apiError) {
        console.error('Failed to load emails from API:', apiError);
      }
      
      // If API fails, use sample data
      const sampleEmails = getSampleEmails();
      setEmails(sampleEmails);
    } catch (error) {
      console.error('Failed to load emails:', error);
      setEmails([]);
    } finally {
      setLoading(false);
    }
  };

  const parseCSV = (csvText) => {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    return lines.slice(1).filter(line => line.trim()).map((line, index) => {
      const values = line.split(',');
      const email = {};
      
      headers.forEach((header, i) => {
        // Handle quoted values with commas inside
        if (values[i] && values[i].startsWith('"') && !values[i].endsWith('"')) {
          let value = values[i];
          let j = i + 1;
          while (j < values.length && !values[j].endsWith('"')) {
            value += ',' + values[j];
            j++;
          }
          if (j < values.length) {
            value += ',' + values[j];
          }
          email[header] = value.replace(/^"|"$/g, '');
        } else {
          email[header] = values[i] ? values[i].replace(/^"|"$/g, '') : '';
        }
      });
      
      // Add generated fields for display
      email.id = index;
      email.priority = getPriority(email.subject);
      email.sentiment = getSentiment(email.body);
      email.status = 'pending';
      email.category = getCategory(email.subject, email.body);
      
      return email;
    });
  };

  const getPriority = (subject) => {
    if (!subject) return 'medium';
    const lowerSubject = subject.toLowerCase();
    if (lowerSubject.includes('urgent') || lowerSubject.includes('critical') || lowerSubject.includes('immediate')) {
      return 'high';
    } else if (lowerSubject.includes('help') || lowerSubject.includes('support')) {
      return 'medium';
    } else {
      return 'low';
    }
  };

  const getSentiment = (body) => {
    if (!body) return 'neutral';
    const lowerBody = body.toLowerCase();
    if (lowerBody.includes('error') || lowerBody.includes('issue') || lowerBody.includes('problem') || 
        lowerBody.includes('cannot') || lowerBody.includes('failed')) {
      return 'negative';
    } else if (lowerBody.includes('thank') || lowerBody.includes('appreciate') || 
               lowerBody.includes('great') || lowerBody.includes('good')) {
      return 'positive';
    } else {
      return 'neutral';
    }
  };

  const getCategory = (subject, body) => {
    if (!subject && !body) return 'general';
    const lowerText = (subject + ' ' + body).toLowerCase();
    
    if (lowerText.includes('login') || lowerText.includes('password') || lowerText.includes('account')) {
      return 'account';
    } else if (lowerText.includes('billing') || lowerText.includes('payment') || lowerText.includes('charged') || 
               lowerText.includes('refund') || lowerText.includes('pricing')) {
      return 'billing';
    } else if (lowerText.includes('technical') || lowerText.includes('error') || 
               lowerText.includes('bug') || lowerText.includes('issue')) {
      return 'technical';
    } else if (lowerText.includes('feature') || lowerText.includes('enhancement') || 
               lowerText.includes('suggestion')) {
      return 'feature';
    } else {
      return 'general';
    }
  };

  const filterAndSortEmails = () => {
    // First, filter emails based on search query and selected filters
    let filtered = emails.filter(email => {
      // Search query filter (check in subject, body, and sender)
      const searchLower = searchQuery.toLowerCase();
      const matchesSearch = searchQuery === '' || 
        (email.subject && email.subject.toLowerCase().includes(searchLower)) ||
        (email.body && email.body.toLowerCase().includes(searchLower)) ||
        (email.sender && email.sender.toLowerCase().includes(searchLower));
      
      // Category filter
      const matchesCategory = selectedFilters.category === 'all' || 
        email.category === selectedFilters.category;
      
      // Priority filter
      const matchesPriority = selectedFilters.priority === 'all' || 
        email.priority === selectedFilters.priority;
      
      // Status filter
      const matchesStatus = selectedFilters.status === 'all' || 
        email.status === selectedFilters.status;
      
      // Sentiment filter
      const matchesSentiment = selectedFilters.sentiment === 'all' || 
        email.sentiment === selectedFilters.sentiment;
      
      // Date filter
      let matchesDate = true;
      if (selectedFilters.date !== 'all') {
        const emailDate = new Date(email.sent_date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        const last7Days = new Date(today);
        last7Days.setDate(last7Days.getDate() - 7);
        
        const last30Days = new Date(today);
        last30Days.setDate(last30Days.getDate() - 30);
        
        const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
        
        const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
        
        switch (selectedFilters.date) {
          case 'today':
            matchesDate = emailDate >= today;
            break;
          case 'yesterday':
            matchesDate = emailDate >= yesterday && emailDate < today;
            break;
          case 'last7days':
            matchesDate = emailDate >= last7Days;
            break;
          case 'last30days':
            matchesDate = emailDate >= last30Days;
            break;
          case 'thisMonth':
            matchesDate = emailDate >= thisMonthStart;
            break;
          case 'lastMonth':
            matchesDate = emailDate >= lastMonthStart && emailDate <= lastMonthEnd;
            break;
          default:
            matchesDate = true;
        }
      }
      
      return matchesSearch && matchesCategory && matchesPriority && matchesStatus && matchesSentiment && matchesDate;
    });
    
    // Then sort the filtered emails
    filtered.sort((a, b) => {
      let valueA = a[sortBy];
      let valueB = b[sortBy];
      
      // Handle date sorting
      if (sortBy === 'sent_date') {
        valueA = new Date(valueA);
        valueB = new Date(valueB);
      }
      
      // Handle string sorting
      if (typeof valueA === 'string') {
        valueA = valueA.toLowerCase();
      }
      if (typeof valueB === 'string') {
        valueB = valueB.toLowerCase();
      }
      
      // Compare values based on sort order
      if (valueA < valueB) return sortOrder === 'asc' ? -1 : 1;
      if (valueA > valueB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
    
    setFilteredEmails(filtered);
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
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

  const handleRefresh = () => {
    loadEmails();
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };

  const handleEmailSelect = (email) => {
    setSelectedEmail(email);
  };

  const handleEmailCheckboxChange = (emailId) => {
    setSelectedEmails(prev => {
      if (prev.includes(emailId)) {
        return prev.filter(id => id !== emailId);
      } else {
        return [...prev, emailId];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedEmails.length === filteredEmails.length) {
      setSelectedEmails([]);
    } else {
      setSelectedEmails(filteredEmails.map(email => email.id));
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return <span className="text-green-500">😊</span>;
      case 'negative': return <span className="text-red-500">😞</span>;
      case 'neutral': return <span className="text-gray-500">😐</span>;
      default: return <span className="text-gray-500">😐</span>;
    }
  };

  const renderEmailList = () => {
    if (loading) {
      return <div className="flex justify-center p-8"><LoadingSpinner /></div>;
    }

    if (filteredEmails.length === 0) {
      return (
        <div className="text-center p-8 text-gray-500">
          No emails found matching your criteria
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input 
                  type="checkbox" 
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  checked={selectedEmails.length === filteredEmails.length && filteredEmails.length > 0}
                  onChange={handleSelectAll}
                />
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSortChange('sender')}
              >
                Sender
                {sortBy === 'sender' && (
                  sortOrder === 'asc' ? <SortAsc className="inline ml-1 h-4 w-4" /> : <SortDesc className="inline ml-1 h-4 w-4" />
                )}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSortChange('subject')}
              >
                Subject
                {sortBy === 'subject' && (
                  sortOrder === 'asc' ? <SortAsc className="inline ml-1 h-4 w-4" /> : <SortDesc className="inline ml-1 h-4 w-4" />
                )}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSortChange('sent_date')}
              >
                Date
                {sortBy === 'sent_date' && (
                  sortOrder === 'asc' ? <SortAsc className="inline ml-1 h-4 w-4" /> : <SortDesc className="inline ml-1 h-4 w-4" />
                )}
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sentiment
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredEmails.map((email) => (
              <tr key={email.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <input 
                    type="checkbox" 
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    checked={selectedEmails.includes(email.id)}
                    onChange={() => handleEmailCheckboxChange(email.id)}
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{email.sender}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 truncate max-w-xs">{email.subject}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{new Date(email.sent_date).toLocaleString()}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(email.priority)} bg-opacity-10`}>
                    {email.priority}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {getSentimentIcon(email.sentiment)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {email.category}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button 
                    className="text-indigo-600 hover:text-indigo-900 mr-2"
                    onClick={() => handleEmailSelect(email)}
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="text-green-600 hover:text-green-900 mr-2">
                    <Reply className="h-4 w-4" />
                  </button>
                  <button className="text-red-600 hover:text-red-900">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderEmailDetail = () => {
    if (!selectedEmail) return null;

    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">Email Details</h2>
              <button 
                className="text-gray-500 hover:text-gray-700"
                onClick={() => setSelectedEmail(null)}
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">From:</div>
              <div className="text-md font-medium">{selectedEmail.sender}</div>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">Subject:</div>
              <div className="text-md font-medium">{selectedEmail.subject}</div>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">Date:</div>
              <div className="text-md">{new Date(selectedEmail.sent_date).toLocaleString()}</div>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">Priority:</div>
              <div className="text-md">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(selectedEmail.priority)} bg-opacity-10`}>
                  {selectedEmail.priority}
                </span>
              </div>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">Sentiment:</div>
              <div className="text-md">{getSentimentIcon(selectedEmail.sentiment)} {selectedEmail.sentiment}</div>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">Category:</div>
              <div className="text-md">{selectedEmail.category}</div>
            </div>
            
            <div className="mb-4">
              <div className="text-sm text-gray-500">Message:</div>
              <div className="text-md mt-2 p-4 bg-gray-50 rounded-lg whitespace-pre-wrap">{selectedEmail.body}</div>
            </div>
            
            <div className="flex justify-end space-x-2 mt-6">
              <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
                <Archive className="h-4 w-4 inline mr-1" /> Archive
              </button>
              <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                <Reply className="h-4 w-4 inline mr-1" /> Reply
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Sample emails for fallback when both CSV and API fail
  const getSampleEmails = () => {
    return [
      {
        id: 1,
        sender: 'alice@example.com',
        subject: 'Urgent request: system access blocked',
        body: 'Hi team, I am unable to log into my account since yesterday. Could you please help me resolve this issue?',
        sent_date: '2023-08-21 21:58:09',
        priority: 'high',
        sentiment: 'negative',
        status: 'pending',
        category: 'technical',
      },
      {
        id: 2,
        sender: 'bob@example.com',
        subject: 'Thank you for your excellent support',
        body: 'I just wanted to express my gratitude for the quick resolution of my issue. Your team is amazing!',
        sent_date: '2023-08-22 10:15:22',
        priority: 'low',
        sentiment: 'positive',
        status: 'resolved',
        category: 'general',
      },
      {
        id: 3,
        sender: 'carol@example.com',
        subject: 'Technical Support: API integration issue',
        body: 'We are experiencing problems with the API integration. The endpoints are returning 500 errors consistently.',
        sent_date: '2023-08-23 14:30:45',
        priority: 'medium',
        sentiment: 'negative',
        status: 'in_progress',
        category: 'technical',
      },
      {
        id: 4,
        sender: 'david@example.com',
        subject: 'Billing question about recent charge',
        body: 'I noticed an unexpected charge on my account. Could you please explain what this is for?',
        sent_date: '2023-08-24 09:22:18',
        priority: 'medium',
        sentiment: 'neutral',
        status: 'pending',
        category: 'billing',
      },
      {
        id: 5,
        sender: 'emma@example.com',
        subject: 'Positive feedback on new features',
        body: 'I love the new dashboard features you added! They have made my workflow much more efficient. Thank you!',
        sent_date: '2023-08-25 16:45:33',
        priority: 'low',
        sentiment: 'positive',
        status: 'closed',
        category: 'feature'
      },
      {
        id: 6,
        sender: 'frank@example.com',
        subject: 'Account access request',
        body: 'I need access to the admin dashboard for our team. Can you please set up the permissions?',
        sent_date: '2023-08-26 11:20:15',
        priority: 'medium',
        sentiment: 'neutral',
        status: 'pending',
        category: 'account'
      },
      {
        id: 7,
        sender: 'grace@example.com',
        subject: 'Technical Support needed for integration',
        body: 'We are trying to integrate your API with our system but facing some challenges. Can your technical team assist?',
        sent_date: '2023-08-27 13:40:22',
        priority: 'high',
        sentiment: 'neutral',
        status: 'pending',
        category: 'technical'
      },
      {
        id: 8,
        sender: 'henry@example.com',
        subject: 'Positive experience with customer service',
        body: 'I wanted to share my positive experience with your customer service team. They were very helpful and resolved my issue quickly.',
        sent_date: '2023-08-28 09:15:30',
        priority: 'low',
        sentiment: 'positive',
        status: 'closed',
        category: 'general'
      },
      {
        id: 2,
        sender: 'eve@startup.io',
        subject: 'Help required with account verification',
        body: 'Do you support integration with third-party APIs? Specifically, I\'m looking for CRM integration options.',
        sent_date: '2025-08-19 00:58:09',
        priority: 'medium',
        sentiment: 'neutral',
        status: 'pending',
        category: 'technical'
      },
      {
        id: 3,
        sender: 'diana@client.co',
        subject: 'General query about subscription',
        body: 'Hi team, I am unable to log into my account since yesterday. Could you please help me resolve this issue?',
        sent_date: '2025-08-25 00:58:09',
        priority: 'low',
        sentiment: 'negative',
        status: 'pending',
        category: 'account'
      },
      {
        id: 4,
        sender: 'eve@startup.io',
        subject: 'Immediate support needed for billing error',
        body: 'Hello, I wanted to understand the pricing tiers better. Could you share a detailed breakdown?',
        sent_date: '2025-08-20 12:58:09',
        priority: 'high',
        sentiment: 'neutral',
        status: 'pending',
        category: 'billing'
      },
      {
        id: 5,
        sender: 'charlie@partner.org',
        subject: 'Help required with account verification',
        body: 'This is urgent – our system is completely inaccessible, and this is affecting our operations.',
        sent_date: '2025-08-18 00:58:09',
        priority: 'high',
        sentiment: 'negative',
        status: 'pending',
        category: 'technical'
      }
    ];
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-4 sm:mb-0">Email Management</h1>
          
          <div className="flex space-x-2">
            <button 
              className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center"
              onClick={handleRefresh}
            >
              <RefreshCw className="h-4 w-4 mr-1" /> Refresh
            </button>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row justify-between mb-6 space-y-4 sm:space-y-0">
          <div className="relative">
            <input
              type="text"
              placeholder="Search emails..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full sm:w-80"
              value={searchQuery}
              onChange={handleSearch}
            />
            <Search className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
          </div>
          
          <div className="flex flex-wrap gap-2">
            <select 
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedFilters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
            >
              <option value="all">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            
            <select 
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedFilters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
            
            <select 
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedFilters.sentiment}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
            
            <select 
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedFilters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              <option value="all">All Categories</option>
              <option value="technical">Technical Support</option>
              <option value="account">Account</option>
              <option value="billing">Billing</option>
              <option value="feature">Feature</option>
              <option value="general">General</option>
            </select>
            
            <select 
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedFilters.date}
              onChange={(e) => handleFilterChange('date', e.target.value)}
            >
              {dateFilterOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
        
        {renderEmailList()}
        {renderEmailDetail()}
      </div>
    </div>
  );
};

export default EmailManagement;