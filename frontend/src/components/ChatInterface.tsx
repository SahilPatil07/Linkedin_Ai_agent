import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { Message } from '../types/chat';

interface ChatInterfaceProps {
  onSendMessage: (message: string) => Promise<void>;
  messages: Message[];
  isLoading: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onSendMessage,
  messages,
  isLoading,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      const message = input.trim();
      setInput('');
      await onSendMessage(message);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          mb: 2,
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {messages.map((message, index) => (
          <Paper
            key={index}
            elevation={1}
            sx={{
              p: 2,
              maxWidth: '80%',
              alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: message.role === 'user' ? '#e3f2fd' : '#f5f5f5',
            }}
          >
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {message.content}
            </Typography>
          </Paper>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          display: 'flex',
          gap: 1,
          p: 2,
          backgroundColor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          size="small"
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!input.trim() || isLoading}
          sx={{ minWidth: 48 }}
        >
          {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
        </IconButton>
      </Box>
    </Box>
  );
};

export default ChatInterface; 