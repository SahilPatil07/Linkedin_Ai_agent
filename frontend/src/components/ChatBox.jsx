import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

const ChatBox = ({ messages, isTyping }) => {
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-messages scrollbar-thin">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="text-center p-8 bg-white rounded-xl shadow-sm max-w-lg">
            <h2 className="text-xl font-semibold mb-3 text-gray-800">Welcome to LinkedIn Post Generator</h2>
            <p className="text-gray-600 mb-6">
              Generate engaging LinkedIn posts in Hinglish. Simply type a topic or choose from the suggestions in the sidebar.
            </p>
            <p className="text-sm text-gray-500">
              Examples: "Career growth tips", "Work-life balance", "Leadership skills"
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <ChatMessage 
              key={index} 
              message={msg.content} 
              isUser={msg.role === 'user'} 
              isPosting={msg.shouldPost}
            />
          ))}
          
          {isTyping && (
            <div className="mb-4 flex justify-start">
              <div className="max-w-3xl p-4 rounded-lg bg-white border border-gray-200">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};

export default ChatBox; 