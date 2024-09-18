import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { FaGithub } from "react-icons/fa";
import "./App.css";



function App() {
  const [message, setMessage] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  const messagesEndRef = useRef(null);
  const [isFetching, setIsFetching] = useState(false);

  useEffect(() => {
    scrollToBottom();
  }, [message]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
  };

  const fetchMessage = async () => {
    setIsFetching(true);

    try {
      const response = await axios.get("http://ip.jsontest.com/");
      setMessage(response.data.ip);
    } catch (error) {
      console.error("Error fetching message:", error);
      setMessage(
        "⚠️ An error occurred while fetching the message. Please try again later."
      );
    } finally {
      setIsFetching(false);
    }
  };
  
  
  
  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  const handleSendMessage = () => {
    fetchMessage();
    setInputMessage("");
  };

  return (
    <div className="App">
      <div className="headline">
        <h1>⚡ Simple Fetch App ⚡</h1>
      </div>
      <div className="chat-container">
        <div className="chat-ui">
          <div className="messages">
            {message && (
              <div className="message">
                <span>{message}</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="input-container">
            <input
              type="text"
              value={inputMessage}
              onChange={handleInputChange}
              placeholder="Type a message..."
            />
            <button onClick={handleSendMessage} disabled={isFetching}>
              {isFetching ? "Fetching..." : "Send"}
            </button>
          </div>
        </div>
      </div>
      <div className="footer">
        <a
          href="https://github.com/fatihbaltaci/chatgpt-clone"
          target="_blank"
          rel="noopener noreferrer"
        >
          <FaGithub className="icon" />
          View on GitHub
        </a>
      </div>
    </div>
  );
}

export default App;

