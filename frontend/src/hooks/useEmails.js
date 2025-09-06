import { useState, useEffect, useCallback, useMemo } from 'react';
import { emailAPI } from '../services/api';

const useEmails = () => {
  // State
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Filters and sorting
  const [filters, setFilters] = useState({
    search: '',
    priority: 'all',
    sentiment: 'all',
    status: 'all',
    category: 'all',
    dateRange: 'all'
  });
  
  const [sortBy, setSortBy] = useState('received_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState('list');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalEmails, setTotalEmails] = useState(0);
  
  // Selection
  const [selectedEmails, setSelectedEmails] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  
  // Cache
  const [emailCache, setEmailCache] = useState(new Map());
  const [lastFetch, setLastFetch] = useState(null);
  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  // Load emails from API
  const loadEmails = useCallback(async (forceRefresh = false) => {
    try {
      setError(null);
      
      // Check cache first
      const now = Date.now();
      if (!forceRefresh && lastFetch && (now - lastFetch) < CACHE_DURATION) {
        return;
      }
      
      setLoading(true);
      const response = await emailAPI.getEmails();
      const emailList = response.emails || [];
      
      setEmails(emailList);
      setTotalEmails(emailList.length);
      setLastFetch(now);
      
      // Update cache
      const newCache = new Map();
      emailList.forEach(email => newCache.set(email.id, email));
      setEmailCache(newCache);
      
    } catch (err) {
      setError(err.message || 'Failed to load emails');
      console.error('Error loading emails:', err);
    } finally {
      setLoading(false);
    }
  }, [lastFetch]);

  // Refresh emails
  const refreshEmails = useCallback(async () => {
    setRefreshing(true);
    await loadEmails(true);
    setRefreshing(false);
  }, [loadEmails]);

  // Apply filters and sorting
  const applyFiltersAndSorting = useCallback(() => {
    let filtered = [...emails];

    // Apply search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(email =>
        email.subject?.toLowerCase().includes(searchLower) ||
        email.sender?.toLowerCase().includes(searchLower) ||
        email.body?.toLowerCase().includes(searchLower)
      );
    }

    // Apply category filters
    if (filters.priority !== 'all') {
      filtered = filtered.filter(email => email.priority === filters.priority);
    }
    if (filters.sentiment !== 'all') {
      filtered = filtered.filter(email => email.sentiment === filters.sentiment);
    }
    if (filters.status !== 'all') {
      filtered = filtered.filter(email => email.status === filters.status);
    }
    if (filters.category !== 'all') {
      filtered = filtered.filter(email => email.category === filters.category);
    }

    // Apply date range filter
    if (filters.dateRange !== 'all') {
      const now = new Date();
      const emailDate = new Date();
      
      switch (filters.dateRange) {
        case 'today':
          filtered = filtered.filter(email => {
            emailDate.setTime(new Date(email.received_at).getTime());
            return emailDate.toDateString() === now.toDateString();
          });
          break;
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          filtered = filtered.filter(email => new Date(email.received_at) >= weekAgo);
          break;
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          filtered = filtered.filter(email => new Date(email.received_at) >= monthAgo);
          break;
        default:
          break;
      }
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
    setTotalEmails(filtered.length);
    setCurrentPage(1); // Reset to first page when filters change
  }, [emails, filters, sortBy, sortOrder]);

  // Update filters
  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Update sorting
  const updateSorting = useCallback((field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  }, [sortBy, sortOrder]);

  // Email selection
  const toggleEmailSelection = useCallback((emailId) => {
    setSelectedEmails(prev => {
      if (prev.includes(emailId)) {
        return prev.filter(id => id !== emailId);
      } else {
        return [...prev, emailId];
      }
    });
  }, []);

  const selectAllEmails = useCallback((checked) => {
    if (checked) {
      setSelectedEmails(filteredEmails.map(email => email.id));
      setSelectAll(true);
    } else {
      setSelectedEmails([]);
      setSelectAll(false);
    }
  }, [filteredEmails]);

  // Bulk operations
  const bulkUpdateStatus = useCallback(async (status) => {
    if (selectedEmails.length === 0) return;
    
    try {
      setLoading(true);
      // Implement bulk status update
      console.log(`Updating ${selectedEmails.length} emails to status: ${status}`);
      
      // Clear selection after operation
      setSelectedEmails([]);
      setSelectAll(false);
      
      // Refresh emails
      await refreshEmails();
    } catch (err) {
      setError(err.message || 'Failed to update emails');
    } finally {
      setLoading(false);
    }
  }, [selectedEmails, refreshEmails]);

  const bulkDelete = useCallback(async () => {
    if (selectedEmails.length === 0) return;
    
    try {
      setLoading(true);
      // Implement bulk delete
      console.log(`Deleting ${selectedEmails.length} emails`);
      
      // Clear selection after operation
      setSelectedEmails([]);
      setSelectAll(false);
      
      // Refresh emails
      await refreshEmails();
    } catch (err) {
      setError(err.message || 'Failed to delete emails');
    } finally {
      setLoading(false);
    }
  }, [selectedEmails, refreshEmails]);

  // Email operations
  const updateEmail = useCallback(async (emailId, updates) => {
    try {
      // Update local state first for optimistic UI
      setEmails(prev => prev.map(email => 
        email.id === emailId ? { ...email, ...updates } : email
      ));
      
      // Update cache
      setEmailCache(prev => {
        const newCache = new Map(prev);
        const email = newCache.get(emailId);
        if (email) {
          newCache.set(emailId, { ...email, ...updates });
        }
        return newCache;
      });
      
      // Call API
      await emailAPI.updateEmail(emailId, updates);
    } catch (err) {
      // Revert optimistic update on error
      await refreshEmails();
      throw err;
    }
  }, [refreshEmails]);

  const deleteEmail = useCallback(async (emailId) => {
    try {
      // Remove from local state
      setEmails(prev => prev.filter(email => email.id !== emailId));
      setFilteredEmails(prev => prev.filter(email => email.id !== emailId));
      
      // Remove from cache
      setEmailCache(prev => {
        const newCache = new Map(prev);
        newCache.delete(emailId);
        return newCache;
      });
      
      // Call API
      await emailAPI.deleteEmail(emailId);
    } catch (err) {
      // Revert on error
      await refreshEmails();
      throw err;
    }
  }, [refreshEmails]);

  // Pagination
  const paginatedEmails = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return filteredEmails.slice(startIndex, endIndex);
  }, [filteredEmails, currentPage, pageSize]);

  const totalPages = useMemo(() => 
    Math.ceil(totalEmails / pageSize), [totalEmails, pageSize]
  );

  const goToPage = useCallback((page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  }, [totalPages]);

  // Statistics
  const stats = useMemo(() => {
    const total = emails.length;
    const urgent = emails.filter(email => email.priority === 'urgent').length;
    const pending = emails.filter(email => email.status === 'pending').length;
    const resolved = emails.filter(email => email.status === 'resolved').length;
    const positive = emails.filter(email => email.sentiment === 'positive').length;
    const negative = emails.filter(email => email.sentiment === 'negative').length;
    const neutral = emails.filter(email => email.sentiment === 'neutral').length;

    return {
      total,
      urgent,
      pending,
      resolved,
      sentiment: { positive, negative, neutral },
      resolutionRate: total > 0 ? (resolved / total) * 100 : 0
    };
  }, [emails]);

  // Effects
  useEffect(() => {
    loadEmails();
  }, [loadEmails]);

  useEffect(() => {
    applyFiltersAndSorting();
  }, [applyFiltersAndSorting]);

  useEffect(() => {
    // Update select all state
    if (selectedEmails.length === 0) {
      setSelectAll(false);
    } else if (selectedEmails.length === filteredEmails.length) {
      setSelectAll(true);
    }
  }, [selectedEmails, filteredEmails]);

  // Return hook interface
  return {
    // Data
    emails: paginatedEmails,
    allEmails: emails,
    filteredEmails,
    totalEmails,
    stats,
    
    // State
    loading,
    refreshing,
    error,
    viewMode,
    
    // Filters and sorting
    filters,
    sortBy,
    sortOrder,
    updateFilters,
    updateSorting,
    
    // Pagination
    currentPage,
    pageSize,
    totalPages,
    goToPage,
    setPageSize,
    
    // Selection
    selectedEmails,
    selectAll,
    toggleEmailSelection,
    selectAllEmails,
    
    // Actions
    loadEmails,
    refreshEmails,
    updateEmail,
    deleteEmail,
    bulkUpdateStatus,
    bulkDelete,
    
    // Cache
    emailCache,
    getEmailById: (id) => emailCache.get(id)
  };
};

export default useEmails;
