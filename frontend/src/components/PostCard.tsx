import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Chip,
  Alert,
  Snackbar,
  CircularProgress,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { format } from 'date-fns';
import { api } from '../services/api';

interface PostCardProps {
  post: {
    id?: number;
    content: string;
    status: string;
    visibility: string;
    created_at: string;
    scheduled_time?: string;
  };
  onPostNow: (postId: number) => Promise<void>;
  onSchedule: (postId: number, scheduledTime: Date) => Promise<void>;
}

const PostCard: React.FC<PostCardProps> = ({ post, onPostNow, onSchedule }) => {
  const [isScheduleDialogOpen, setIsScheduleDialogOpen] = useState(false);
  const [scheduledTime, setScheduledTime] = useState<Date | null>(new Date());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handlePostNow = async () => {
    if (!post.id) return;
    setIsLoading(true);
    setError(null);
    try {
      await onPostNow(post.id);
      setSuccess('Post published successfully!');
    } catch (err: any) {
      setError(err.message || 'Failed to post to LinkedIn');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSchedule = async () => {
    if (!post.id || !scheduledTime) return;
    setIsLoading(true);
    setError(null);
    try {
      await onSchedule(post.id, scheduledTime);
      setSuccess('Post scheduled successfully!');
      setIsScheduleDialogOpen(false);
    } catch (err: any) {
      setError(err.message || 'Failed to schedule post');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(null);
  };

  const isPostDisabled = isLoading || post.status === 'POSTED';
  const isScheduleDisabled = isLoading || post.status === 'POSTED';

  return (
    <>
      <Card sx={{ maxWidth: 600, mb: 2, position: 'relative' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Chip 
              label={post.status} 
              color={
                post.status === 'POSTED' ? 'success' :
                post.status === 'SCHEDULED' ? 'warning' :
                'default'
              }
            />
            <Chip label={post.visibility} color="primary" />
          </Box>
          
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
            {post.content}
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            Created: {format(new Date(post.created_at), 'PPp')}
          </Typography>
          
          {post.scheduled_time && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
              Scheduled for: {format(new Date(post.scheduled_time), 'PPp')}
            </Typography>
          )}
        </CardContent>

        <CardActions sx={{ justifyContent: 'flex-end', gap: 1, p: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handlePostNow}
            disabled={isPostDisabled}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {isLoading ? 'Posting...' : 'Post Now'}
          </Button>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => setIsScheduleDialogOpen(true)}
            disabled={isScheduleDisabled}
          >
            Schedule
          </Button>
        </CardActions>
      </Card>

      <Dialog 
        open={isScheduleDialogOpen} 
        onClose={() => !isLoading && setIsScheduleDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Schedule Post</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <DateTimePicker
              label="Schedule Time"
              value={scheduledTime}
              onChange={(newValue) => setScheduledTime(newValue)}
              renderInput={(params) => <TextField {...params} fullWidth />}
              minDateTime={new Date()}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setIsScheduleDialogOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSchedule}
            variant="contained"
            disabled={!scheduledTime || isLoading}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {isLoading ? 'Scheduling...' : 'Schedule'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={handleCloseSnackbar}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar 
        open={!!success} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={handleCloseSnackbar}>
          {success}
        </Alert>
      </Snackbar>
    </>
  );
};

export default PostCard; 