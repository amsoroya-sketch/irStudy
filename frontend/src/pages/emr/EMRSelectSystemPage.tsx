/**
 * EMR System Selector Page
 *
 * Allows user to choose between Epic and Cerner EMR systems for a session.
 *
 * Features:
 * - Visual cards for Epic and Cerner
 * - Theme preview
 * - System descriptions
 * - Remembers user preference
 */

import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Box,
  Chip,
  Paper,
} from '@mui/material';
import {
  LightMode as LightIcon,
  DarkMode as DarkIcon,
  BusinessCenter as EpicIcon,
  Science as CernerIcon,
} from '@mui/icons-material';

const EMRSelectSystemPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();

  useEffect(() => {
    document.title = 'Select EMR System - irStudy';
  }, []);

  const handleSystemSelect = (system: 'epic' | 'cerner') => {
    // Save preference to localStorage
    localStorage.setItem('emr_system_preference', system);

    // Navigate to selected system
    navigate(`/emr/${system}/${sessionId}`);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={0} sx={{ p: 3, mb: 4, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h4" gutterBottom>
          Select EMR System
        </Typography>
        <Typography variant="body1">
          Choose between Epic and Cerner EMR interfaces for your clinical documentation practice.
          Both systems provide the same functionality with different visual themes.
        </Typography>
      </Paper>

      <Grid container spacing={4}>
        {/* Epic Card */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card
            elevation={3}
            sx={{
              height: '100%',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 6,
              },
            }}
          >
            <CardActionArea onClick={() => handleSystemSelect('epic')} sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <EpicIcon sx={{ fontSize: 40, mr: 2, color: '#D4C5A9' }} />
                  <Typography variant="h5" component="h2">
                    Epic
                  </Typography>
                </Box>

                <Chip
                  icon={<LightIcon />}
                  label="Light Theme"
                  size="small"
                  sx={{ mb: 2, bgcolor: '#D4C5A9', color: '#2C2C2C' }}
                />

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Professional light interface with beige/tan color scheme. Used widely in
                  Australian hospitals and medical centers.
                </Typography>

                <Box
                  sx={{
                    p: 2,
                    bgcolor: '#FAFAF8',
                    border: '2px solid #D4C5A9',
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="caption" sx={{ color: '#2C2C2C' }}>
                    <strong>Features:</strong>
                    <br />
                    • Professional beige/tan theme
                    <br />
                    • Clean, structured layout
                    <br />
                    • Industry-standard interface
                    <br />• Ideal for day-time practice
                  </Typography>
                </Box>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>

        {/* Cerner Card */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card
            elevation={3}
            sx={{
              height: '100%',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 6,
              },
            }}
          >
            <CardActionArea onClick={() => handleSystemSelect('cerner')} sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CernerIcon sx={{ fontSize: 40, mr: 2, color: '#0066CC' }} />
                  <Typography variant="h5" component="h2">
                    Cerner
                  </Typography>
                </Box>

                <Chip
                  icon={<DarkIcon />}
                  label="Dark Theme"
                  size="small"
                  sx={{ mb: 2, bgcolor: '#0066CC', color: 'white' }}
                />

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Modern dark interface with blue accents. Reduces eye strain during extended
                  practice sessions.
                </Typography>

                <Box
                  sx={{
                    p: 2,
                    bgcolor: '#1E1E1E',
                    border: '2px solid #0066CC',
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="caption" sx={{ color: '#FFFFFF' }}>
                    <strong>Features:</strong>
                    <br />
                    • Dark mode blue theme
                    <br />
                    • Modern, sleek interface
                    <br />
                    • Reduces eye fatigue
                    <br />• Ideal for evening practice
                  </Typography>
                </Box>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Your selection will be saved for future sessions. You can change this preference anytime.
        </Typography>
      </Box>
    </Container>
  );
};

export default EMRSelectSystemPage;
