import React from 'react';
import Logo from '../assets/logo.svg';

const Header = () => {
  return (
    <header className="header">
      <div className="flex items-center">
        <img src={Logo} alt="LinkedIn Post Generator" className="w-10 h-10 mr-3" />
        <h1 className="text-xl font-semibold text-gray-800">LinkedIn Post Generator</h1>
      </div>
      <div>
        <button 
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          History
        </button>
      </div>
    </header>
  );
};

export default Header; 