import React from 'react';

const PostPreview = ({ post, onClose, onPost }) => {
  if (!post) return null;

  // Format the content for display
  const formatContent = (content) => {
    if (!content) return '';
    
    // Process hashtags
    return content.replace(
      /(#\w+)/g, 
      '<span class="linkedin-hashtag">$1</span>'
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Preview Post</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-6">
          <div className="mb-4 p-4 border border-gray-200 rounded-lg bg-white linkedin-text">
            <div dangerouslySetInnerHTML={{ __html: formatContent(post) }} />
          </div>
          
          <div className="flex justify-end space-x-3 mt-4">
            <button 
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </button>
            <button 
              onClick={onPost}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Post to LinkedIn
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostPreview; 