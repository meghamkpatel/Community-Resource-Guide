import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPaperPlane } from "@fortawesome/free-solid-svg-icons";
import ReactMarkdown from "react-markdown";  // Import ReactMarkdown
import botLogo from './assets/botlogo.png'; // Ensure this path is correct

function ChatUI({ messages, inputMessage, setInputMessage, sendMessage, isAssistantTyping, messagesEndRef }) {

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-ui">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div className={`message ${message.role.toLowerCase()}`} key={index}>
            {message.role.toLowerCase() === "assistant" && (
              <img src={botLogo} alt="Assistant" className="avatar" />
            )}
            <div className="message-content">
              {/* Use ReactMarkdown to render the message content safely */}
              <ReactMarkdown>{message.content}</ReactMarkdown>
              <div className="timestamp">{formatTimestamp(message.timestamp)}</div>
            </div>
          </div>
        ))}
        {isAssistantTyping && (
          <div className="typing-indicator">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Type a message"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage} disabled={!inputMessage.trim()}>
          <FontAwesomeIcon icon={faPaperPlane} />
        </button>
      </div>
    </div>
  );
}

export default ChatUI;

