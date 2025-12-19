import React, { useState, useEffect } from 'react';
import api from '../api';
import { Users, Settings, BarChart3, Shield, Plus, Save } from 'lucide-react';

const Admin = () => {
  const [users, setUsers] = useState([]);
  const [config, setConfig] = useState(null);
  const [usage, setUsage] = useState(null);
  const [newTopic, setNewTopic] = useState({ name: '', description: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usersRes, configRes, usageRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/config'),
        api.get('/admin/usage-report')
      ]);
      setUsers(usersRes.data);
      setConfig(configRes.data);
      setUsage(usageRes.data);
    } catch (err) {
      console.error(err);
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
      setNewTopic({ name: '', description: '' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container animate-fade-in">
      <header style={{ marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Shield size={32} color="var(--primary)" /> Admin Control Center
        </h1>
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
                <h3 style={{ fontSize: '1.5rem' }}>{usage.total_sessions}</h3>
              </div>
              <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>OpenAI Tokens</p>
                <h3 style={{ fontSize: '1.5rem' }}>{usage.total_openai_tokens}</h3>
              </div>
              <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Polly Characters</p>
                <h3 style={{ fontSize: '1.5rem' }}>{usage.total_polly_characters}</h3>
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
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button 
                    className={`btn ${config.features_enabled.audio_generation ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => handleUpdateConfig({ features_enabled: { ...config.features_enabled, audio_generation: !config.features_enabled.audio_generation } })}
                  >
                    Audio Gen: {config.features_enabled.audio_generation ? 'ON' : 'OFF'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </section>

        <section className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
            <Users size={20} color="var(--primary)" /> User Management
          </h2>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  <th style={{ padding: '0.5rem' }}>Email</th>
                  <th style={{ padding: '0.5rem' }}>Plan</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} style={{ borderTop: '1px solid var(--glass-border)' }}>
                    <td style={{ padding: '0.75rem' }}>{u.email}</td>
                    <td style={{ padding: '0.75rem' }}>
                      <span className={`badge badge-${u.plan}`}>{u.plan}</span>
                    </td>
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
