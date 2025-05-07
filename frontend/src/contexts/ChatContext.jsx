import React, { createContext, useState, useContext, useEffect } from 'react';
import { fetchChatResponse, setupChatWebSocket } from '../services/api';

const ChatContext = createContext();

export const useChatContext = () => useContext(ChatContext);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [currentPostContent, setCurrentPostContent] = useState(null);
  const [showPostPreview, setShowPostPreview] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const [useWebsocket, setUseWebsocket] = useState(true);

  // Initialize websocket connection
  useEffect(() => {
    if (useWebsocket) {
      const ws = setupChatWebSocket({
        onMessage: handleWebSocketMessage,
        onClose: () => console.log('WebSocket closed'),
        onError: (error) => console.error('WebSocket error:', error)
      });
      
      setWebsocket(ws);
      
      // Clean up on unmount
      return () => {
        if (ws) ws.close();
      };
    }
  }, [useWebsocket]);

  // Handle incoming WebSocket messages
  const handleWebSocketMessage = (data) => {
    if (data.error) {
      console.error('Error from WebSocket:', data.error);
      setIsTyping(false);
      return;
    }
    
    if (data.type === 'complete') {
      // Final message with complete response
      setIsTyping(false);
      
      // Check if we should post
      if (data.should_post && data.post_content) {
        setCurrentPostContent(data.post_content);
        setShowPostPreview(true);
      }
      
      return;
    }
    
    // Handle content chunks
    if (data.content) {
      setMessages(prev => {
        const lastMessageIndex = prev.length - 1;
        
        // If there's no assistant message yet, create a new one
        if (lastMessageIndex < 0 || prev[lastMessageIndex].role !== 'assistant') {
          return [...prev, { role: 'assistant', content: data.content }];
        }
        
        // Otherwise, append to the existing assistant message
        const updatedMessages = [...prev];
        updatedMessages[lastMessageIndex] = {
          ...updatedMessages[lastMessageIndex],
          content: updatedMessages[lastMessageIndex].content + data.content
        };
        
        return updatedMessages;
      });
    }
  };

  // Send a message through REST API
  const sendMessageREST = async (messageText) => {
    try {
      setIsTyping(true);
      
      // Add user message to state
      const userMessage = { role: 'user', content: messageText };
      setMessages(prev => [...prev, userMessage]);
      
      // Prepare chat history for API
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Send request to API
      const response = await fetchChatResponse(messageText, chatHistory);
      
      // Add assistant response to state
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: response.message,
          shouldPost: response.should_post 
        }
      ]);
      
      // Check if we should show post preview
      if (response.should_post && response.post_content) {
        setCurrentPostContent(response.post_content);
        setShowPostPreview(true);
      }
      
      setIsTyping(false);
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
    }
  };

  // Send a message through WebSocket
  const sendMessageWS = (messageText) => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      // Fallback to REST API
      sendMessageREST(messageText);
      return;
    }
    
    try {
      setIsTyping(true);
      
      // Add user message to state
      const userMessage = { role: 'user', content: messageText };
      setMessages(prev => [...prev, userMessage]);
      
      // Prepare chat history for API
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Send message through WebSocket
      websocket.send(JSON.stringify({
        message: messageText,
        chat_history: chatHistory
      }));
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      setIsTyping(false);
    }
  };

  // Send a message (using WebSocket or REST API)
  const sendMessage = (messageText) => {
    if (useWebsocket && websocket) {
      sendMessageWS(messageText);
    } else {
      sendMessageREST(messageText);
    }
  };

  // Post to LinkedIn (simulated)
  const postToLinkedIn = () => {
    // Here you would integrate with LinkedIn API
    // For now, we'll just simulate a successful post
    alert('Post shared successfully to LinkedIn!');
    setShowPostPreview(false);
  };

  const value = {
    messages,
    isTyping,
    sendMessage,
    currentPostContent,
    showPostPreview,
    setShowPostPreview,
    postToLinkedIn,
    useWebsocket,
    setUseWebsocket
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}; 