import React, { useState, useRef, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to CampusAI! I am the official university assistant. Ask me about policies, search courses, download the handbook, or submit contact requests.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 11));
  const [currentPage, setCurrentPage] = useState('Home');
  const [currentUrl, setCurrentUrl] = useState('/');
  const [lastAction, setLastAction] = useState(null);

  const messagesEndRef = useRef(null);

  const suggestChips = [
    { label: 'Attendance Rule', text: 'What is the minimum attendance requirement?' },
    { label: 'Admission Documents', text: 'What documents are required for admission?' },
    { label: 'Exam Revaluation', text: 'What is the examination revaluation process?' },
    { label: 'Hostel Curfew', text: 'What are the hostel rules?' },
    { label: 'Download Handbook', text: 'Download the university handbook' },
    { label: 'Nav: Exams', text: 'Take me to the examinations page' },
    { label: 'Search AI Course', text: 'Search courses about Artificial Intelligence' },
    { label: 'Contact Office', text: 'I want to submit a contact request' }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleActionExecution = (action) => {
    if (!action) return;

    if (action.type === 'navigation') {
      setCurrentPage(action.data.page.charAt(0).toUpperCase() + action.data.page.slice(1));
      setCurrentUrl(action.data.url);
      setLastAction({
        type: 'navigation',
        message: `Successfully navigated to: ${action.data.url}`
      });
    } else if (action.type === 'download') {
      // Trigger download using the endpoint
      const downloadUrl = `${API_URL}${action.data.url}`;
      window.open(downloadUrl, '_blank');
      setLastAction({
        type: 'download',
        message: `Initiated download for: ${action.data.filename}`
      });
    } else if (action.type === 'contact_success') {
      setLastAction({
        type: 'contact',
        message: `Contact request submitted successfully!`
      });
    }
  };

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputValue.trim();
    if (!text) return;

    if (!textToSend) {
      setInputValue('');
    }

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Append user message
    setMessages(prev => [...prev, { role: 'user', content: text, time: timestamp }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to reach assistant.');
      }

      const data = await response.json();
      
      const assistantTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          time: assistantTimestamp,
          tool: data.tool,
          action: data.action,
          sources: data.sources
        }
      ]);

      // Execute actions if they are returning deterministic action payloads
      if (data.action) {
        handleActionExecution(data.action);
      }

    } catch (error) {
      const assistantTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.message || 'Unable to process the request right now.'}`,
          time: assistantTimestamp
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const submitFormConfirm = (confirm) => {
    if (confirm) {
      handleSendMessage('Yes, submit it.');
    } else {
      handleSendMessage('Cancel');
    }
  };

  return (
    <div className="app-container">
      {/* Upper Navigation Header bar */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo">C</div>
          <div className="brand-title-group">
            <h1>CampusAI</h1>
            <span className="brand-subtitle">University Assistant Portal</span>
          </div>
        </div>
        
        {/* Right side page indicator */}
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span className="status-text">Server Online</span>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.06)', padding: '6px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
            Active View: <strong style={{ color: 'var(--accent-color)' }}>{currentPage}</strong> ({currentUrl})
          </div>
        </div>
      </header>

      {/* Main split-pane content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Chat Pane */}
        <div className="chat-window" style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRight: '1px solid var(--border-color)' }}>
          <div className="message-list">
            {messages.map((msg, index) => (
              <div key={index} className={`message-item ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                  
                  {/* Sources Grounding Visualizer */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="payload-box">
                      <div className="payload-title">📚 Retrieved Handbook Context</div>
                      {msg.sources.map((src, sIdx) => (
                        <div key={sIdx} className="source-item">
                          <div className="source-header">{src.section} (Match Score: {src.score.toFixed(2)})</div>
                          <div className="payload-content">{src.text}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Active Tool invocation Visualizer */}
                  {msg.tool && (
                    <div className="payload-box" style={{ borderColor: 'rgba(99, 102, 241, 0.4)' }}>
                      <div className="payload-title" style={{ color: '#818cf8' }}>🛠️ Tool Triggered</div>
                      <div className="payload-content" style={{ fontFamily: 'monospace' }}>
                        {msg.tool}()
                      </div>
                    </div>
                  )}

                  {/* Confirmation flow details */}
                  {msg.action && msg.action.type === 'contact_confirmation' && (
                    <div className="payload-box" style={{ borderColor: 'var(--warning)' }}>
                      <div className="payload-title" style={{ color: 'var(--warning)' }}>⚠️ Confirmation Required</div>
                      <div className="payload-content">Please review the details above. Ready to submit?</div>
                      <div className="action-confirm-box">
                        <button className="action-btn" onClick={() => submitFormConfirm(true)}>Confirm & Send</button>
                        <button className="action-btn cancel" onClick={() => submitFormConfirm(false)}>Cancel</button>
                      </div>
                    </div>
                  )}
                </div>
                <span className="message-time">{msg.time}</span>
              </div>
            ))}

            {isLoading && (
              <div className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            {/* Suggestion Chips */}
            <div className="suggest-chips">
              {suggestChips.map((chip, idx) => (
                <button
                  key={idx}
                  className="suggest-chip"
                  onClick={() => handleSendMessage(chip.text)}
                  disabled={isLoading}
                >
                  {chip.label}
                </button>
              ))}
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="input-form"
            >
              <input
                type="text"
                className="chat-input"
                placeholder="Ask about policies, rules, courses, or type 'submit contact request'..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="submit"
                className="send-button"
                disabled={isLoading || !inputValue.trim()}
              >
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Live Portal Dashboard Preview Pane */}
        <div style={{ width: '380px', background: 'rgba(5, 2, 15, 0.4)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '8px' }}>Portal Live Feed</h2>
            <p style={{ fontSize: '0.8rem', color: var(--text-secondary) }}>
              Simulates direct client actions triggered by the AI assistant payloads.
            </p>
          </div>

          {/* Last Action details */}
          <div style={{ flex: 1, border: '1px solid var(--border-color)', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <h3 style={{ fontSize: '0.9rem', color: '#a5b4fc', fontWeight: 600 }}>Active Event Monitor</h3>
            {lastAction ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', animation: 'fadeIn 0.5s ease' }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: lastAction.type === 'download' ? '#10b981' : '#6366f1', fontWeight: 700 }}>
                  [{lastAction.type}] event
                </div>
                <div style={{ fontSize: '0.85rem', color: '#f8fafc', lineHeight: 1.4 }}>
                  {lastAction.message}
                </div>
              </div>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic', margin: 'auto' }}>
                No external action triggered yet.
              </div>
            )}
          </div>

          {/* Handbook Download Card */}
          <div style={{ border: '1px solid rgba(16,185,129,0.15)', borderRadius: '12px', background: 'rgba(16,185,129,0.03)', padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <h4 style={{ fontSize: '0.85rem', color: '#34d399', fontWeight: 700 }}>Quick Resource Access</h4>
            <p style={{ fontSize: '0.75rem', color: var(--text-secondary) }}>
              Click here to manually fetch the official handbook.
            </p>
            <a
              href={`${API_URL}/downloads/university_handbook.pdf`}
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'inline-block',
                textAlign: 'center',
                background: '#10b981',
                color: '#fff',
                fontSize: '0.8rem',
                fontWeight: 600,
                textDecoration: 'none',
                padding: '8px 12px',
                borderRadius: '8px',
                marginTop: '6px',
                transition: 'background 0.2s'
              }}
              onMouseOver={(e) => (e.target.style.background = '#059669')}
              onMouseOut={(e) => (e.target.style.background = '#10b981')}
            >
              Download PDF Handbook
            </a>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
