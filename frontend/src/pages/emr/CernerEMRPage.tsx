/**
 * Cerner EMR Session Page
 *
 * Full Cerner EMR interface for clinical documentation practice.
 *
 * Features:
 * - Cerner theme (dark mode with blue accents)
 * - SOAP note editor with auto-save
 * - Patient banner, sidebar, app bar
 * - Prescription and pathology panels
 * - Real-time validation
 * - Auto-save every 5 seconds
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { Box, CircularProgress, Alert, Container, Typography } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { useQuery, useMutation } from '@tanstack/react-query';
import { cernerTheme } from '../../themes/cernerTheme';
import {
  CernerAppBar,
  CernerSidebar,
  CernerPatientBanner,
  CernerSOAPEditor,
  CernerPrescriptionPanel,
  CernerPathologyPanel,
} from '../../components/emr/cerner';
import { useAutoSave } from '../../hooks/useAutoSave';
import axiosInstance from '../../utils/axiosInstance';
import { EMRSession, SOAPNoteDraft, MockPatient } from '../../types/emr';

type SidebarSection = 'chart' | 'orders' | 'results';

const CernerEMRPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [activeSection, setActiveSection] = useState<SidebarSection>('chart');
  const [sessionData, setSessionData] = useState<SOAPNoteDraft>({
    subjective: '',
    objective: '',
    assessment: '',
    plan: '',
    prescriptions: [],
    pathology_orders: [],
    imaging_orders: [],
  });

  // Fetch session data
  const {
    data: session,
    isLoading,
    error,
  } = useQuery<EMRSession>({
    queryKey: ['emr-session', sessionId],
    queryFn: async () => {
      const response = await axiosInstance.get(`/api/v1/emr/sessions/${sessionId}`);
      return response.data;
    },
    enabled: !!sessionId,
  });

  // Fetch patient data
  const { data: patient } = useQuery<MockPatient>({
    queryKey: ['patient', session?.patient_id],
    queryFn: async () => {
      const res = await axiosInstance.get(`/api/v1/patients/${session?.patient_id}`);
      return res.data;
    },
    enabled: !!session?.patient_id,
  });

  // Load existing session data
  useEffect(() => {
    if (session?.session_data) {
      setSessionData(session.session_data);
    }
  }, [session]);

  // Auto-save hook (debounced, 5s delay)
  const { debouncedSave, saveStatus } = useAutoSave({
    sessionId: sessionId || '',
    debounceMs: 5000,
    maxWaitMs: 30000,
  });

  // Handler for SOAP field changes
  const handleSOAPChange = (field: keyof SOAPNoteDraft, value: string) => {
    const newData = { ...sessionData, [field]: value };
    setSessionData(newData);
    debouncedSave(newData);
  };

  // Handler for prescription changes
  const handlePrescriptionChange = (prescriptions: any[]) => {
    const newData = { ...sessionData, prescriptions };
    setSessionData(newData);
    debouncedSave(newData);
  };

  // Handler for pathology order changes
  const handlePathologyChange = (pathology_orders: any[]) => {
    const newData = { ...sessionData, pathology_orders };
    setSessionData(newData);
    debouncedSave(newData);
  };

  // Submit session mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      const response = await axiosInstance.post(
        `/api/v1/emr/sessions/${sessionId}/submit`,
        { session_data: sessionData }
      );
      return response.data;
    },
    onSuccess: () => {
      navigate(`/emr/validation/${sessionId}`);
    },
  });

  const handleSave = () => {
    debouncedSave(sessionData);
  };

  const handleExit = () => {
    navigate('/dashboard');
  };

  if (isLoading) {
    return (
      <ThemeProvider theme={cernerTheme}>
        <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
          <CircularProgress />
        </Container>
      </ThemeProvider>
    );
  }

  if (error) {
    return (
      <ThemeProvider theme={cernerTheme}>
        <Container sx={{ py: 4 }}>
          <Alert severity="error">Failed to load EMR session: {(error as Error).message}</Alert>
        </Container>
      </ThemeProvider>
    );
  }

  if (!session || !patient) {
    return null;
  }

  return (
    <ThemeProvider theme={cernerTheme}>
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* Sidebar */}
        <CernerSidebar activeSection={activeSection} onSectionChange={setActiveSection} />

        {/* Main Content Area */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* App Bar */}
          <CernerAppBar
            patient={patient}
            onSave={handleSave}
            onSubmit={() => submitMutation.mutate()}
            onExit={handleExit}
            autoSaveStatus={saveStatus}
            isSubmitting={submitMutation.isPending}
          />

          {/* Patient Banner */}
          <CernerPatientBanner patient={patient} />

          {/* OSCE Conversion Indicator */}
          {session?.source_osce_attempt_id && session?.conversion_metadata && (
            <Alert severity="info" sx={{ mx: 2, mt: 2 }} icon={<InfoIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2">
                  This EMR session was auto-filled from your OSCE conversation (
                  {Math.round((session.conversion_metadata.pre_fill_percentage || 0) * 100)}%
                  pre-filled). Review and refine the content before submitting.
                </Typography>
              </Box>
            </Alert>
          )}

          {/* Scrollable Content */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
            {/* SOAP Note Editor */}
            <CernerSOAPEditor
              sessionId={sessionId || ''}
              draft={sessionData}
              onChange={handleSOAPChange}
            />

            {/* Prescription Panel */}
            <Box sx={{ mt: 2 }}>
              <CernerPrescriptionPanel
                prescriptions={sessionData.prescriptions}
                onChange={handlePrescriptionChange}
              />
            </Box>

            {/* Pathology Panel */}
            <Box sx={{ mt: 2 }}>
              <CernerPathologyPanel
                pathologyOrders={sessionData.pathology_orders}
                onChange={handlePathologyChange}
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default CernerEMRPage;
