import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchChatResponse } from '../services/api';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
  font-family: 'Inter', sans-serif;
`;

const ChatHeader = styled.header`
  padding: 1.5rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid #e9ecef;
`;

const ChatTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3436;
  margin: 0;
`;

const ChatSubtitle = styled.p`
  font-size: 0.875rem;
  color: #636e72;
  margin: 0.25rem 0 0;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Message = styled(motion.div)`
  max-width: 80%;
  padding: 1rem;
  border-radius: 1rem;
  font-size: 0.9375rem;
  line-height: 1.5;
  background: ${props => props.$isUser ? '#6c5ce7' : 'white'};
  color: ${props => props.$isUser ? 'white' : '#2d3436'};
  align-self: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  border-bottom-right-radius: ${props => props.$isUser ? '0.25rem' : '1rem'};
  border-bottom-left-radius: ${props => props.$isUser ? '1rem' : '0.25rem'};
  box-shadow: ${props => !props.$isUser ? '0 2px 4px rgba(0, 0, 0, 0.05)' : 'none'};
`;

const InputContainer = styled.div`
  padding: 1.5rem;
  background: white;
  border-top: 1px solid #e9ecef;
`;

const InputForm = styled.form`
  display: flex;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
`;

const Input = styled.input`
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #6c5ce7;
    box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
  }
`;

const SendButton = styled(motion.button)`
  padding: 0.75rem 1.5rem;
  background: #6c5ce7;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #5f4fd1;
  }
  
  &:disabled {
    background: #a29bfe;
    cursor: not-allowed;
  }
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-radius: 1rem;
  align-self: flex-start;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const Dot = styled(motion.div)`
  width: 8px;
  height: 8px;
  background: #6c5ce7;
  border-radius: 50%;
`;

const ErrorMessage = styled.div`
  color: #e74c3c;
  background: #fef2f2;
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem;
  text-align: center;
`;

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      text: "👋 Hi! I'm your LinkedIn content assistant. I can help you create engaging posts and manage your content strategy. What would you like to post about today?",
      isUser: false
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);

    try {
      const response = await fetchChatResponse(userMessage, messages.map(msg => ({
        role: msg.isUser ? 'user' : 'assistant',
        content: msg.text
      })));

      const botResponse = response.response || 'Sorry, I could not generate a response.';
      
      setMessages(prev => [...prev, { text: botResponse, isUser: false }]);
      
      if (response.posts && response.posts.length > 0) {
        response.posts.forEach(post => {
          setMessages(prev => [...prev, { text: post, isUser: false }]);
        });
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = error.message || 'Sorry, there was an error processing your message. Please try again.';
      setError(errorMessage);
      setMessages(prev => [...prev, { 
        text: errorMessage, 
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>LinkedIn Post Generator</ChatTitle>
        <ChatSubtitle>Create engaging LinkedIn posts with AI assistance</ChatSubtitle>
      </ChatHeader>

      <MessagesContainer>
        <AnimatePresence>
          {messages.map((message, index) => (
            <Message
              key={index}
              $isUser={message.isUser}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {message.text}
            </Message>
          ))}
        </AnimatePresence>

        {isLoading && (
          <LoadingDots>
            <Dot
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0 }}
            />
            <Dot
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
            />
            <Dot
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }}
            />
          </LoadingDots>
        )}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <InputForm onSubmit={handleSubmit}>
          <Input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <SendButton
            type="submit"
            disabled={!input.trim() || isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Send
          </SendButton>
        </InputForm>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface; 