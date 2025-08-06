import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { analyticsAPI, goalsAPI, reviewsAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { 
  UserGroupIcon, 
  TargetIcon, 
  DocumentTextIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const { user, hasRole } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [userGoals, setUserGoals] = useState([]);
  const [userReviews, setUserReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (hasRole(['admin', 'manager'])) {
          const [dashboardRes, goalsRes, reviewsRes] = await Promise.all([
            analyticsAPI.getDashboard(),
            goalsAPI.getAll(),
            reviewsAPI.getAll()
          ]);
          setDashboardData(dashboardRes.data);
          setUserGoals(goalsRes.data);
          setUserReviews(reviewsRes.data);
        } else {
          const [goalsRes, reviewsRes] = await Promise.all([
            goalsAPI.getAll(),
            reviewsAPI.getAll()
          ]);
          setUserGoals(goalsRes.data);
          setUserReviews(reviewsRes.data);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [hasRole]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const StatCard = ({ title, value, icon: Icon, color = 'blue' }) => (
    <div className="card">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );

  const getGoalStatusData = () => {
    const statusCounts = userGoals.reduce((acc, goal) => {
      acc[goal.status] = (acc[goal.status] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(statusCounts).map(([status, count]) => ({
      name: status.charAt(0).toUpperCase() + status.slice(1),
      value: count
    }));
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's an overview of your performance management dashboard.
        </p>
      </div>

      {/* Stats Cards */}
      {hasRole(['admin', 'manager']) && dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Employees"
            value={dashboardData.total_employees}
            icon={UserGroupIcon}
            color="blue"
          />
          <StatCard
            title="Active Goals"
            value={dashboardData.total_goals}
            icon={TargetIcon}
            color="green"
          />
          <StatCard
            title="Reviews Completed"
            value={dashboardData.total_reviews}
            icon={DocumentTextIcon}
            color="yellow"
          />
          <StatCard
            title="Goal Completion Rate"
            value={`${dashboardData.goal_completion_rate}%`}
            icon={ChartBarIcon}
            color="purple"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Goals Overview */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {hasRole(['admin', 'manager']) ? 'Team Goals Status' : 'My Goals Status'}
          </h3>
          {userGoals.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={getGoalStatusData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {getGoalStatusData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No goals found</p>
          )}
        </div>

        {/* Recent Reviews */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Reviews</h3>
          {userReviews.length > 0 ? (
            <div className="space-y-4">
              {userReviews.slice(0, 5).map((review) => (
                <div key={review.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">
                      {hasRole(['admin', 'manager']) ? review.reviewee_name : review.reviewer_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      {review.review_type} review • {review.review_period}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      {review.overall_rating ? `${review.overall_rating}/5` : 'Pending'}
                    </p>
                    <p className={`text-xs px-2 py-1 rounded-full ${
                      review.status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {review.status}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No reviews found</p>
          )}
        </div>
      </div>

      {/* Performance Metrics for Admins/Managers */}
      {hasRole(['admin', 'manager']) && dashboardData && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Performance Ratings</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { name: 'Overall', rating: dashboardData.average_ratings.overall },
              { name: 'Technical', rating: dashboardData.average_ratings.technical },
              { name: 'Communication', rating: dashboardData.average_ratings.communication },
              { name: 'Leadership', rating: dashboardData.average_ratings.leadership },
              { name: 'Teamwork', rating: dashboardData.average_ratings.teamwork },
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 5]} />
              <Tooltip />
              <Bar dataKey="rating" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Dashboard;