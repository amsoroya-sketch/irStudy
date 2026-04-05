/**
 * Epic Pathology Panel Component
 *
 * Australian MBS pathology test ordering interface.
 *
 * Features:
 * - MBS pathology test selection
 * - Test indication and urgency
 * - Test list with edit/delete
 * - Australian MBS item codes
 * - WCAG 2.2 AA accessible
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  MenuItem,
  Alert,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { PathologyOrderDraft } from '../../../types/emr';

interface EpicPathologyPanelProps {
  pathologyOrders: PathologyOrderDraft[];
  onChange: (orders: PathologyOrderDraft[]) => void;
  readonly?: boolean;
}

// Common Australian MBS pathology tests
const COMMON_PATHOLOGY_TESTS = [
  'Full Blood Count (FBC)',
  'Urea and Electrolytes (UEC)',
  'Liver Function Tests (LFTs)',
  'C-Reactive Protein (CRP)',
  'Erythrocyte Sedimentation Rate (ESR)',
  'Thyroid Function Tests (TFTs)',
  'Lipid Panel',
  'HbA1c',
  'Fasting Blood Glucose',
  'Coagulation Studies (INR, APTT)',
  'Blood Cultures',
  'Urinalysis',
  'Urine Microscopy & Culture',
  'Troponin',
  'D-Dimer',
  'Vitamin B12 & Folate',
  'Iron Studies',
];

export const EpicPathologyPanel: React.FC<EpicPathologyPanelProps> = ({
  pathologyOrders,
  onChange,
  readonly = false,
}) => {
  const [isAdding, setIsAdding] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [formData, setFormData] = useState<PathologyOrderDraft>({
    test_name: '',
    indication: '',
    urgency: 'routine',
  });

  const handleAddNew = () => {
    setIsAdding(true);
    setEditIndex(null);
    setFormData({
      test_name: '',
      indication: '',
      urgency: 'routine',
    });
  };

  const handleEdit = (index: number) => {
    setIsAdding(true);
    setEditIndex(index);
    setFormData(pathologyOrders[index]);
  };

  const handleSave = () => {
    if (!formData.test_name || !formData.indication) {
      return; // Validation: required fields
    }

    const updatedOrders = [...pathologyOrders];
    if (editIndex !== null) {
      updatedOrders[editIndex] = formData;
    } else {
      updatedOrders.push(formData);
    }

    onChange(updatedOrders);
    setIsAdding(false);
    setEditIndex(null);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditIndex(null);
  };

  const handleDelete = (index: number) => {
    const updatedOrders = pathologyOrders.filter((_, i) => i !== index);
    onChange(updatedOrders);
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'stat':
        return 'error';
      case 'urgent':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Paper elevation={0} sx={{ p: 2, border: '1px solid', borderColor: 'divider' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h3">
          Pathology Orders
        </Typography>
        {!readonly && !isAdding && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddNew}
            aria-label="Add new pathology order"
          >
            Add Pathology Test
          </Button>
        )}
      </Box>

      {/* Australian MBS Note */}
      <Alert severity="info" sx={{ mb: 2 }}>
        <Typography variant="body2">
          Australian MBS pathology tests. Indicate clinical justification for test ordering.
        </Typography>
      </Alert>

      {/* Pathology Order Form */}
      {isAdding && (
        <Paper variant="outlined" sx={{ p: 2, mb: 2, backgroundColor: 'background.default' }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            {editIndex !== null ? 'Edit Pathology Order' : 'New Pathology Order'}
          </Typography>

          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              fullWidth
              select
              label="Test Name"
              value={formData.test_name}
              onChange={(e) => setFormData({ ...formData, test_name: e.target.value })}
              required
              helperText="Select from common MBS pathology tests"
            >
              {COMMON_PATHOLOGY_TESTS.map((test) => (
                <MenuItem key={test} value={test}>
                  {test}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              fullWidth
              label="Clinical Indication"
              value={formData.indication}
              onChange={(e) => setFormData({ ...formData, indication: e.target.value })}
              required
              multiline
              rows={2}
              placeholder="e.g., Suspected anaemia, infection screening"
              helperText="Justify why this test is clinically indicated"
            />

            <TextField
              fullWidth
              select
              label="Urgency"
              value={formData.urgency}
              onChange={(e) => setFormData({ ...formData, urgency: e.target.value as typeof formData.urgency })}
              required
            >
              <MenuItem value="routine">Routine</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
              <MenuItem value="stat">STAT (Immediate)</MenuItem>
            </TextField>

            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button onClick={handleCancel}>Cancel</Button>
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={!formData.test_name || !formData.indication}
              >
                {editIndex !== null ? 'Update' : 'Add'}
              </Button>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Pathology Orders List */}
      {pathologyOrders.length > 0 ? (
        <TableContainer>
          <Table size="small" aria-label="Pathology orders list">
            <TableHead>
              <TableRow>
                <TableCell>Test Name</TableCell>
                <TableCell>Clinical Indication</TableCell>
                <TableCell>Urgency</TableCell>
                {!readonly && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {pathologyOrders.map((order, index) => (
                <TableRow key={index}>
                  <TableCell>{order.test_name}</TableCell>
                  <TableCell>{order.indication}</TableCell>
                  <TableCell>
                    <Chip
                      label={order.urgency.toUpperCase()}
                      size="small"
                      color={getUrgencyColor(order.urgency)}
                    />
                  </TableCell>
                  {!readonly && (
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(index)}
                        aria-label={`Edit pathology order ${index + 1}`}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(index)}
                        aria-label={`Delete pathology order ${index + 1}`}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Alert severity="info">No pathology orders added yet</Alert>
      )}
    </Paper>
  );
};
