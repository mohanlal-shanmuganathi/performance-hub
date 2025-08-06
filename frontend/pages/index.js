import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://mohanlal.pythonanywhere.com/api';

export default function Home() {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [authToken, setAuthToken] = useState(null);
  const [goals, setGoals] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    if (token && userData) {
      setAuthToken(token);
      setUser(JSON.parse(userData));
      setCurrentView('dashboard');
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      
      if (response.ok) {
        setAuthToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('userData', JSON.stringify(data.user));
        setCurrentView('dashboard');
      } else {
        alert('Login failed: ' + data.message);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const logout = () => {
    setAuthToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    setCurrentView('login');
  };

  const loadGoals = async () => {
    try {
      const response = await fetch(`${API_BASE}/goals`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      const data = await response.json();
      if (response.ok) setGoals(data);
    } catch (error) {
      console.error('Error loading goals:', error);
    }
  };

  const createGoal = async (goalData) => {
    try {
      const response = await fetch(`${API_BASE}/goals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(goalData)
      });
      if (response.ok) {
        loadGoals();
        alert('Goal created successfully!');
      }
    } catch (error) {
      alert('Error creating goal: ' + error.message);
    }
  };

  if (currentView === 'login') {
    return <LoginForm onLogin={login} />;
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <nav style={{ background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', padding: '1rem' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333' }}>Performance Management</h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button onClick={() => setCurrentView('dashboard')} style={navBtnStyle}>Dashboard</button>
            <button onClick={() => setCurrentView('goals')} style={navBtnStyle}>Goals</button>
            <button onClick={logout} style={{ ...navBtnStyle, background: '#ef4444', color: 'white' }}>Logout</button>
          </div>
        </div>
      </nav>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        {currentView === 'dashboard' && <Dashboard user={user} />}
        {currentView === 'goals' && <Goals goals={goals} onLoad={loadGoals} onCreate={createGoal} />}
      </main>
    </div>
  );
}

const navBtnStyle = {
  padding: '0.5rem 1rem',
  border: 'none',
  borderRadius: '0.5rem',
  background: '#f3f4f6',
  color: '#374151',
  cursor: 'pointer',
  fontSize: '0.875rem'
};

function LoginForm({ onLogin }) {
  const [email, setEmail] = useState('admin@company.com');
  const [password, setPassword] = useState('admin123');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(email, password);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div style={{ background: 'white', padding: '2rem', borderRadius: '1rem', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', width: '400px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1.5rem', textAlign: 'center', color: '#333' }}>Login</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', color: '#374151', fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '1rem' }}
              required
            />
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', color: '#374151', fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '1rem' }}
              required
            />
          </div>
          <button
            type="submit"
            style={{ width: '100%', background: '#3b82f6', color: 'white', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', fontSize: '1rem', cursor: 'pointer' }}
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

function Dashboard({ user }) {
  return (
    <div>
      <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1.5rem', color: 'white' }}>Welcome, {user?.first_name}!</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div style={{ background: 'rgba(255,255,255,0.9)', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem', color: '#333' }}>Your Role</h3>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>{user?.role}</p>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.9)', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem', color: '#333' }}>Department</h3>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>{user?.department || 'N/A'}</p>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.9)', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem', color: '#333' }}>Status</h3>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#8b5cf6' }}>Active</p>
        </div>
      </div>
    </div>
  );
}

function Goals({ goals, onLoad, onCreate }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    progress: 0
  });

  useEffect(() => {
    onLoad();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreate({ ...formData, status: 'draft' });
    setFormData({ title: '', description: '', category: '', progress: 0 });
    setShowForm(false);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>Goals</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{ background: '#3b82f6', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '0.5rem', border: 'none', cursor: 'pointer' }}
        >
          {showForm ? 'Cancel' : 'Add Goal'}
        </button>
      </div>

      {showForm && (
        <div style={{ background: 'rgba(255,255,255,0.95)', padding: '1.5rem', borderRadius: '1rem', marginBottom: '1.5rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ display: 'block', color: '#374151', fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem' }}
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', color: '#374151', fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem' }}
                >
                  <option value="">Select category</option>
                  <option value="Professional Development">Professional Development</option>
                  <option value="Leadership">Leadership</option>
                  <option value="Technical Skills">Technical Skills</option>
                  <option value="Performance">Performance</option>
                </select>
              </div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', color: '#374151', fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', minHeight: '80px' }}
              />
            </div>
            <button
              type="submit"
              style={{ background: '#10b981', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '0.5rem', border: 'none', cursor: 'pointer' }}
            >
              Create Goal
            </button>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {goals.map((goal) => (
          <div key={goal.id} style={{ background: 'rgba(255,255,255,0.9)', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem', color: '#333' }}>{goal.title}</h3>
            <p style={{ color: '#6b7280', marginBottom: '0.5rem', fontSize: '0.875rem' }}>{goal.description}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{goal.category}</span>
              <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>{goal.progress}%</span>
            </div>
            <div style={{ width: '100%', background: '#e5e7eb', borderRadius: '9999px', height: '8px' }}>
              <div
                style={{ background: '#3b82f6', height: '8px', borderRadius: '9999px', width: `${goal.progress}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}