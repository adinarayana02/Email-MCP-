import React, { useState, useEffect } from 'react';
import { 
  X, 
  Send, 
  Edit3, 
  RefreshCw, 
  Copy, 
  Download, 
  Eye, 
  EyeOff,
  MessageSquare,
  Sparkles,
  Clock,
  User,
  Mail,
  Phone,
  Tag,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { emailAPI } from '../../services/api';
import { 
  getPriorityColor, 
  getSentimentColor, 
  copyToClipboard, 
  downloadFile,
  extractInitials,
  formatRelativeTime
} from '../../utils/helpers';

const ResponseEditor = ({ email, onClose }) => {
  const [responseText, setResponseText] = useState('');
  const [originalResponse, setOriginalResponse] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [tone, setTone] = useState('professional');
  const [responseType, setResponseType] = useState('reply');
  const [saving, setSaving] = useState(false);
  const [extractedInfo, setExtractedInfo] = useState({});
  const [templates, setTemplates] = useState([
    { id: 1, name: 'Technical Support', content: 'Thank you for contacting our technical support team. We understand you\'re experiencing issues with [ISSUE]. Our team is working to resolve this as quickly as possible.' },
    { id: 2, name: 'Billing Inquiry', content: 'Thank you for your billing inquiry. We\'ve reviewed your account and can confirm that [DETAILS]. If you have any further questions, please let us know.' },
    { id: 3, name: 'Feature Request', content: 'Thank you for your feature suggestion. We appreciate your input and have forwarded this to our product team for consideration in future updates.' },
    { id: 4, name: 'General Inquiry', content: 'Thank you for reaching out. We\'re happy to assist with your inquiry about [TOPIC]. Here\'s the information you requested: [INFORMATION].' }
  ]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {
    if (email) {
      loadEmailData();
    }
  }, [email]);

  const loadEmailData = async () => {
    try {
      // Load email details and any existing response
      if (email.generated_response) {
        setResponseText(email.generated_response);
        setOriginalResponse(email.generated_response);
      }
      
      // Extract contact information and other details
      const info = extractContactInfo(email.body || '');
      setExtractedInfo(info);
    } catch (error) {
      console.error('Failed to load email data:', error);
    }
  };

  const extractContactInfo = (body) => {
    const phoneRegex = /(\+?[\d\s\-\(\)]{10,})/g;
    const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    const nameRegex = /(?:from|by|sent by|regards|sincerely|best regards|yours truly)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/gi;
    
    const phones = body.match(phoneRegex) || [];
    const emails = body.match(emailRegex) || [];
    const names = body.match(nameRegex) || [];
    
    return {
      phones: [...new Set(phones)],
      emails: [...new Set(emails)],
      names: [...new Set(names)].map(name => name.replace(/^(?:from|by|sent by|regards|sincerely|best regards|yours truly)[:\s]+/i, ''))
    };
  };

  const generateAIResponse = async () => {
    try {
      setIsGenerating(true);
      
      // Simulate AI response generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const aiResponse = generateContextualResponse(email, tone);
      setResponseText(aiResponse);
      setOriginalResponse(aiResponse);
      setIsEditing(true);
    } catch (error) {
      console.error('Failed to generate AI response:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateContextualResponse = (email, tone) => {
    const baseResponse = `Dear ${email.sender?.split('@')[0] || 'Valued Customer'},

Thank you for reaching out to us regarding "${email.subject}".

${getToneSpecificText(tone)}

${getContextualResponse(email)}

If you have any further questions or need additional assistance, please don't hesitate to contact us.

Best regards,
Your Support Team`;

    return baseResponse;
  };

  const getToneSpecificText = (tone) => {
    switch (tone) {
      case 'friendly':
        return "We're here to help and appreciate you taking the time to contact us.";
      case 'empathetic':
        return "We understand how frustrating this situation must be, and we're committed to resolving it for you.";
      case 'professional':
        return "We appreciate your inquiry and are committed to providing you with the best possible assistance.";
      case 'formal':
        return "We acknowledge receipt of your communication and are processing your request accordingly.";
      default:
        return "We appreciate your inquiry and are here to assist you.";
    }
  };

  const getContextualResponse = (email) => {
    if (email.category === 'technical_support') {
      return "Our technical team has been notified of your issue and will investigate this matter promptly. We typically resolve technical issues within 24-48 hours.";
    } else if (email.category === 'billing') {
      return "We're reviewing your billing inquiry and will provide a detailed response within 1-2 business days. If this is urgent, please let us know.";
    } else if (email.category === 'complaint') {
      return "We sincerely apologize for the inconvenience you've experienced. Your feedback is important to us, and we're taking immediate steps to address your concerns.";
    } else {
      return "We're currently reviewing your request and will provide you with a comprehensive response as soon as possible.";
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Save the response
      await emailAPI.updateResponse(email.id, responseText);
      
      // Close the editor
      onClose();
    } catch (error) {
      console.error('Failed to save response:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleSend = async () => {
    try {
      setSaving(true);
      
      // Send the response
      await emailAPI.sendResponse(email.id, responseText);
      
      // Close the editor
      onClose();
    } catch (error) {
      console.error('Failed to send response:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleCopyToClipboard = async () => {
    try {
      await copyToClipboard(responseText);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleDownloadResponse = () => {
    downloadFile(responseText, `response_${email.id}.txt`, 'text/plain');
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

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-100';
      case 'negative':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (!email) return null;

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setResponseText(template.content);
    setIsEditing(true);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Response Editor</h2>
              <p className="text-sm text-gray-600">Compose and edit your response</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              className={`px-3 py-1 rounded ${isEditing ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}
              onClick={() => setIsEditing(!isEditing)}
            >
              <Edit3 className="h-4 w-4 inline mr-1" /> {isEditing ? 'Editing' : 'Edit'}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Left Panel - Email Details */}
          <div className="w-1/3 border-r border-gray-200 p-6 overflow-y-auto">
            <div className="space-y-6">
              {/* Email Header */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Original Email</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">{email.sender}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-700">{email.subject}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-500">{email.received_at}</span>
                  </div>
                </div>
              </div>

              {/* Email Content */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Content</h4>
                <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700 max-h-32 overflow-y-auto">
                  {email.body}
                </div>
              </div>

              {/* AI Analysis */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">AI Analysis</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Priority:</span>
                    <div className="flex items-center space-x-2">
                      {getPriorityIcon(email.priority)}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(email.priority)}`}>
                        {email.priority}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Sentiment:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(email.sentiment)}`}>
                      {email.sentiment}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Category:</span>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {email.category?.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Extracted Information */}
              {Object.keys(extractedInfo).length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Extracted Information</h4>
                  <div className="space-y-2">
                    {extractedInfo.phones?.length > 0 && (
                      <div className="flex items-center space-x-2">
                        <Phone className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-700">{extractedInfo.phones[0]}</span>
                      </div>
                    )}
                    {extractedInfo.emails?.length > 0 && (
                      <div className="flex items-center space-x-2">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-700">{extractedInfo.emails[0]}</span>
                      </div>
                    )}
                    {extractedInfo.names?.length > 0 && (
                      <div className="flex items-center space-x-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-700">{extractedInfo.names[0]}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Response Editor */}
          <div className="flex-1 p-6 flex flex-col">
            {/* Response Controls */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="empathetic">Empathetic</option>
                  <option value="formal">Formal</option>
                </select>
                <select
                  value={responseType}
                  onChange={(e) => setResponseType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="reply">Reply</option>
                  <option value="forward">Forward</option>
                  <option value="template">Template</option>
                </select>
                {responseType === 'template' && (
                  <select
                    value={selectedTemplate?.id || ''}
                    onChange={(e) => {
                      const template = templates.find(t => t.id === parseInt(e.target.value));
                      if (template) handleTemplateSelect(template);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select template...</option>
                    {templates.map(template => (
                      <option key={template.id} value={template.id}>{template.name}</option>
                    ))}
                  </select>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  <span>{showPreview ? 'Hide Preview' : 'Show Preview'}</span>
                </button>
                <button
                  onClick={handleCopyToClipboard}
                  className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Copy className="w-4 h-4" />
                  <span>Copy</span>
                </button>
                <button
                  onClick={handleDownloadResponse}
                  className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>

            {/* AI Generation Button */}
            {!responseText && (
              <div className="mb-4">
                <button
                  onClick={generateAIResponse}
                  disabled={isGenerating}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50"
                >
                  {isGenerating ? (
                    <RefreshCw className="w-5 h-5 animate-spin" />
                  ) : (
                    <Sparkles className="w-5 h-5" />
                  )}
                  <span>{isGenerating ? 'AI is writing...' : 'Generate Smart Response'}</span>
                </button>
              </div>
            )}

            {/* Response Editor */}
            <div className="flex-1">
              {showPreview ? (
                <div className="bg-gray-50 rounded-lg p-4 h-full overflow-y-auto">
                  <h4 className="font-medium text-gray-900 mb-3">Preview</h4>
                  <div className="prose prose-sm max-w-none">
                    <div className="whitespace-pre-wrap text-gray-700">{responseText}</div>
                  </div>
                </div>
              ) : (
                <textarea
                  value={responseText}
                  onChange={(e) => setResponseText(e.target.value)}
                  placeholder="Start typing your response or generate one using AI..."
                  className="w-full h-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={20}
                />
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setResponseText(originalResponse)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Reset to Original
                </button>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Edit3 className="w-4 h-4 inline mr-2" />
                  {isEditing ? 'View Only' : 'Edit Mode'}
                </button>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSave}
                  disabled={saving || !responseText.trim()}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>{saving ? 'Saving...' : 'Save Draft'}</span>
                </button>
                <button
                  onClick={handleSend}
                  disabled={saving || !responseText.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>{saving ? 'Sending...' : 'Send Response'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponseEditor;
