import React, { useState, useEffect } from 'react';
import api from '../api';
import { Users, Settings, BarChart3, Shield, Plus, Save, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';

const Admin = () => {
  const [users, setUsers] = useState([]);
  const [config, setConfig] = useState(null);
  const [usage, setUsage] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [newTopic, setNewTopic] = useState({ name: '', description: '', prompt_template: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersRes, configRes, usageRes, sessionsRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/config'),
        api.get('/admin/usage-report'),
        api.get('/admin/sessions')
      ]);
      setUsers(usersRes.data);
      setConfig(configRes.data);
      setUsage(usageRes.data);
      setSessions(sessionsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateConfig = async (updates) => {
    try {
      const res = await api.put('/admin/config', updates);
      setConfig(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddTopic = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/topics', newTopic);
      setNewTopic({ name: '', description: '', prompt_template: '' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="container animate-fade-in">
      <header style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Shield size={32} color="var(--primary)" /> Admin Control Center
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <ThemeToggle />
          <button 
            onClick={handleLogout}
            className="btn btn-secondary"
            style={{ padding: '0.5rem', minWidth: 'auto' }}
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <div className="grid grid-2">
        <section className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
            <BarChart3 size={20} color="var(--primary)" /> Usage Overview
          </h2>
          {usage && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Total Sessions</p>
                <h3 style={{ fontSize: '1.5rem' }}>{usage.summary.total_sessions}</h3>
              </div>
              <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Total Cost</p>
                <h3 style={{ fontSize: '1.5rem' }}>${usage.summary.total_cost.toFixed(4)}</h3>
              </div>
              <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>OpenAI Tokens</p>
                <h3 style={{ fontSize: '1.5rem' }}>{usage.summary.total_openai_tokens}</h3>
              </div>
              <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Polly Characters</p>
                <h3 style={{ fontSize: '1.5rem' }}>{usage.summary.total_polly_characters}</h3>
              </div>
            </div>
          )}
        </section>

        <section className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
            <Settings size={20} color="var(--primary)" /> App Configuration
          </h2>
          {config && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="input-group">
                <label>Trial Session Limit</label>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <input 
                    type="number" 
                    value={config.trial_limit_sessions} 
                    onChange={(e) => setConfig({...config, trial_limit_sessions: parseInt(e.target.value)})} 
                  />
                  <button className="btn btn-primary" onClick={() => handleUpdateConfig({ trial_limit_sessions: config.trial_limit_sessions })}>
                    <Save size={16} />
                  </button>
                </div>
              </div>
              
              <div>
                <label style={{ color: 'var(--text-muted)', fontSize: '0.875rem', display: 'block', marginBottom: '0.5rem' }}>Feature Toggles</label>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {Object.entries(config.features_enabled).map(([key, val]) => (
                    <button 
                      key={key}
                      className={`btn ${val ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => handleUpdateConfig({ features_enabled: { ...config.features_enabled, [key]: !val } })}
                    >
                      {key.replace('_', ' ')}: {val ? 'ON' : 'OFF'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        <section className="glass-card" style={{ gridColumn: 'span 2' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
            <Users size={20} color="var(--primary)" /> User Usage Details
          </h2>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  <th style={{ padding: '0.5rem' }}>Email</th>
                  <th style={{ padding: '0.5rem' }}>Sessions</th>
                  <th style={{ padding: '0.5rem' }}>Tokens</th>
                  <th style={{ padding: '0.5rem' }}>Characters</th>
                  <th style={{ padding: '0.5rem' }}>Cost</th>
                </tr>
              </thead>
              <tbody>
                {usage?.user_usage.map(u => (
                  <tr key={u._id} style={{ borderTop: '1px solid var(--glass-border)' }}>
                    <td style={{ padding: '0.75rem' }}>{u.email}</td>
                    <td style={{ padding: '0.75rem' }}>{u.sessions}</td>
                    <td style={{ padding: '0.75rem' }}>{u.openai_tokens}</td>
                    <td style={{ padding: '0.75rem' }}>{u.polly_characters}</td>
                    <td style={{ padding: '0.75rem' }}>${u.total_cost.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="glass-card" style={{ gridColumn: 'span 2' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
            <Shield size={20} color="var(--primary)" /> Prompt History
          </h2>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  <th style={{ padding: '0.5rem' }}>Topic</th>
                  <th style={{ padding: '0.5rem' }}>Prompt</th>
                  <th style={{ padding: '0.5rem' }}>Date</th>
                  <th style={{ padding: '0.5rem' }}>Listens</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map(s => (
                  <tr key={s.id} style={{ borderTop: '1px solid var(--glass-border)' }}>
                    <td style={{ padding: '0.75rem' }}>{s.topic}</td>
                    <td style={{ padding: '0.75rem', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {s.prompt}
                    </td>
                    <td style={{ padding: '0.75rem' }}>{new Date(s.created_at).toLocaleDateString()}</td>
                    <td style={{ padding: '0.75rem' }}>{s.listen_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
            <Plus size={20} color="var(--primary)" /> Topic Presets
          </h2>
          <form onSubmit={handleAddTopic}>
            <div className="input-group">
              <label>Topic Name</label>
              <input type="text" value={newTopic.name} onChange={(e) => setNewTopic({...newTopic, name: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Prompt Template</label>
              <textarea 
                value={newTopic.prompt_template} 
                onChange={(e) => setNewTopic({...newTopic, prompt_template: e.target.value})} 
                required 
                style={{ width: '100%', background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', color: 'white', padding: '0.5rem', borderRadius: '0.5rem' }}
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              Add Preset
            </button>
          </form>
          <div style={{ marginTop: '1.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {config?.topics.map((t, i) => (
              <span key={i} className="badge" style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)' }}>
                {t.name}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Admin;
