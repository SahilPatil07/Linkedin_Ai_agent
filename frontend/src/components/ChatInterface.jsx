import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchChatResponse } from '../api/api';

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

const PostButton = styled(motion.button)`
  padding: 0.5rem 1rem;
  background: #0077b5;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 0.5rem;
  
  &:hover {
    background: #006399;
  }
  
  &:disabled {
    background: #a0a0a0;
    cursor: not-allowed;
  }
`;

const MessageActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
`;

const LoginButton = styled(motion.button)`
  padding: 0.75rem 1.5rem;
  background: #0077b5;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 1rem;
  
  &:hover {
    background: #006399;
  }
`;

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      text: "👋 Hi! I'm your LinkedIn content assistant. Please login to LinkedIn to start posting.",
      isUser: false
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      setIsLoading(true);
      setError(null);

      // Add user message to chat
      const userMessage = { text: input.trim(), isUser: true };
      setMessages(prev => [...prev, userMessage]);
      setInput('');

      // Get AI response
      const response = await fetchChatResponse(input, messages);
      
      // Add AI response to chat
      if (response) {
        setMessages(prev => [...prev, { 
          text: response, 
          isUser: false 
        }]);
      } else {
        throw new Error('No response received from the AI');
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

  const handlePostToLinkedIn = async (content) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8000/api/v1/posts/post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          visibility: 'PUBLIC'
        })
      });

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to post to LinkedIn');
      }

      // Add success message to chat
      setMessages(prev => [...prev, {
        text: `✅ ${data.message || 'Successfully posted to LinkedIn!'}`,
        isUser: false
      }]);

    } catch (error) {
      console.error('Error posting to LinkedIn:', error);
      setError(error.message || 'Failed to post to LinkedIn');
      setMessages(prev => [...prev, {
        text: `❌ ${error.message || 'Failed to post to LinkedIn'}`,
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLinkedInLogin = () => {
    window.location.href = 'http://localhost:8000/api/v1/auth/linkedin/login';
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>LinkedIn Post Generator</ChatTitle>
        <ChatSubtitle>Create and post engaging LinkedIn content with AI assistance</ChatSubtitle>
        {!isAuthenticated && (
          <LoginButton
            onClick={handleLinkedInLogin}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Login with LinkedIn
          </LoginButton>
        )}
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
              {!message.isUser && message.text.length > 50 && (
                <MessageActions>
                  <PostButton
                    onClick={() => handlePostToLinkedIn(message.text)}
                    disabled={isLoading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Post to LinkedIn
                  </PostButton>
                </MessageActions>
              )}
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