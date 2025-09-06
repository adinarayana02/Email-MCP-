import React, { useState, useEffect } from 'react';
import { Search, Filter, RefreshCw, Plus, UserPlus, Mail, Phone, BarChart } from 'lucide-react';

const LoadingSpinner = ({ size = "md", text = "Loading..." }) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
    xl: "w-12 h-12"
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`animate-spin rounded-full border-t-2 border-b-2 border-blue-500 ${sizeClasses[size]}`}></div>
      {text && <p className="mt-2 text-gray-600">{text}</p>}
    </div>
  );
};

export const TeamManagement = () => {
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filterRole, setFilterRole] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [currentMember, setCurrentMember] = useState(null);

  useEffect(() => {
    // Simulate API call
    const fetchTeamMembers = async () => {
      setLoading(true);
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data
        const mockTeamMembers = [
          {
            id: 1,
            name: 'John Doe',
            email: 'john.doe@example.com',
            role: 'Support Agent',
            status: 'Active',
            phone: '+1 (555) 123-4567',
            performance: {
              responseTime: '1.5h',
              resolutionRate: '92%',
              customerSatisfaction: '4.8/5',
              ticketsHandled: 145
            }
          },
          {
            id: 2,
            name: 'Jane Smith',
            email: 'jane.smith@example.com',
            role: 'Support Manager',
            status: 'Active',
            phone: '+1 (555) 987-6543',
            performance: {
              responseTime: '1.2h',
              resolutionRate: '95%',
              customerSatisfaction: '4.9/5',
              ticketsHandled: 112
            }
          },
          {
            id: 3,
            name: 'Robert Johnson',
            email: 'robert.johnson@example.com',
            role: 'Support Agent',
            status: 'On Leave',
            phone: '+1 (555) 456-7890',
            performance: {
              responseTime: '1.8h',
              resolutionRate: '88%',
              customerSatisfaction: '4.6/5',
              ticketsHandled: 98
            }
          }
        ];
        
        setTeamMembers(mockTeamMembers);
      } catch (error) {
        console.error('Error fetching team members:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamMembers();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  const resetFilters = () => {
    setFilterRole('');
    setFilterStatus('');
  };

  const openAddMemberModal = () => {
    setCurrentMember(null);
    setShowModal(true);
  };

  const openEditMemberModal = (member) => {
    setCurrentMember(member);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setCurrentMember(null);
  };

  const handleSaveMember = (memberData) => {
    if (currentMember) {
      // Edit existing member
      setTeamMembers(teamMembers.map(member => 
        member.id === currentMember.id ? { ...member, ...memberData } : member
      ));
    } else {
      // Add new member
      const newMember = {
        id: Date.now(),
        ...memberData,
        performance: {
          responseTime: '0h',
          resolutionRate: '0%',
          customerSatisfaction: '0/5',
          ticketsHandled: 0
        }
      };
      setTeamMembers([...teamMembers, newMember]);
    }
    closeModal();
  };

  const filteredMembers = teamMembers.filter(member => {
    const matchesSearch = member.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          member.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = filterRole === '' || member.role === filterRole;
    const matchesStatus = filterStatus === '' || member.status === filterStatus;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'On Leave': return 'bg-yellow-100 text-yellow-800';
      case 'Inactive': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Team Management</h2>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <input
              type="text"
              placeholder="Search team members..."
              value={searchTerm}
              onChange={handleSearch}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Search className="absolute left-3 top-2.5 text-gray-400 w-4 h-4" />
          </div>
          <button onClick={toggleFilters} className="px-3 py-2 border rounded-lg hover:bg-gray-50 flex items-center">
            <Filter className="w-4 h-4 mr-1" />
            Filters
          </button>
          <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
          <button 
            onClick={openAddMemberModal}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <UserPlus className="w-4 h-4 mr-1" />
            Add Member
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
              >
                <option value="">All Roles</option>
                <option value="Support Agent">Support Agent</option>
                <option value="Support Manager">Support Manager</option>
                <option value="Team Lead">Team Lead</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="Active">Active</option>
                <option value="On Leave">On Leave</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end mt-4">
            <button onClick={resetFilters} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
              Reset Filters
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <LoadingSpinner size="lg" text="Loading team members..." />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {filteredMembers.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredMembers.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                          <span className="text-gray-600 font-medium">{member.name.split(' ').map(n => n[0]).join('')}</span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{member.name}</div>
                          <div className="flex items-center text-sm text-gray-500">
                            <Mail className="w-3 h-3 mr-1" />
                            {member.email}
                          </div>
                          <div className="flex items-center text-sm text-gray-500">
                            <Phone className="w-3 h-3 mr-1" />
                            {member.phone}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{member.role}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(member.status)}`}>
                        {member.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 flex items-center">
                        <BarChart className="w-4 h-4 mr-1 text-blue-500" />
                        <span className="font-medium">{member.performance.customerSatisfaction}</span>
                        <span className="mx-1 text-gray-500">•</span>
                        <span>{member.performance.ticketsHandled} tickets</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        onClick={() => openEditMemberModal(member)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        Edit
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-6 text-center text-gray-500">
              No team members found matching your criteria
            </div>
          )}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                {currentMember ? 'Edit Team Member' : 'Add New Team Member'}
              </h3>
            </div>
            <div className="p-6">
              <form>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <input 
                      type="text" 
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
                      defaultValue={currentMember?.name || ''}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                    <input 
                      type="email" 
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
                      defaultValue={currentMember?.email || ''}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                    <input 
                      type="tel" 
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
                      defaultValue={currentMember?.phone || ''}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                    <select 
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={currentMember?.role || ''}
                    >
                      <option value="">Select Role</option>
                      <option value="Support Agent">Support Agent</option>
                      <option value="Support Manager">Support Manager</option>
                      <option value="Team Lead">Team Lead</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select 
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      defaultValue={currentMember?.status || 'Active'}
                    >
                      <option value="Active">Active</option>
                      <option value="On Leave">On Leave</option>
                      <option value="Inactive">Inactive</option>
                    </select>
                  </div>
                </div>
              </form>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button 
                onClick={closeModal}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Cancel
              </button>
              <button 
                onClick={() => handleSaveMember({name: 'New Member', email: 'new@example.com', role: 'Support Agent', status: 'Active', phone: '+1 (555) 000-0000'})}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {currentMember ? 'Save Changes' : 'Add Member'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};