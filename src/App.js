import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import SuggestedQuestions from "./components/SuggestedQuestions";
import ChatUI from "./components/ChatUI";
import companyLogo from './assets/companylogo.png'; // Ensure this path is correct
import botLogo from './assets/botlogo.png'; // Ensure this path is correct

function App({ profile, onLogout }) {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [messages, setMessages] = useState([
    {
      content: "Hello! I'm your Community Resources Guide bot. I can help you find information about community organizations, volunteer opportunities, fundraisers, and more in Durham, NC. How can I assist you today?",
      role: "assistant",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const messagesEndRef = useRef(null);
  const [isAssistantTyping, setIsAssistantTyping] = useState(false);

  const suggestedQuestions = [
    "Can you suggest some volunteer opportunities in the Durham area?",
    "Are there any ongoing fundraisers for local nonprofits in Durham?",
    "What resources are available for job seekers in Durham?",
    "Can you help me find mental health services in Durham?",
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
  };

  const sendMessage = async () => {
    const newMessage = {
      content: inputMessage,
      role: "user",
      timestamp: new Date().toISOString(),
    };
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);
    setInputMessage("");

    setIsAssistantTyping(true);

    const payload = {
      messages: newMessages.map(message => ({
        content: message.content,
        role: message.role,
        timestamp: message.timestamp,
      })),
    };

    console.log("Sending to server:", payload);

    try {
      const response = await axios.post("http://127.0.0.1:5000/ask", payload);

      const assistantMessage = {
        content: response.data.response,
        role: "assistant",
        timestamp: new Date().toISOString(),
      };

      setMessages([...newMessages, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        content: "Sorry, something went wrong. Please try again later.",
        role: "assistant",
        timestamp: new Date().toISOString(),
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setIsAssistantTyping(false);
    }
  };

  const handleQuestionSelect = (question) => {
    setInputMessage(question);
  };

  return (
    <div className="App">
      <header className="header">
        <img src={companyLogo} alt="Company Logo" className="company-logo-header" />
        <h1>Community Resource Bot</h1>
        {profile && (
          <div className="user-profile">
            <img src={profile.picture} alt={profile.name} className="user-picture" />
            <span className="user-name">{profile.name}</span>
            <button onClick={onLogout} className="logout-button">Logout</button>
          </div>
        )}
      </header>
      <div className="main-content">
        <div className="sidebar">
          <SuggestedQuestions
            suggestedQuestions={suggestedQuestions}
            onQuestionSelect={handleQuestionSelect}
          />
        </div>
        <div className="chat-container">
          <ChatUI
            messages={messages}
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            sendMessage={sendMessage}
            isAssistantTyping={isAssistantTyping}
            messagesEndRef={messagesEndRef}
          />
        </div>
      </div>
    </div>
  );
}

export default App;

