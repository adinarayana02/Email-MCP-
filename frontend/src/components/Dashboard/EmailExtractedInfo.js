import React from 'react';
import { Calendar, Clock, Tag, Mail, Phone, Link, FileText, AlertTriangle, ThumbsUp, ThumbsDown } from 'lucide-react';

const EmailExtractedInfo = ({ extractedInfo }) => {
  if (!extractedInfo) {
    return (
      <div className="p-4 bg-gray-50 rounded-md">
        <p className="text-gray-500 text-sm">No extracted information available</p>
      </div>
    );
  }

  const {
    dates,
    emails,
    phone_numbers,
    urls,
    request_type,
    urgency_indicators,
    sentiment_indicators,
    urgency_level,
    sentiment,
    key_phrases
  } = extractedInfo;

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-500';
      case 'negative':
        return 'text-red-500';
      case 'neutral':
      default:
        return 'text-blue-500';
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'urgent':
        return 'text-red-500';
      case 'high':
        return 'text-orange-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
      default:
        return 'text-green-500';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'support':
        return 'bg-blue-100 text-blue-800';
      case 'billing':
        return 'bg-green-100 text-green-800';
      case 'technical':
        return 'bg-purple-100 text-purple-800';
      case 'feedback':
        return 'bg-yellow-100 text-yellow-800';
      case 'complaint':
        return 'bg-red-100 text-red-800';
      case 'inquiry':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <ThumbsUp className="w-4 h-4 text-green-500" />;
      case 'negative':
        return <ThumbsDown className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
      <h3 className="text-lg font-medium mb-3">Extracted Information</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Request Type */}
        <div className="flex items-start space-x-2">
          <Tag className="w-5 h-5 mt-0.5 text-gray-500" />
          <div>
            <p className="text-sm font-medium text-gray-700">Request Type</p>
            {request_type ? (
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(request_type)}`}>
                {request_type}
              </span>
            ) : (
              <p className="text-sm text-gray-500">Not detected</p>
            )}
          </div>
        </div>

        {/* Urgency Level */}
        <div className="flex items-start space-x-2">
          <AlertTriangle className={`w-5 h-5 mt-0.5 ${getUrgencyColor(urgency_level)}`} />
          <div>
            <p className="text-sm font-medium text-gray-700">Urgency Level</p>
            {urgency_level ? (
              <p className={`text-sm font-medium ${getUrgencyColor(urgency_level)}`}>
                {urgency_level.charAt(0).toUpperCase() + urgency_level.slice(1)}
              </p>
            ) : (
              <p className="text-sm text-gray-500">Not detected</p>
            )}
            {urgency_indicators && urgency_indicators.length > 0 && (
              <div className="mt-1">
                <p className="text-xs text-gray-500">Indicators:</p>
                <ul className="text-xs text-gray-600 list-disc list-inside">
                  {urgency_indicators.slice(0, 3).map((indicator, index) => (
                    <li key={index}>{indicator}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Sentiment */}
        <div className="flex items-start space-x-2">
          {getSentimentIcon(sentiment)}
          <div>
            <p className="text-sm font-medium text-gray-700">Sentiment</p>
            {sentiment ? (
              <p className={`text-sm font-medium ${getSentimentColor(sentiment)}`}>
                {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
              </p>
            ) : (
              <p className="text-sm text-gray-500">Not detected</p>
            )}
            {sentiment_indicators && sentiment_indicators.length > 0 && (
              <div className="mt-1">
                <p className="text-xs text-gray-500">Indicators:</p>
                <ul className="text-xs text-gray-600 list-disc list-inside">
                  {sentiment_indicators.slice(0, 3).map((indicator, index) => (
                    <li key={index}>{indicator}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Dates */}
        {dates && dates.length > 0 && (
          <div className="flex items-start space-x-2">
            <Calendar className="w-5 h-5 mt-0.5 text-gray-500" />
            <div>
              <p className="text-sm font-medium text-gray-700">Dates Mentioned</p>
              <ul className="text-sm text-gray-600">
                {dates.map((date, index) => (
                  <li key={index}>{date}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Contact Information */}
        <div className="col-span-1 md:col-span-2">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Contact Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Emails */}
            {emails && emails.length > 0 && (
              <div className="flex items-start space-x-2">
                <Mail className="w-5 h-5 mt-0.5 text-gray-500" />
                <div>
                  <p className="text-xs font-medium text-gray-600">Email Addresses</p>
                  <ul className="text-sm text-gray-600">
                    {emails.map((email, index) => (
                      <li key={index}>
                        <a href={`mailto:${email}`} className="text-blue-500 hover:underline">
                          {email}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Phone Numbers */}
            {phone_numbers && phone_numbers.length > 0 && (
              <div className="flex items-start space-x-2">
                <Phone className="w-5 h-5 mt-0.5 text-gray-500" />
                <div>
                  <p className="text-xs font-medium text-gray-600">Phone Numbers</p>
                  <ul className="text-sm text-gray-600">
                    {phone_numbers.map((phone, index) => (
                      <li key={index}>
                        <a href={`tel:${phone}`} className="text-blue-500 hover:underline">
                          {phone}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* URLs */}
            {urls && urls.length > 0 && (
              <div className="flex items-start space-x-2">
                <Link className="w-5 h-5 mt-0.5 text-gray-500" />
                <div>
                  <p className="text-xs font-medium text-gray-600">URLs</p>
                  <ul className="text-sm text-gray-600">
                    {urls.map((url, index) => (
                      <li key={index} className="truncate max-w-xs">
                        <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                          {url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Key Phrases */}
        {key_phrases && key_phrases.length > 0 && (
          <div className="col-span-1 md:col-span-2 flex items-start space-x-2">
            <FileText className="w-5 h-5 mt-0.5 text-gray-500" />
            <div>
              <p className="text-sm font-medium text-gray-700">Key Phrases</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {key_phrases.map((phrase, index) => (
                  <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {phrase}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailExtractedInfo;