import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Grid,
  Box,
  Alert,
  CircularProgress,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import DeleteIcon from '@mui/icons-material/Delete';
import { generatePosts, postToLinkedIn, schedulePost, cancelScheduledPost, getScheduledPosts } from '../services/api';
import PostCard from '../components/PostCard';
import { useAuth } from '../contexts/AuthContext';

const GeneratePost: React.FC = () => {
  const { user } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLinkedInConnected, setIsLinkedInConnected] = useState(false);
  const [scheduledPosts, setScheduledPosts] = useState<any[]>([]);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [scheduledTime, setScheduledTime] = useState<Date | null>(null);
  const [postingStatus, setPostingStatus] = useState<{ [key: number]: 'idle' | 'posting' | 'scheduling' }>({});

  useEffect(() => {
    checkLinkedInConnection();
    loadScheduledPosts();
  }, []);

  const checkLinkedInConnection = async () => {
    try {
      const response = await fetch('/api/linkedin/check-connection');
      const data = await response.json();
      setIsLinkedInConnected(data.connected);
    } catch (error) {
      console.error('Error checking LinkedIn connection:', error);
      setIsLinkedInConnected(false);
    }
  };

  const loadScheduledPosts = async () => {
    try {
      const response = await getScheduledPosts();
      setScheduledPosts(response);
    } catch (error) {
      console.error('Error loading scheduled posts:', error);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const generatedPosts = await generatePosts(prompt);
      setPosts(generatedPosts);
    } catch (error) {
      setError('Failed to generate posts. Please try again.');
      console.error('Error generating posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePostNow = async (post: any) => {
    if (!isLinkedInConnected) {
      setError('Please connect your LinkedIn account first');
      return;
    }

    setPostingStatus(prev => ({ ...prev, [post.id]: 'posting' }));

    try {
      await postToLinkedIn(post);
      setPosts(prevPosts => prevPosts.filter(p => p.id !== post.id));
      setError(null);
    } catch (error) {
      setError('Failed to post to LinkedIn. Please try again.');
      console.error('Error posting to LinkedIn:', error);
    } finally {
      setPostingStatus(prev => ({ ...prev, [post.id]: 'idle' }));
    }
  };

  const handleSchedule = (post: any) => {
    setSelectedPost(post);
    setScheduledTime(null);
    setScheduleDialogOpen(true);
  };

  const handleScheduleConfirm = async () => {
    if (!selectedPost || !scheduledTime) return;

    setPostingStatus(prev => ({ ...prev, [selectedPost.id]: 'scheduling' }));

    try {
      await schedulePost(selectedPost.id, scheduledTime);
      setPosts(prevPosts => prevPosts.filter(p => p.id !== selectedPost.id));
      await loadScheduledPosts();
      setScheduleDialogOpen(false);
      setError(null);
    } catch (error) {
      setError('Failed to schedule post. Please try again.');
      console.error('Error scheduling post:', error);
    } finally {
      setPostingStatus(prev => ({ ...prev, [selectedPost.id]: 'idle' }));
    }
  };

  const handleCancelSchedule = async (postId: number) => {
    try {
      await cancelScheduledPost(postId);
      await loadScheduledPosts();
    } catch (error) {
      setError('Failed to cancel scheduled post. Please try again.');
      console.error('Error cancelling scheduled post:', error);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Generate LinkedIn Posts
          </Typography>

          {!isLinkedInConnected && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              Please connect your LinkedIn account to post content.
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                variant="outlined"
                label="Enter your prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                sx={{ minWidth: 200 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Generate Posts'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {scheduledPosts.length > 0 && (
          <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Scheduled Posts
            </Typography>
            <List>
              {scheduledPosts.map((post) => (
                <ListItem key={post.id}>
                  <ListItemText
                    primary={post.content}
                    secondary={`Scheduled for: ${new Date(post.scheduled_time).toLocaleString()}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleCancelSchedule(post.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        <Grid container spacing={3}>
          {posts.map((post) => (
            <Grid item xs={12} key={post.id}>
              <PostCard
                post={post}
                onPostNow={() => handlePostNow(post)}
                onSchedule={() => handleSchedule(post)}
                isPosting={postingStatus[post.id] === 'posting'}
                isScheduling={postingStatus[post.id] === 'scheduling'}
                isLinkedInConnected={isLinkedInConnected}
              />
            </Grid>
          ))}
        </Grid>

        <Dialog open={scheduleDialogOpen} onClose={() => setScheduleDialogOpen(false)}>
          <DialogTitle>Schedule Post</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <DateTimePicker
                label="Schedule Time"
                value={scheduledTime}
                onChange={(newValue) => setScheduledTime(newValue)}
                minDateTime={new Date()}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setScheduleDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleScheduleConfirm}
              disabled={!scheduledTime}
              variant="contained"
            >
              Schedule
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </LocalizationProvider>
  );
};

export default GeneratePost; 