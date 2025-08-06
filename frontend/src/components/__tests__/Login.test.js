import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../../pages/Login';
import { AuthProvider } from '../../hooks/useAuth';

// Mock the API
jest.mock('../../services/api', () => ({
  authAPI: {
    login: jest.fn()
  }
}));

const MockedLogin = () => (
  <BrowserRouter>
    <AuthProvider>
      <Login />
    </AuthProvider>
  </BrowserRouter>
);

describe('Login Component', () => {
  test('renders login form', () => {
    render(<MockedLogin />);
    
    expect(screen.getByText('Performance Management System')).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    render(<MockedLogin />);
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });

  test('shows validation error for invalid email', async () => {
    render(<MockedLogin />);
    
    const emailInput = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Invalid email address')).toBeInTheDocument();
    });
  });

  test('displays demo credentials', () => {
    render(<MockedLogin />);
    
    expect(screen.getByText('Demo Credentials:')).toBeInTheDocument();
    expect(screen.getByText(/admin@company.com/)).toBeInTheDocument();
    expect(screen.getByText(/manager@company.com/)).toBeInTheDocument();
    expect(screen.getByText(/employee@company.com/)).toBeInTheDocument();
  });
});