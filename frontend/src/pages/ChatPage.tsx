import React, { useState } from 'react';
import { Container, Box, Typography, Paper } from '@mui/material';
import ChatInterface from '../components/ChatInterface';
import { Message } from '../types/chat';
import { sendMessage } from '../services/api';

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    try {
      setIsLoading(true);
      
      // Add user message
      const userMessage: Message = { role: 'user', content: message };
      setMessages(prev => [...prev, userMessage]);

      // Send to API
      const response = await sendMessage(message);
      
      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.status === 'success' ? response.message : response.error || 'An error occurred'
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, an error occurred while processing your request.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ height: '100vh', py: 4 }}>
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Chat Assistant
        </Typography>
        
        <Paper 
          elevation={3} 
          sx={{ 
            flex: 1,
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#ffffff'
          }}
        >
          <ChatInterface
            onSendMessage={handleSendMessage}
            messages={messages}
            isLoading={isLoading}
          />
        </Paper>
      </Box>
    </Container>
  );
};

export default ChatPage; 