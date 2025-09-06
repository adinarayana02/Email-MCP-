// ============================================================================
// PREMIUM UTILITY FUNCTIONS FOR AI COMMUNICATION ASSISTANT
// ============================================================================

/**
 * DATE & TIME UTILITIES
 */
export const formatDate = (date, format = 'medium') => {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return 'Invalid Date';
  
  const now = new Date();
  const diffTime = Math.abs(now - d);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  switch (format) {
    case 'short':
      return d.toLocaleDateString();
    case 'medium':
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
      if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months ago`;
      return `${Math.ceil(diffDays / 365)} years ago`;
    case 'long':
      return d.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    case 'time':
      return d.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    case 'datetime':
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    default:
      return d.toLocaleDateString();
  }
};

export const formatRelativeTime = (date) => {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return 'Invalid Date';
  
  const now = new Date();
  const diffTime = Math.abs(now - d);
  const diffSeconds = Math.floor(diffTime / 1000);
  const diffMinutes = Math.floor(diffTime / (1000 * 60));
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffSeconds < 60) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.ceil(diffDays / 7)}w ago`;
  if (diffDays < 365) return `${Math.ceil(diffDays / 30)}mo ago`;
  return `${Math.ceil(diffDays / 365)}y ago`;
};

export const isToday = (date) => {
  if (!date) return false;
  const d = new Date(date);
  const today = new Date();
  return d.toDateString() === today.toDateString();
};

export const isThisWeek = (date) => {
  if (!date) return false;
  const d = new Date(date);
  const today = new Date();
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  return d >= weekAgo;
};

/**
 * TEXT PROCESSING UTILITIES
 */
export const truncateText = (text, maxLength = 100, suffix = '...') => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + suffix;
};

export const capitalizeFirst = (text) => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const capitalizeWords = (text) => {
  if (!text) return '';
  return text.split(' ')
    .map(word => capitalizeFirst(word))
    .join(' ');
};

export const extractInitials = (name, maxLength = 2) => {
  if (!name) return '?';
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, maxLength);
};

export const cleanText = (text) => {
  if (!text) return '';
  return text
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s\-.,!?]/g, '')
    .trim();
};

export const wordCount = (text) => {
  if (!text) return 0;
  return text.trim().split(/\s+/).length;
};

export const readingTime = (text, wordsPerMinute = 200) => {
  const words = wordCount(text);
  const minutes = Math.ceil(words / wordsPerMinute);
  return minutes;
};

/**
 * EMAIL & CONTACT UTILITIES
 */
export const extractEmail = (text) => {
  if (!text) return null;
  const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
  const matches = text.match(emailRegex);
  return matches ? matches[0] : null;
};

export const extractPhone = (text) => {
  if (!text) return null;
  const phoneRegex = /(\+?[\d\s\-\(\)]{10,})/g;
  const matches = text.match(phoneRegex);
  return matches ? matches[0].replace(/\s+/g, '') : null;
};

export const validateEmail = (email) => {
  if (!email) return false;
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone) => {
  if (!phone) return false;
  const cleanPhone = phone.replace(/\s+/g, '');
  return cleanPhone.length >= 10 && /^\d+$/.test(cleanPhone);
};

export const formatPhone = (phone) => {
  if (!phone) return '';
  const cleanPhone = phone.replace(/\D/g, '');
  if (cleanPhone.length === 10) {
    return `(${cleanPhone.slice(0, 3)}) ${cleanPhone.slice(3, 6)}-${cleanPhone.slice(6)}`;
  }
  if (cleanPhone.length === 11 && cleanPhone[0] === '1') {
    return `+1 (${cleanPhone.slice(1, 4)}) ${cleanPhone.slice(4, 7)}-${cleanPhone.slice(7)}`;
  }
  return phone;
};

/**
 * COLOR & STYLING UTILITIES
 */
export const getPriorityColor = (priority) => {
  const colors = {
    urgent: 'text-red-600 bg-red-100 border-red-200',
    high: 'text-orange-600 bg-orange-100 border-orange-200',
    normal: 'text-blue-600 bg-blue-100 border-blue-200',
    low: 'text-gray-600 bg-gray-100 border-gray-200'
  };
  return colors[priority] || colors.normal;
};

export const getSentimentColor = (sentiment) => {
  const colors = {
    positive: 'text-green-600 bg-green-100 border-green-200',
    negative: 'text-red-600 bg-red-100 border-red-200',
    neutral: 'text-gray-600 bg-gray-100 border-gray-200'
  };
  return colors[sentiment] || colors.neutral;
};

