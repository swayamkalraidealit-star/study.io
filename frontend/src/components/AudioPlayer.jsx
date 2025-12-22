import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, Volume2, Settings } from 'lucide-react';

const AudioPlayer = ({ src, title, userPlan, listenCount, content, speechMarks = [] }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [currentWordIndex, setCurrentWordIndex] = useState(-1);
    const audioRef = useRef(null);

    const isTrial = userPlan === 'trial';
    const canHighlight = userPlan === 'paid' && speechMarks.length > 0;

    useEffect(() => {
        if (audioRef.current) {
            audioRef.current.playbackRate = playbackSpeed;
        }
    }, [playbackSpeed]);

    const togglePlay = () => {
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const handleTimeUpdate = () => {
        const time = audioRef.current.currentTime * 1000; // Polly marks are in ms
        setCurrentTime(audioRef.current.currentTime);
        
        if (canHighlight) {
            // Find the current word based on time
            const markIndex = speechMarks.findIndex((mark, index) => {
                const nextMark = speechMarks[index + 1];
                return time >= mark.time && (!nextMark || time < nextMark.time);
            });
            setCurrentWordIndex(markIndex);
        }
    };

    const handleLoadedMetadata = () => {
        setDuration(audioRef.current.duration);
    };

    const handleSeek = (e) => {
        const time = parseFloat(e.target.value);
        audioRef.current.currentTime = time;
        setCurrentTime(time);
    };

    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    const renderHighlightedContent = () => {
        if (!content) return null;
        if (!canHighlight) return <p style={{ lineHeight: '1.6' }}>{content}</p>;

        return (
            <p style={{ lineHeight: '1.8', fontSize: '1.05rem' }}>
                {speechMarks.map((mark, index) => (
                    <span 
                        key={index}
                        style={{
                            backgroundColor: currentWordIndex === index ? 'rgba(var(--primary-rgb), 0.3)' : 'transparent',
                            borderRadius: '2px',
                            padding: '0 2px',
                            transition: 'background-color 0.1s ease',
                            color: currentWordIndex === index ? 'var(--primary)' : 'inherit',
                            fontWeight: currentWordIndex === index ? 'bold' : 'normal'
                        }}
                    >
                        {mark.value}{' '}
                    </span>
                ))}
            </p>
        );
    };

    return (
        <div className="glass-card audio-player" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>{title}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Study Session Audio</p>
                </div>
                {isTrial && (
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Listens Used</div>
                        <div style={{ fontSize: '0.875rem', fontWeight: 'bold', color: listenCount >= 3 ? 'var(--error)' : 'var(--primary)' }}>
                            {listenCount} / 3
                        </div>
                    </div>
                )}
            </div>

            <div style={{ marginBottom: '1.5rem', maxHeight: '200px', overflowY: 'auto', padding: '1rem', background: 'rgba(0,0,0,0.05)', borderRadius: '8px' }}>
                {renderHighlightedContent()}
            </div>

            <audio
                ref={audioRef}
                src={src}
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={() => setIsPlaying(false)}
                controlsList="nodownload"
                onContextMenu={(e) => e.preventDefault()}
            />

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <button onClick={togglePlay} className="btn btn-primary" style={{ borderRadius: '50%', width: '3rem', height: '3rem', padding: 0, justifyContent: 'center' }}>
                    {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: isTrial ? 0.5 : 1 }}>
                    <Settings size={16} color="var(--text-muted)" />
                    <select
                        value={playbackSpeed}
                        onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                        disabled={isTrial}
                        style={{ 
                            background: 'rgba(0, 0, 0, 0.2)', 
                            border: '1px solid rgba(255, 255, 255, 0.2)', 
                            color: 'var(--text-main)', 
                            fontSize: '0.875rem', 
                            outline: 'none', 
                            cursor: isTrial ? 'not-allowed' : 'pointer',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px'
                        }}
                    >
                        <option value="0.75">0.75x</option>
                        <option value="1">1.0x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                        <option value="2">2.0x</option>
                    </select>
                    {isTrial && <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>(Paid Only)</span>}
                </div>

                <button
                    onClick={() => { audioRef.current.currentTime = 0; }}
                    className="btn btn-secondary"
                    style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem' }}
                >
                    <RotateCcw size={14} /> Reset
                </button>
            </div>
        </div>
    );
};

export default AudioPlayer;
