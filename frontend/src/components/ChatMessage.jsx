import React from 'react';

const ChatMessage = ({ message, isUser, isPosting }) => {
  // Format the message content to properly display hashtags
  const formatContent = (content) => {
    if (!content) return '';
    
    // Split by newlines and process each line
    const lines = content.split('\n');
    
    return lines.map((line, lineIndex) => {
      // Handle hashtags
      const processedLine = line.replace(
        /(#\w+)/g, 
        '<span class="linkedin-hashtag">$1</span>'
      );
      
      return (
        <React.Fragment key={lineIndex}>
          <span dangerouslySetInnerHTML={{ __html: processedLine }} />
          {lineIndex < lines.length - 1 && <br />}
        </React.Fragment>
      );
    });
  };

  return (
    <div className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-3xl p-4 rounded-lg ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-white text-gray-800 border border-gray-200'
        } ${isPosting ? 'post-card' : ''}`}
      >
        {isPosting && (
          <div className="mb-2 pb-2 border-b border-gray-200">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Ready to Post
            </span>
          </div>
        )}
        
        <div className={`linkedin-text ${isUser ? 'text-white' : 'text-gray-800'}`}>
          {formatContent(message)}
        </div>
        
        {isPosting && (
          <div className="mt-3 text-right">
            <button className="px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
              Post to LinkedIn
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage; 