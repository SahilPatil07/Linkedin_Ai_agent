import React, { useState, useEffect } from 'react';

const LinkedInPost: React.FC = () => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check authentication status on component mount
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/auth/linkedin/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const data = await response.json();
      setIsAuthenticated(data.success);
      
      if (!data.success) {
        setError(data.message || 'LinkedIn authentication required');
      } else {
        setError(null);
      }
    } catch (err) {
      setIsAuthenticated(false);
      setError('Failed to verify LinkedIn authentication');
    } finally {
      setLoading(false);
    }
  };

  const handleLinkedInLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/v1/auth/linkedin/login');
      const data = await response.json();
      
      if (data.url) {
        // Store current URL to return to after auth
        localStorage.setItem('returnUrl', window.location.href);
        window.location.href = data.url;
      } else {
        setError('Failed to get LinkedIn login URL');
      }
    } catch (err) {
      setError('Failed to initiate LinkedIn login');
    } finally {
      setLoading(false);
    }
  };

  const handlePost = async () => {
    if (!content) {
      setError('Please enter some content for your post');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/post-to-linkedin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ content })
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.needs_auth) {
          setIsAuthenticated(false);
          setError('LinkedIn authentication required. Please login first.');
          return;
        }
        throw new Error(data.error || 'Failed to post to LinkedIn');
      }

      setSuccess('Post successfully published to LinkedIn!');
      setContent('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to post to LinkedIn');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <h2 className="text-2xl font-bold mb-4">LinkedIn Authentication Required</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
          <p className="text-blue-700 mb-4">
            You need to connect your LinkedIn account before you can post.
          </p>
          <button
            onClick={handleLinkedInLogin}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
          >
            Connect LinkedIn Account
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Create LinkedIn Post</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}
      
      <div className="mb-4">
        <textarea
          className="w-full p-2 border rounded"
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your LinkedIn post here..."
        />
      </div>
      
      <div className="flex gap-4">
        <button
          className={`bg-blue-500 text-white px-4 py-2 rounded ${
            loading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'
          }`}
          onClick={handlePost}
          disabled={loading}
        >
          {loading ? 'Posting...' : 'Post to LinkedIn'}
        </button>
        
        <button
          onClick={handleLinkedInLogin}
          className="text-blue-500 hover:text-blue-600"
        >
          Reconnect LinkedIn
        </button>
      </div>
    </div>
  );
};

export default LinkedInPost; 