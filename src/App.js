import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import SuggestedQuestions from "./components/SuggestedQuestions";
import ChatUI from "./components/ChatUI";
import companyLogo from './assets/companylogo.png'; // Ensure this path is correct
import botLogo from './assets/botlogo.png'; // Ensure this path is correct
import ReactMarkdown from 'react-markdown';  // Import the React Markdown library



function App() {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [messages, setMessages] = useState([
    {
      content: "Welcome to the Community Resource Guide! I'm here to help you navigate and connect with essential services in your community. Whether you're in need of housing support, food assistance, healthcare, job opportunities, legal aid, or more, My goal is to make it easy for you to find the help you need, when you need it. Simply tell me what you're looking for, and I'll assist you every step of the way!",
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
      const response = await axios.post('http://3.138.158.238:8000/ask', payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
      console.log(response);
      
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
            renderMessage={(message) => (
              // Use ReactMarkdown to process the message content
              <ReactMarkdown>
                {message.content}
              </ReactMarkdown>
            )}
          />
        </div>
      </div>
    </div>
  );
}

export default App;

