import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard/Dashboard';
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import EmailList from './components/Dashboard/EmailList';
import Analytics from './components/Dashboard/Analytics';
import ResponseEditor from './components/Dashboard/ResponseEditor';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { systemAPI } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState('checking');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [showResponseEditor, setShowResponseEditor] = useState(false);

  useEffect(() => {
    // Check system health on startup
    checkSystemHealth();
    
    // Set up periodic health checks
    const healthCheckInterval = setInterval(checkSystemHealth, 300000); // Every 5 minutes
    
    return () => clearInterval(healthCheckInterval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await systemAPI.healthCheck();
      setSystemStatus('healthy');
      console.log('System status:', health);
    } catch (error) {
      setSystemStatus('unhealthy');
      console.error('System health check failed:', error);
    }
  };

  const handleProcessEmails = async () => {
    try {
      const result = await systemAPI.processEmails();
      toast.success('Email processing triggered successfully!');
      console.log('Email processing result:', result);
    } catch (error) {
      toast.error('Failed to trigger email processing');
      console.error('Email processing error:', error);
    }
  };

  const handleSearch = () => {
    // Implement search functionality
    console.log('Searching for:', searchQuery);
  };

  const handleEmailSelect = (email) => {
    setSelectedEmail(email);
    setShowResponseEditor(true);
  };

  const handleCloseResponseEditor = () => {
    setShowResponseEditor(false);
    setSelectedEmail(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        systemStatus={systemStatus}
        onProcessEmails={handleProcessEmails}
        onSearch={handleSearch}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Content */}
        <main className={`flex-1 transition-all duration-300 ${
          sidebarOpen ? 'lg:ml-64' : 'ml-0'
        }`}>
          <div className="p-6">
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'emails' && <EmailList onEmailSelect={handleEmailSelect} />}
            {activeTab === 'analytics' && <Analytics />}
            {activeTab === 'responses' && <ResponseEditor />}
          </div>
        </main>
      </div>

      {/* Response Editor Modal */}
      {showResponseEditor && selectedEmail && (
        <ResponseEditor
          email={selectedEmail}
          onClose={handleCloseResponseEditor}
        />
      )}

      {/* Toast notifications */}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </div>
  );
}

export default App;