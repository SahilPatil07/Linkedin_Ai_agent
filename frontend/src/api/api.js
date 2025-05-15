export const fetchChatResponse = async (message, chatHistory = []) => {
  try {
    // Format chat history correctly
    const formattedHistory = chatHistory.map(msg => ({
      role: msg.isUser ? 'user' : 'assistant',
      content: msg.text
    }));

    const requestBody = {
      message: message.trim(),
      chat_history: formattedHistory
    };
    
    console.log('Sending request:', requestBody);  // Debug log

    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();
    console.log('Received response:', data);  // Debug log
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to get chat response');
    }

    if (!data.success) {
      throw new Error(data.error || 'Failed to get chat response');
    }

    return data.data.message;
  } catch (error) {
    console.error('Error fetching chat response:', error);
    throw error;
  }
}; 