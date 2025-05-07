import React from 'react';
import './App.css';

const PostCard = ({ post, index, onSelect, onSchedule }) => {
  // Format the post content
  const formatPost = (content) => {
    const lines = content.split('\n');
    const title = lines[0];
    const paragraphs = lines.slice(1).filter(line => line.trim());
    
    return { title, paragraphs };
  };

  const { title, paragraphs } = formatPost(post.response);
  
  // Extract hashtags from the last paragraph
  const hashtags = post.response.match(/#\w+/g) || [];
  
  return (
    <div className="post-card">
      <div className="post-number">#{index + 1}</div>
      
      <div className="post-title">
        {title}
      </div>
      
      <div className="post-body">
        {paragraphs.map((paragraph, i) => (
          <p key={i} className="post-paragraph">
            {paragraph}
          </p>
        ))}
      </div>
      
      <div className="post-hashtags">
        {hashtags.map((tag, i) => (
          <span key={i} className="hashtag">
            {tag}
          </span>
        ))}
      </div>
      
      <div className="post-actions">
        <button 
          className="select-btn"
          onClick={() => onSelect(index)}
        >
          <span>✅</span>
          Select This Post
        </button>
        
        <button 
          className="schedule-btn"
          onClick={() => onSchedule(index)}
        >
          <span>📅</span>
          Schedule
        </button>
      </div>
    </div>
  );
};

const PostGrid = ({ posts, onSelect, onSchedule }) => {
  return (
    <div className="card-grid">
      {posts.map((post, index) => (
        <PostCard
          key={index}
          post={post}
          index={index}
          onSelect={onSelect}
          onSchedule={onSchedule}
        />
      ))}
    </div>
  );
};

export default PostGrid;