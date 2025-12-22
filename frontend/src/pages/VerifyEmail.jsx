import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api';
import { CheckCircle, XCircle, Mail, Loader } from 'lucide-react';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. No token provided.');
        return;
      }

      try {
        const response = await api.post(`/auth/verify-email?token=${token}`);
        setStatus('success');
        setMessage(response.data.message);
        setEmail(response.data.email);
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } catch (err) {
        setStatus('error');
        setMessage(err.response?.data?.detail || 'Verification failed. Please try again.');
      }
    };

    verifyToken();
  }, [searchParams, navigate]);

  const handleResendEmail = async () => {
    if (!email) {
      setMessage('Please go to the login page and use "Resend verification email"');
      return;
    }

    try {
      await api.post('/auth/resend-verification', { email });
      setMessage('Verification email sent! Please check your inbox.');
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to resend email.');
    }
  };

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
      <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '500px', textAlign: 'center' }}>
        {status === 'verifying' && (
          <>
            <Loader size={64} style={{ color: 'var(--primary)', margin: '0 auto 1.5rem', animation: 'spin 1s linear infinite' }} />
            <h2>Verifying Your Email...</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>
              Please wait while we verify your email address.
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle size={64} style={{ color: 'var(--success)', margin: '0 auto 1.5rem' }} />
            <h2 style={{ color: 'var(--success)' }}>Email Verified!</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>
              {message}
            </p>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', fontSize: '0.875rem' }}>
              Redirecting to login page...
            </p>
            <button 
              onClick={() => navigate('/login')}
              className="btn btn-primary"
              style={{ marginTop: '1.5rem' }}
            >
              Go to Login
            </button>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle size={64} style={{ color: 'var(--error)', margin: '0 auto 1.5rem' }} />
            <h2 style={{ color: 'var(--error)' }}>Verification Failed</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>
              {message}
            </p>
            <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button 
                onClick={handleResendEmail}
                className="btn btn-secondary"
              >
                <Mail size={18} /> Resend Email
              </button>
              <button 
                onClick={() => navigate('/login')}
                className="btn btn-primary"
              >
                Go to Login
              </button>
            </div>
          </>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default VerifyEmail;
