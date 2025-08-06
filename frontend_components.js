        // Dashboard Component
        const Dashboard = ({ user }) => {
            const [analytics, setAnalytics] = useState(null);
            const [goals, setGoals] = useState([]);
            const [loading, setLoading] = useState(true);

            useEffect(() => {
                fetchDashboardData();
            }, []);

            const fetchDashboardData = async () => {
                try {
                    const goalsData = await apiCall('/goals');
                    setGoals(goalsData);

                    if (user.role !== 'employee') {
                        const analyticsData = await apiCall('/analytics/dashboard');
                        setAnalytics(analyticsData);
                    }
                } catch (error) {
                    console.error('Error fetching dashboard data:', error);
                } finally {
                    setLoading(false);
                }
            };

            if (loading) {
                return (
                    <div className="flex items-center justify-center h-64">
                        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
                    </div>
                );
            }

            return (
                <div className="max-w-7xl mx-auto py-8 px-4 space-y-8">
                    <div className="text-center mb-8">
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                            Welcome back, {user?.first_name}! 👋
                        </h1>
                        <p className="text-gray-600 text-lg">Here's your performance overview</p>
                    </div>

                    {analytics && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <div className="glass-effect rounded-2xl p-6 card-hover">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Total Employees</p>
                                        <p className="text-3xl font-bold text-gray-900 mt-2">{analytics.total_employees}</p>
                                    </div>
                                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-2xl">👥</div>
                                </div>
                            </div>
                            <div className="glass-effect rounded-2xl p-6 card-hover">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Active Goals</p>
                                        <p className="text-3xl font-bold text-gray-900 mt-2">{analytics.total_goals}</p>
                                    </div>
                                    <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-2xl">🎯</div>
                                </div>
                            </div>
                            <div className="glass-effect rounded-2xl p-6 card-hover">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                                        <p className="text-3xl font-bold text-gray-900 mt-2">{analytics.goal_completion_rate}%</p>
                                    </div>
                                    <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-2xl">📈</div>
                                </div>
                            </div>
                            <div className="glass-effect rounded-2xl p-6 card-hover">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Avg Rating</p>
                                        <p className="text-3xl font-bold text-gray-900 mt-2">{analytics.average_ratings.overall}/5</p>
                                    </div>
                                    <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center text-2xl">⭐</div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="glass-effect rounded-2xl p-6 card-hover">
                        <h3 className="text-xl font-semibold text-gray-900 mb-6">Your Goals 🎯</h3>
                        <div className="space-y-4">
                            {goals.slice(0, 5).map(goal => (
                                <div key={goal.id} className="bg-white/50 rounded-xl p-4 border border-white/20">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className="font-medium text-gray-900">{goal.title}</h4>
                                        <span className={`px-2 py-1 text-xs rounded-full ${
                                            goal.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            goal.status === 'active' ? 'bg-blue-100 text-blue-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {goal.status}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 mb-3">{goal.category}</p>
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1 mr-4">
                                            <div className="w-full bg-gray-200 rounded-full h-2">
                                                <div
                                                    className={`h-2 rounded-full transition-all duration-500 ${
                                                        goal.progress >= 80 ? 'bg-green-500' :
                                                        goal.progress >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                                                    }`}
                                                    style={{ width: `${goal.progress}%` }}
                                                />
                                            </div>
                                        </div>
                                        <span className="text-sm font-medium text-gray-900">{goal.progress}%</span>
                                    </div>
                                </div>
                            ))}
                            {goals.length === 0 && (
                                <div className="text-center py-8 text-gray-500">
                                    <div className="text-4xl mb-2">🎯</div>
                                    <p>No goals yet. Create your first goal!</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        };

        // Employee Management Component
        const Employees = ({ user }) => {
            const [employees, setEmployees] = useState([]);
            const [showForm, setShowForm] = useState(false);
            const [editingEmployee, setEditingEmployee] = useState(null);
            const [loading, setLoading] = useState(true);
            const [formData, setFormData] = useState({
                email: '', password: '', first_name: '', last_name: '',
                role: 'employee', department: '', position: '', manager_id: '', hire_date: ''
            });

            useEffect(() => {
                fetchEmployees();
            }, []);

            const fetchEmployees = async () => {
                try {
                    const data = await apiCall('/employees');
                    setEmployees(data);
                } catch (error) {
                    console.error('Error fetching employees:', error);
                } finally {
                    setLoading(false);
                }
            };

            const handleSubmit = async (e) => {
                e.preventDefault();
                try {
                    if (editingEmployee) {
                        const updateData = { ...formData };
                        delete updateData.password;
                        await apiCall(`/employees/${editingEmployee.id}`, {
                            method: 'PUT',
                            body: JSON.stringify(updateData)
                        });
                    } else {
                        await apiCall('/employees', {
                            method: 'POST',
                            body: JSON.stringify(formData)
                        });
                    }
                    setShowForm(false);
                    setEditingEmployee(null);
                    setFormData({
                        email: '', password: '', first_name: '', last_name: '',
                        role: 'employee', department: '', position: '', manager_id: '', hire_date: ''
                    });
                    fetchEmployees();
                } catch (error) {
                    alert('Error saving employee: ' + error.message);
                }
            };

            const handleEdit = (employee) => {
                setEditingEmployee(employee);
                setFormData({
                    email: employee.email,
                    first_name: employee.first_name,
                    last_name: employee.last_name,
                    role: employee.role,
                    department: employee.department || '',
                    position: employee.position || '',
                    manager_id: employee.manager_id || '',
                    hire_date: employee.hire_date || '',
                    password: ''
                });
                setShowForm(true);
            };

            if (loading) {
                return (
                    <div className="flex items-center justify-center h-64">
                        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
                    </div>
                );
            }

            return (
                <div className="max-w-6xl mx-auto py-8 px-4">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            Team Management 👥
                        </h2>
                        {user.role === 'admin' && (
                            <button
                                onClick={() => setShowForm(true)}
                                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-200 shadow-lg"
                            >
                                Add Employee
                            </button>
                        )}
                    </div>

                    {showForm && (
                        <div className="glass-effect rounded-2xl p-6 mb-6 card-hover">
                            <h3 className="text-lg font-semibold mb-4">
                                {editingEmployee ? 'Edit Employee' : 'Add New Employee'}
                            </h3>
                            <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                {!editingEmployee && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                                        <input
                                            type="password"
                                            value={formData.password}
                                            onChange={(e) => setFormData({...formData, password: e.target.value})}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                            required
                                        />
                                    </div>
                                )}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                                    <input
                                        type="text"
                                        value={formData.first_name}
                                        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                                    <input
                                        type="text"
                                        value={formData.last_name}
                                        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                                    <select
                                        value={formData.role}
                                        onChange={(e) => setFormData({...formData, role: e.target.value})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="employee">Employee</option>
                                        <option value="manager">Manager</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                                    <input
                                        type="text"
                                        value={formData.department}
                                        onChange={(e) => setFormData({...formData, department: e.target.value})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div className="col-span-2 flex justify-end space-x-3">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setShowForm(false);
                                            setEditingEmployee(null);
                                        }}
                                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-md hover:from-blue-600 hover:to-purple-600"
                                    >
                                        {editingEmployee ? 'Update' : 'Create'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="glass-effect rounded-2xl overflow-hidden card-hover">
                        <div className="overflow-x-auto">
                            <table className="min-w-full">
                                <thead className="bg-white/50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {employees.map(employee => (
                                        <tr key={employee.id} className="hover:bg-white/30">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {employee.first_name} {employee.last_name}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {employee.email}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                                                {employee.role}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {employee.department}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <button
                                                    onClick={() => handleEdit(employee)}
                                                    className="text-blue-600 hover:text-blue-900 mr-3"
                                                >
                                                    Edit
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            );
        };