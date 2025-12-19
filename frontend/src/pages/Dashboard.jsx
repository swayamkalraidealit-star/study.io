import React, { useState, useEffect } from 'react';
import api from '../api';
import AudioPlayer from '../components/AudioPlayer';
import { BookOpen, History, Send, Sparkles, Clock, Tag } from 'lucide-react';

const Dashboard = () => {
  const [prompt, setPrompt] = useState('');
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(3);
  const [history, setHistory] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  const [examMode, setExamMode] = useState(false);
  const [textHighlighting, setTextHighlighting] = useState(false);

  const [config, setConfig] = useState(null);

  useEffect(() => {
    fetchUser();
    fetchHistory();
    fetchConfig();
  }, []);

  const fetchUser = async () => {
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchConfig = async () => {
    try {
      const res = await api.get('/study/config');
      setConfig(res.data);
      // Set default duration if not already set or if trial
      if (user?.plan === 'trial') {
        setDuration(3);
      } else if (res.data.allowed_durations?.length > 0) {
        setDuration(res.data.allowed_durations[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await api.get('/study/history');
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/study/generate', {
        prompt,
        topic,
        duration_minutes: parseInt(duration),
        exam_mode: examMode,
        text_highlighting: textHighlighting
      });
      setCurrentSession(res.data);
      fetchHistory();
      fetchUser(); // Refresh daily count
      setPrompt('');
      setTopic('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate study content');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container animate-fade-in">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Study.io</h1>
          <p style={{ color: 'var(--text-muted)' }}>Welcome back, {user?.full_name || 'User'}</p>
        </div>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ textAlign: 'right', fontSize: '0.875rem' }}>
              <div style={{ color: 'var(--text-muted)' }}>Daily Generations</div>
              <div style={{ fontWeight: 'bold' }}>{user.daily_generations || 0} / 5</div>
            </div>
            <div className={`badge badge-${user.plan}`}>
              {user.plan.toUpperCase()} PLAN
            </div>
          </div>
        )}
      </header>

      <div className="grid grid-2">
        <section>
          <div className="glass-card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
              <Sparkles size={20} color="var(--primary)" /> New Study Session
            </h2>

            {error && <div style={{ color: 'var(--error)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}

            <form onSubmit={handleGenerate}>
              <div className="input-group">
                <label><Tag size={14} /> Topic</label>
                <select 
                  value={config?.topics?.some(t => t.name === topic) ? topic : (topic ? 'Custom' : '')} 
                  onChange={(e) => {
                    if (e.target.value === 'Custom') {
                      setTopic('');
                    } else {
                      setTopic(e.target.value);
                    }
                  }} 
                  required
                >
                  <option value="">Select a topic...</option>
                  {config?.topics?.map(t => (
                    <option key={t.name} value={t.name}>{t.name}</option>
                  ))}
                  <option value="Custom">Custom Topic</option>
                </select>
              </div>
              
              {(!config?.topics?.some(t => t.name === topic) && topic !== '') || (config?.topics?.some(t => t.name === topic) === false && topic === '') ? (
                <div className="input-group">
                  <label>Enter Topic</label>
                  <input 
                    type="text" 
                    placeholder="e.g. Quantum Physics" 
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)} 
                    required 
                  />
                </div>
              ) : null}

              <div className="input-group">
                <label><Clock size={14} /> Duration (Minutes)</label>
                <select 
                  value={duration} 
                  onChange={(e) => setDuration(e.target.value)}
                >
                  {config?.allowed_durations?.map(d => {
                    const access = config.plan_access?.durations?.[d.toString()] || ['paid'];
                    const hasAccess = access.includes(user?.plan);
                    return (
                      <option key={d} value={d} disabled={!hasAccess}>
                        {d} Minutes {!hasAccess && '(Locked)'}
                      </option>
                    );
                  })}
                </select>
                {user?.plan === 'trial' && (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    Upgrade to access longer durations.
                  </p>
                )}
              </div>

              <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem' }}>
                {config?.features_enabled?.exam_mode && (
                  <label style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem', 
                    cursor: !(config.plan_access?.exam_mode?.includes(user?.plan)) ? 'not-allowed' : 'pointer', 
                    opacity: !(config.plan_access?.exam_mode?.includes(user?.plan)) ? 0.5 : 1 
                  }}>
                    <input 
                      type="checkbox" 
                      checked={examMode} 
                      onChange={(e) => setExamMode(e.target.checked)}
                      disabled={!(config.plan_access?.exam_mode?.includes(user?.plan))}
                    />
                    <span style={{ fontSize: '0.875rem' }}>
                      Exam Mode {!(config.plan_access?.exam_mode?.includes(user?.plan)) && '🔒'}
                    </span>
                  </label>
                )}
                {config?.features_enabled?.text_highlighting && (
                  <label style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem', 
                    cursor: !(config.plan_access?.text_highlighting?.includes(user?.plan)) ? 'not-allowed' : 'pointer', 
                    opacity: !(config.plan_access?.text_highlighting?.includes(user?.plan)) ? 0.5 : 1 
                  }}>
                    <input 
                      type="checkbox" 
                      checked={textHighlighting} 
                      onChange={(e) => setTextHighlighting(e.target.checked)}
                      disabled={!(config.plan_access?.text_highlighting?.includes(user?.plan))}
                    />
                    <span style={{ fontSize: '0.875rem' }}>
                      Text Highlighting {!(config.plan_access?.text_highlighting?.includes(user?.plan)) && '🔒'}
                    </span>
                  </label>
                )}
              </div>

              <div className="input-group">
                <label><BookOpen size={14} /> What do you want to study?</label>
                <textarea
                  rows="4"
                  placeholder="Enter your prompt here..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
                {loading ? 'Generating...' : <><Send size={18} /> Generate Audio</>}
              </button>
            </form>
          </div>

          {currentSession && (
            <div style={{ marginTop: '2rem' }}>
              <AudioPlayer
                src={`http://localhost:8000${currentSession.audio_url}`}
                title={currentSession.topic}
                content={currentSession.content}
                speechMarks={currentSession.speech_marks}
                userPlan={user?.plan}
                listenCount={currentSession.listen_count}
              />
            </div>
          )}
        </section>

        <section>
          <div className="glass-card" style={{ height: '100%' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
              <History size={20} color="var(--primary)" /> Recent History
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {history.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>No history yet. Start your first session!</p>
              ) : (
                history.map((session) => (
                  <div
                    key={session.id}
                    className="glass-card"
                    style={{ padding: '1rem', cursor: 'pointer', border: currentSession?.id === session.id ? '1px solid var(--primary)' : '1px solid var(--glass-border)' }}
                    onClick={() => setCurrentSession(session)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h4 style={{ fontSize: '1rem' }}>{session.topic}</h4>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(session.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
