import React, { useState, useEffect } from 'react';
import './WelcomeMessage.css';

const WelcomeMessage = () => {
  const [show, setShow] = useState(true);

  useEffect(() => {
    const hasShown = localStorage.getItem('welcomeShown');
    if (hasShown) {
      setShow(false);
    } else {
      localStorage.setItem('welcomeShown', 'true');
      setTimeout(() => setShow(false), 5000);
    }
  }, []);

  if (!show) return null;

  return (
    <div className="welcome-message">
      <div className="welcome-content">
        <h2>👋 Welcome to LinkedIn Post Generator!</h2>
        <p>I'm your AI assistant, ready to help you create engaging professional content.</p>
      </div>
    </div>
  );
};

export default WelcomeMessage;