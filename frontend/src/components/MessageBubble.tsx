import React from 'react';
import './MessageBubble.css';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  isCached?: boolean;
  responseId?: string;
  sources?: any[];
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  content,
  isCached,
  responseId,
  sources,
}) => {
  const isUser = role === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        <div className="message-text">
          {content.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
        
        {!isUser && (
          <div className="message-meta">
            {isCached !== undefined && (
              <span className={`badge ${isCached ? 'cached' : 'fresh'}`}>
                {isCached ? '⚡ CACHED' : '✨ FRESH'}
              </span>
            )}
            {responseId && (
              <span className="response-id">
                ID: {responseId.substring(0, 8)}
              </span>
            )}
          </div>
        )}

        {!isUser && sources && sources.length > 0 && (
          <div className="message-sources">
            <h4>Sources:</h4>
            <ul>
              {sources.map((source, idx) => (
                <li key={idx}>
                  {source.title || source.source || `Document ${idx + 1}`}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
