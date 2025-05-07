import React from 'react';

const TopicSuggestion = ({ topic, onClick }) => {
  return (
    <div 
      className="p-3 mb-2 bg-white rounded-md cursor-pointer hover:bg-blue-50 border border-gray-200"
      onClick={() => onClick(topic)}
    >
      <p className="font-medium text-gray-800">{topic}</p>
    </div>
  );
};

const Sidebar = ({ onTopicSelect }) => {
  const topicSuggestions = [
    "Career Growth in Tech Industry",
    "Remote Work Best Practices",
    "Leadership Skills Development",
    "Digital Marketing Trends 2025",
    "Startup Funding Strategies",
    "Work-Life Balance Tips",
    "AI in Business Operations",
    "Personal Branding for Professionals",
    "Networking in Digital Age",
    "Employee Wellness Programs"
  ];

  return (
    <aside className="sidebar scrollbar-thin">
      <div className="p-4">
        <h2 className="mb-4 text-lg font-semibold">Topic Suggestions</h2>
        
        <div className="mb-6">
          {topicSuggestions.map((topic, index) => (
            <TopicSuggestion 
              key={index} 
              topic={topic} 
              onClick={onTopicSelect}
            />
          ))}
        </div>
        
        <div className="mt-8">
          <h3 className="mb-3 text-md font-medium">Tips for Great Posts</h3>
          <ul className="text-sm text-gray-600 space-y-2">
            <li>• Use personal stories to connect</li>
            <li>• Keep paragraphs short and scannable</li>
            <li>• Add 3-5 relevant hashtags</li>
            <li>• Ask engaging questions</li>
            <li>• Include a clear call-to-action</li>
          </ul>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar; 