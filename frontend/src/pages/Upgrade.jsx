import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Crown, Check, X, Sparkles, Clock, Zap, Star, ArrowRight } from 'lucide-react';

const Upgrade = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
      
      // If user is already on premium, redirect to dashboard
      if (res.data.plan === 'paid') {
        setTimeout(() => navigate('/dashboard'), 2000);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to load user information');
    }
  };

  const handleUpgrade = async () => {
    setLoading(true);
    setError('');
    
    try {
      await api.post('/upgrade/to-premium');
      setSuccess(true);
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upgrade. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const trialFeatures = [
    { text: '5 generations per day', included: true },
    { text: '3-minute sessions only', included: true },
    { text: 'Basic audio quality', included: true },
    { text: 'Longer session durations', included: false },
    { text: 'Exam mode', included: false },
    { text: 'Text highlighting', included: false },
    { text: 'Unlimited generations', included: false },
  ];

  const premiumFeatures = [
    { text: 'Unlimited generations', included: true, highlight: true },
    { text: '3, 5, and 10 minute sessions', included: true, highlight: true },
    { text: 'Premium neural voices', included: true },
    { text: 'Exam mode preparation', included: true, highlight: true },
    { text: 'Text highlighting sync', included: true, highlight: true },
    { text: 'Priority support', included: true },
    { text: 'Advanced study features', included: true },
  ];

  if (user?.plan === 'paid') {
    return (
      <div className="container animate-fade-in" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="glass-card" style={{ textAlign: 'center', maxWidth: '500px' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>👑</div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>You're Already Premium!</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
            Enjoy all the premium features Study.io has to offer.
          </p>
          <button 
            onClick={() => navigate('/dashboard')} 
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container animate-fade-in" style={{ minHeight: '100vh', paddingTop: '3rem', paddingBottom: '3rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <div style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '0.5rem', 
          padding: '0.5rem 1.5rem', 
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1))',
          borderRadius: 'var(--radius-full)',
          marginBottom: '1.5rem',
          border: '1px solid rgba(99, 102, 241, 0.2)'
        }}>
          <Sparkles size={16} color="var(--primary)" />
          <span style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--primary)' }}>SPECIAL OFFER</span>
        </div>
        
        <h1 style={{ fontSize: '3rem', marginBottom: '1rem', background: 'linear-gradient(135deg, var(--primary), var(--accent))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          Upgrade to Premium
        </h1>
        <p style={{ fontSize: '1.25rem', color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto' }}>
          Unlock unlimited learning potential with advanced AI-powered study features
        </p>
      </div>

      {error && (
        <div style={{ 
          maxWidth: '900px', 
          margin: '0 auto 2rem', 
          padding: '1rem', 
          background: 'rgba(239, 68, 68, 0.1)', 
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius)',
          color: 'var(--error)',
          textAlign: 'center'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ 
          maxWidth: '900px', 
          margin: '0 auto 2rem', 
          padding: '1rem', 
          background: 'rgba(34, 197, 94, 0.1)', 
          border: '1px solid rgba(34, 197, 94, 0.3)',
          borderRadius: 'var(--radius)',
          color: '#22c55e',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem'
        }}>
          <Check size={20} />
          <span>Successfully upgraded to Premium! Redirecting...</span>
        </div>
      )}

      <div className="grid grid-2" style={{ maxWidth: '900px', margin: '0 auto', gap: '2rem' }}>
        {/* Trial Plan */}
        <div className="glass-card" style={{ position: 'relative', opacity: 0.7 }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Trial Plan</h3>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
              Free
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Current plan</p>
          </div>

          <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {trialFeatures.map((feature, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  {feature.included ? (
                    <Check size={18} color="var(--primary)" style={{ flexShrink: 0 }} />
                  ) : (
                    <X size={18} color="var(--text-muted)" style={{ flexShrink: 0, opacity: 0.5 }} />
                  )}
                  <span style={{ 
                    fontSize: '0.875rem', 
                    color: feature.included ? 'var(--text-primary)' : 'var(--text-muted)',
                    textDecoration: feature.included ? 'none' : 'line-through'
                  }}>
                    {feature.text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Premium Plan */}
        <div className="glass-card" style={{ 
          position: 'relative',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1))',
          border: '2px solid var(--primary)',
          boxShadow: '0 0 40px rgba(99, 102, 241, 0.2)'
        }}>
          <div style={{ 
            position: 'absolute', 
            top: '-12px', 
            right: '20px', 
            background: 'linear-gradient(135deg, var(--primary), var(--accent))',
            color: 'white',
            padding: '0.25rem 1rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem'
          }}>
            <Star size={12} fill="white" />
            RECOMMENDED
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Crown size={24} color="var(--primary)" />
              <h3 style={{ fontSize: '1.5rem' }}>Premium Plan</h3>
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
              Free
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Limited time offer</p>
          </div>

          <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1.5rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {premiumFeatures.map((feature, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ 
                    width: '18px', 
                    height: '18px', 
                    borderRadius: '50%', 
                    background: feature.highlight ? 'linear-gradient(135deg, var(--primary), var(--accent))' : 'var(--primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <Check size={12} color="white" />
                  </div>
                  <span style={{ 
                    fontSize: '0.875rem',
                    fontWeight: feature.highlight ? '600' : '400'
                  }}>
                    {feature.text}
                  </span>
                  {feature.highlight && <Zap size={14} color="var(--accent)" />}
                </div>
              ))}
            </div>
          </div>

          <button 
            onClick={handleUpgrade}
            disabled={loading || success}
            className="btn btn-primary"
            style={{ 
              width: '100%', 
              justifyContent: 'center',
              background: 'linear-gradient(135deg, var(--primary), var(--accent))',
              fontSize: '1rem',
              padding: '0.875rem',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {loading ? (
              'Upgrading...'
            ) : success ? (
              <>
                <Check size={20} />
                Upgraded!
              </>
            ) : (
              <>
                <Crown size={20} />
                Upgrade Now
                <ArrowRight size={20} />
              </>
            )}
          </button>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '3rem' }}>
        <button 
          onClick={() => navigate('/dashboard')}
          style={{ 
            background: 'none', 
            border: 'none', 
            color: 'var(--text-muted)', 
            cursor: 'pointer',
            fontSize: '0.875rem',
            textDecoration: 'underline'
          }}
        >
          Maybe later, back to dashboard
        </button>
      </div>
    </div>
  );
};

export default Upgrade;
