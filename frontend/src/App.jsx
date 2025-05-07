import React from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatBox from './components/ChatBox';
import ChatInput from './components/ChatInput';
import PostPreview from './components/PostPreview';
import { ChatProvider, useChatContext } from './contexts/ChatContext';
import './styles/App.css';

const ChatContainer = () => {
  const { 
    messages, 
    isTyping, 
    sendMessage, 
    showPostPreview, 
    setShowPostPreview,
    currentPostContent,
    postToLinkedIn
  } = useChatContext();

  const handleTopicSelect = (topic) => {
    sendMessage(topic);
  };

  return (
    <div className="app-container">
      <Header />
      <div className="main-content">
        <Sidebar onTopicSelect={handleTopicSelect} />
        <div className="chat-container">
          <ChatBox messages={messages} isTyping={isTyping} />
          <ChatInput onSendMessage={sendMessage} isLoading={isTyping} />
        </div>
      </div>
      
      {showPostPreview && (
        <PostPreview 
          post={currentPostContent} 
          onClose={() => setShowPostPreview(false)} 
          onPost={postToLinkedIn}
        />
      )}
    </div>
  );
};

const App = () => {
  return (
    <ChatProvider>
      <ChatContainer />
    </ChatProvider>
  );
};

export default App; 