import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { goalsAPI } from '../services/api';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { PlusIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

const Goals = () => {
  const { user, hasRole } = useAuth();
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const response = await goalsAPI.getAll();
      setGoals(response.data);
    } catch (error) {
      toast.error('Failed to fetch goals');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      if (editingGoal) {
        await goalsAPI.update(editingGoal.id, data);
        toast.success('Goal updated successfully');
      } else {
        await goalsAPI.create(data);
        toast.success('Goal created successfully');
      }
      
      reset();
      setShowCreateForm(false);
      setEditingGoal(null);
      fetchGoals();
    } catch (error) {
      toast.error('Failed to save goal');
    }
  };

  const handleApprove = async (goalId) => {
    try {
      await goalsAPI.approve(goalId);
      toast.success('Goal approved successfully');
      fetchGoals();
    } catch (error) {
      toast.error('Failed to approve goal');
    }
  };

  const handleEdit = (goal) => {
    setEditingGoal(goal);
    reset({
      title: goal.title,
      description: goal.description,
      category: goal.category,
      target_date: goal.target_date,
      progress: goal.progress,
      status: goal.status
    });
    setShowCreateForm(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Goals</h1>
          <p className="mt-2 text-gray-600">
            {hasRole(['admin', 'manager']) ? 'Manage team goals and track progress' : 'Track your goals and progress'}
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Goal
        </button>
      </div>

      {/* Create/Edit Goal Form */}
      {showCreateForm && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingGoal ? 'Edit Goal' : 'Create New Goal'}
          </h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Title</label>
                <input
                  {...register('title', { required: 'Title is required' })}
                  className="form-input"
                  placeholder="Goal title"
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
                )}
              </div>
              
              <div>
                <label className="form-label">Category</label>
                <select {...register('category')} className="form-input">
                  <option value="">Select category</option>
                  <option value="Professional Development">Professional Development</option>
                  <option value="Leadership">Leadership</option>
                  <option value="Technical Skills">Technical Skills</option>
                  <option value="Performance">Performance</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div>
              <label className="form-label">Description</label>
              <textarea
                {...register('description')}
                className="form-input"
                rows="3"
                placeholder="Goal description"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="form-label">Target Date</label>
                <input
                  {...register('target_date')}
                  type="date"
                  className="form-input"
                />
              </div>
              
              <div>
                <label className="form-label">Progress (%)</label>
                <input
                  {...register('progress', { 
                    min: { value: 0, message: 'Progress must be at least 0' },
                    max: { value: 100, message: 'Progress cannot exceed 100' }
                  })}
                  type="number"
                  min="0"
                  max="100"
                  className="form-input"
                  placeholder="0"
                />
                {errors.progress && (
                  <p className="mt-1 text-sm text-red-600">{errors.progress.message}</p>
                )}
              </div>
              
              <div>
                <label className="form-label">Status</label>
                <select {...register('status')} className="form-input">
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingGoal(null);
                  reset();
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {editingGoal ? 'Update Goal' : 'Create Goal'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Goals List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.map((goal) => (
          <div key={goal.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold text-gray-900">{goal.title}</h3>
              <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(goal.status)}`}>
                {goal.status}
              </span>
            </div>
            
            {goal.description && (
              <p className="text-gray-600 text-sm mb-3">{goal.description}</p>
            )}
            
            <div className="space-y-2 mb-4">
              {goal.category && (
                <p className="text-sm text-gray-500">
                  <span className="font-medium">Category:</span> {goal.category}
                </p>
              )}
              {goal.target_date && (
                <p className="text-sm text-gray-500">
                  <span className="font-medium">Target Date:</span> {new Date(goal.target_date).toLocaleDateString()}
                </p>
              )}
              {hasRole(['admin', 'manager']) && goal.employee_name && (
                <p className="text-sm text-gray-500">
                  <span className="font-medium">Employee:</span> {goal.employee_name}
                </p>
              )}
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Progress</span>
                <span>{goal.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getProgressColor(goal.progress)}`}
                  style={{ width: `${goal.progress}%` }}
                />
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(goal)}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  Edit
                </button>
              </div>
              
              {hasRole(['admin', 'manager']) && !goal.manager_approved && goal.status === 'draft' && (
                <button
                  onClick={() => handleApprove(goal.id)}
                  className="flex items-center text-green-600 hover:text-green-700 text-sm font-medium"
                >
                  <CheckIcon className="h-4 w-4 mr-1" />
                  Approve
                </button>
              )}
              
              {goal.manager_approved && (
                <span className="flex items-center text-green-600 text-sm">
                  <CheckIcon className="h-4 w-4 mr-1" />
                  Approved
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {goals.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No goals found. Create your first goal to get started!</p>
        </div>
      )}
    </div>
  );
};

export default Goals;