export const getStatusColor = (status) => {
  const colors = {
    pending: 'text-yellow-600 bg-yellow-100 border-yellow-200',
    in_progress: 'text-blue-600 bg-blue-100 border-blue-200',
    resolved: 'text-green-600 bg-green-100 border-green-200',
    closed: 'text-gray-600 bg-gray-100 border-gray-200'
  };
  return colors[status] || colors.pending;
};

export const getCategoryColor = (category) => {
  const colors = {
    technical_support: 'text-purple-600 bg-purple-100 border-purple-200',
    billing: 'text-green-600 bg-green-100 border-green-200',
    complaint: 'text-red-600 bg-red-100 border-red-200',
    general_inquiry: 'text-blue-600 bg-blue-100 border-blue-200',
    feature_request: 'text-indigo-600 bg-indigo-100 border-indigo-200',
    account_management: 'text-yellow-600 bg-yellow-100 border-yellow-200'
  };
  return colors[category] || 'text-gray-600 bg-gray-100 border-gray-200';
};

/**
 * ARRAY & OBJECT UTILITIES
 */
export const groupBy = (array, key) => {
  if (!Array.isArray(array)) return {};
  return array.reduce((groups, item) => {
    const group = item[key];
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {});
};

export const sortBy = (array, key, order = 'asc') => {
  if (!Array.isArray(array)) return [];
  return [...array].sort((a, b) => {
    let aVal = a[key];
    let bVal = b[key];
    
    if (typeof aVal === 'string') aVal = aVal.toLowerCase();
    if (typeof bVal === 'string') bVal = bVal.toLowerCase();
    
    if (order === 'desc') {
      return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
    }
    return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
  });
};

export const unique = (array, key = null) => {
  if (!Array.isArray(array)) return [];
  if (key) {
    const seen = new Set();
    return array.filter(item => {
      const value = item[key];
      if (seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }
  return [...new Set(array)];
};

export const chunk = (array, size) => {
  if (!Array.isArray(array)) return [];
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

/**
 * STRING & FORMATTING UTILITIES
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatNumber = (num, options = {}) => {
  const defaults = {
    decimals: 2,
    thousandsSeparator: ',',
    decimalSeparator: '.'
  };
  const opts = { ...defaults, ...options };
  
  if (typeof num !== 'number') return '0';
  
  const parts = num.toFixed(opts.decimals).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, opts.thousandsSeparator);
  
  return parts.join(opts.decimalSeparator);
};

export const formatPercentage = (value, total, decimals = 1) => {
  if (!total || total === 0) return '0%';
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(decimals)}%`;
};

/**
 * VALIDATION UTILITIES
 */
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

export const isNotEmpty = (value) => !isEmpty(value);

export const isValidUrl = (string) => {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
};

export const isNumeric = (value) => {
  return !isNaN(parseFloat(value)) && isFinite(value);
};

/**
 * PERFORMANCE & UTILITY FUNCTIONS
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const retry = async (fn, retries = 3, delay = 1000) => {
  try {
    return await fn();
  } catch (error) {
    if (retries === 0) throw error;
    await sleep(delay);
    return retry(fn, retries - 1, delay * 2);
  }
};

/**
 * DOM & BROWSER UTILITIES
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return true;
  }
};

export const downloadFile = (content, filename, type = 'text/plain') => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

export const scrollToTop = (behavior = 'smooth') => {
  window.scrollTo({
    top: 0,
    behavior
  });
};

export const scrollToElement = (elementId, offset = 0, behavior = 'smooth') => {
  const element = document.getElementById(elementId);
  if (element) {
    const elementPosition = element.offsetTop - offset;
    window.scrollTo({
      top: elementPosition,
      behavior
    });
  }
};

/**
 * EXPORT ALL UTILITIES
 */
export default {
  // Date & Time
  formatDate,
  formatRelativeTime,
  isToday,
  isThisWeek,
  
  // Text Processing
  truncateText,
  capitalizeFirst,
  capitalizeWords,
  extractInitials,
  cleanText,
  wordCount,
  readingTime,
  
  // Email & Contact
  extractEmail,
  extractPhone,
  validateEmail,
  validatePhone,
  formatPhone,
  
  // Colors & Styling
  getPriorityColor,
  getSentimentColor,
  getStatusColor,
  getCategoryColor,
  
  // Array & Object
  groupBy,
  sortBy,
  unique,
  chunk,
  
  // String & Formatting
  formatFileSize,
  formatNumber,
  formatPercentage,
  
  // Validation
  isEmpty,
  isNotEmpty,
  isValidUrl,
  isNumeric,
  
  // Performance
  debounce,
  throttle,
  sleep,
  retry,
  
  // DOM & Browser
  copyToClipboard,
  downloadFile,
  scrollToTop,
  scrollToElement
};
