import React, { useState } from 'react';
import { 
  User, 
  Clock, 
  MessageSquare, 
  Star, 
  StarOff, 
  Archive, 
  Trash2, 
  Eye,
  Reply,
  MoreVertical,
  AlertTriangle,
  CheckCircle,
  Tag,
  Phone,
  Mail as MailIcon
} from 'lucide-react';
import { formatRelativeTime, getSentimentColor, getPriorityColor, getCategoryColor } from '../../services/api';

const EmailCard = ({ 
  email, 
  onSelect, 
  onSelectionChange, 
  isSelected, 
  viewMode = 'list' 
}) => {
  const [showActions, setShowActions] = useState(false);
  const [isStarred, setIsStarred] = useState(email.is_starred || false);

  const handleStarToggle = (e) => {
    e.stopPropagation();
    setIsStarred(!isStarred);
  };

  const handleActionClick = (action, e) => {
    e.stopPropagation();
    setShowActions(false);
    
    switch (action) {
      case 'view':
        onSelect(email);
        break;
      case 'reply':
        onSelect(email);
        break;
      case 'archive':
        // Implement archive action
        console.log('Archive email:', email.id);
        break;
      case 'delete':
        // Implement delete action
        console.log('Delete email:', email.id);
        break;
      default:
        break;
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

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const extractContactInfo = (body) => {
    const phoneRegex = /(\+?[\d\s\-\(\)]{10,})/g;
    const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    
    const phones = body.match(phoneRegex) || [];
    const emails = body.match(emailRegex) || [];
    
    return { phones: [...new Set(phones)], emails: [...new Set(emails)] };
  };

  const contactInfo = extractContactInfo(email.body || '');

  if (viewMode === 'compact') {
    return (
      <div 
        className={`bg-white rounded-lg border border-gray-200 p-3 hover:shadow-md transition-all duration-200 cursor-pointer ${
          isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
        }`}
        onClick={() => onSelect(email)}
      >
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => onSelectionChange(e.target.checked)}
            onClick={(e) => e.stopPropagation()}
            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
          
          <div className="flex-shrink-0">
            {getPriorityIcon(email.priority)}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {email.subject}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {email.sender}
            </p>
          </div>
          
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <span>{formatRelativeTime(email.received_at)}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(email.priority)}`}>
              {email.priority}
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (viewMode === 'grid') {
    return (
      <div 
        className={`bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-all duration-200 cursor-pointer ${
          isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
        }`}
        onClick={() => onSelect(email)}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => onSelectionChange(e.target.checked)}
              onClick={(e) => e.stopPropagation()}
              className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-blue-600">
                {getInitials(email.sender)}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={handleStarToggle}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              {isStarred ? (
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
              ) : (
                <StarOff className="w-4 h-4 text-gray-400" />
              )}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowActions(!showActions);
              }}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              <MoreVertical className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <p className="font-medium text-gray-900 line-clamp-2">
            {email.subject}
          </p>
          <p className="text-sm text-gray-600 line-clamp-3">
            {email.body}
          </p>
          
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(email.priority)}`}>
                {email.priority}
              </span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(email.sentiment)}`}>
                {email.sentiment}
              </span>
            </div>
            <span className="text-xs text-gray-500">
              {formatRelativeTime(email.received_at)}
            </span>
          </div>
        </div>

        {/* Actions Dropdown */}
        {showActions && (
          <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
            <div className="py-1">
              <button
                onClick={(e) => handleActionClick('view', e)}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <Eye className="w-4 h-4 mr-2" />
                View Details
              </button>
              <button
                onClick={(e) => handleActionClick('reply', e)}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <Reply className="w-4 h-4 mr-2" />
                Reply
              </button>
              <button
                onClick={(e) => handleActionClick('archive', e)}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <Archive className="w-4 h-4 mr-2" />
                Archive
              </button>
              <button
                onClick={(e) => handleActionClick('delete', e)}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Default list view
  return (
    <div 
      className={`bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer relative ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
      }`}
      onClick={() => onSelect(email)}
    >
      <div className="flex items-start space-x-4">
        {/* Checkbox and Avatar */}
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => onSelectionChange(e.target.checked)}
            onClick={(e) => e.stopPropagation()}
            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
          
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-lg font-medium text-blue-600">
              {getInitials(email.sender)}
            </span>
          </div>
        </div>

        {/* Email Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-1">
                {email.subject}
              </h3>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span className="font-medium">{email.sender}</span>
                <span>•</span>
                <span>{formatRelativeTime(email.received_at)}</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={handleStarToggle}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {isStarred ? (
                  <Star className="w-5 h-5 text-yellow-500 fill-current" />
                ) : (
                  <StarOff className="w-5 h-5 text-gray-400" />
                )}
              </button>
              
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowActions(!showActions);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <MoreVertical className="w-5 h-5 text-gray-400" />
                </button>
                
                {/* Actions Dropdown */}
                {showActions && (
                  <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                    <div className="py-1">
                      <button
                        onClick={(e) => handleActionClick('view', e)}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </button>
                      <button
                        onClick={(e) => handleActionClick('reply', e)}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Reply className="w-4 h-4 mr-2" />
                        Reply
                      </button>
                      <button
                        onClick={(e) => handleActionClick('archive', e)}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Archive className="w-4 h-4 mr-2" />
                        Archive
                      </button>
                      <button
                        onClick={(e) => handleActionClick('delete', e)}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Email Body Preview */}
          <p className="text-gray-700 mb-4 line-clamp-2">
            {email.body}
          </p>

          {/* Tags and Metadata */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(email.priority)}`}>
                {getPriorityIcon(email.priority)}
                <span className="ml-1">{email.priority}</span>
              </span>
              
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSentimentColor(email.sentiment)}`}>
                {email.sentiment}
              </span>
              
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(email.category)}`}>
                <Tag className="w-3 h-3 inline mr-1" />
                {email.category?.replace('_', ' ')}
              </span>
              
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                {getStatusIcon(email.status)}
                <span className="ml-1">{email.status?.replace('_', ' ')}</span>
              </span>
            </div>

            {/* Contact Info */}
            {(contactInfo.phones.length > 0 || contactInfo.emails.length > 0) && (
              <div className="flex items-center space-x-3 text-xs text-gray-500">
                {contactInfo.phones.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <Phone className="w-3 h-3" />
                    <span>{contactInfo.phones[0]}</span>
                  </div>
                )}
                {contactInfo.emails.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <MailIcon className="w-3 h-3" />
                    <span>{contactInfo.emails[0]}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailCard;
