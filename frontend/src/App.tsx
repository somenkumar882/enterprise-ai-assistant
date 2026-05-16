import React from 'react';
import { ChatInterface } from './components/ChatInterface';

function App() {
  return (
    <div className="app-container">
      <header className="header">
        <div className="header-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
          Enterprise AI
        </div>
        <div className="header-stats">
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
            API Docs
          </a>
        </div>
      </header>
      
      <main style={{ flex: 1, overflow: 'hidden' }}>
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
