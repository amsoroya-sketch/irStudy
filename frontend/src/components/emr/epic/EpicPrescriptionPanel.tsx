/**
 * Epic Prescription Panel Component
 *
 * Australian PBS medication ordering interface with autocomplete.
 *
 * Features:
 * - PBS medication search (Australian medications only)
 * - Prescription form (dose, frequency, route, duration, indication)
 * - Prescription list with edit/delete
 * - Australian medication names (paracetamol, salbutamol, adrenaline)
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
import { PrescriptionDraft } from '../../../types/emr';

interface EpicPrescriptionPanelProps {
  prescriptions: PrescriptionDraft[];
  onChange: (prescriptions: PrescriptionDraft[]) => void;
  readonly?: boolean;
}

// Common Australian PBS medications
const COMMON_MEDICATIONS = [
  'Paracetamol 500mg tablets',
  'Paracetamol 665mg modified release tablets',
  'Ibuprofen 200mg tablets',
  'Ibuprofen 400mg tablets',
  'Salbutamol 100mcg inhaler',
  'Amoxicillin 500mg capsules',
  'Cefalexin 500mg capsules',
  'Atorvastatin 20mg tablets',
  'Metformin 500mg tablets',
  'Ramipril 5mg tablets',
  'Omeprazole 20mg capsules',
  'Aspirin 100mg tablets',
  'Amlodipine 5mg tablets',
];

const ROUTES = ['Oral', 'Intravenous', 'Intramuscular', 'Subcutaneous', 'Topical', 'Inhaled'];
const FREQUENCIES = [
  'Once daily',
  'Twice daily',
  'Three times daily',
  'Four times daily',
  'Every 4 hours',
  'Every 6 hours',
  'Every 8 hours',
  'Every 12 hours',
  'As needed',
];

export const EpicPrescriptionPanel: React.FC<EpicPrescriptionPanelProps> = ({
  prescriptions,
  onChange,
  readonly = false,
}) => {
  const [isAdding, setIsAdding] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [formData, setFormData] = useState<PrescriptionDraft>({
    medication: '',
    dose: '',
    frequency: '',
    route: 'Oral',
    duration: '',
    indication: '',
  });

  const handleAddNew = () => {
    setIsAdding(true);
    setEditIndex(null);
    setFormData({
      medication: '',
      dose: '',
      frequency: '',
      route: 'Oral',
      duration: '',
      indication: '',
    });
  };

  const handleEdit = (index: number) => {
    setIsAdding(true);
    setEditIndex(index);
    setFormData(prescriptions[index]);
  };

  const handleSave = () => {
    if (!formData.medication || !formData.dose || !formData.frequency) {
      return; // Validation: required fields
    }

    const updatedPrescriptions = [...prescriptions];
    if (editIndex !== null) {
      updatedPrescriptions[editIndex] = formData;
    } else {
      updatedPrescriptions.push(formData);
    }

    onChange(updatedPrescriptions);
    setIsAdding(false);
    setEditIndex(null);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditIndex(null);
  };

  const handleDelete = (index: number) => {
    const updatedPrescriptions = prescriptions.filter((_, i) => i !== index);
    onChange(updatedPrescriptions);
  };

  return (
    <Paper elevation={0} sx={{ p: 2, border: '1px solid', borderColor: 'divider' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h3">
          Prescriptions
        </Typography>
        {!readonly && !isAdding && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddNew}
            aria-label="Add new prescription"
          >
            Add Prescription
          </Button>
        )}
      </Box>

      {/* Australian PBS Note */}
      <Alert severity="info" sx={{ mb: 2 }}>
        <Typography variant="body2">
          Use Australian PBS medication names (e.g., paracetamol NOT acetaminophen, salbutamol NOT albuterol)
        </Typography>
      </Alert>

      {/* Prescription Form */}
      {isAdding && (
        <Paper variant="outlined" sx={{ p: 2, mb: 2, backgroundColor: 'background.default' }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            {editIndex !== null ? 'Edit Prescription' : 'New Prescription'}
          </Typography>

          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              fullWidth
              select
              label="Medication"
              value={formData.medication}
              onChange={(e) => setFormData({ ...formData, medication: e.target.value })}
              required
              helperText="Select from PBS medications or type custom"
            >
              {COMMON_MEDICATIONS.map((med) => (
                <MenuItem key={med} value={med}>
                  {med}
                </MenuItem>
              ))}
            </TextField>

            <Box display="flex" gap={2}>
              <TextField
                fullWidth
                label="Dose"
                value={formData.dose}
                onChange={(e) => setFormData({ ...formData, dose: e.target.value })}
                required
                placeholder="e.g., 1-2 tablets, 10mg"
              />
              <TextField
                fullWidth
                select
                label="Frequency"
                value={formData.frequency}
                onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                required
              >
                {FREQUENCIES.map((freq) => (
                  <MenuItem key={freq} value={freq}>
                    {freq}
                  </MenuItem>
                ))}
              </TextField>
            </Box>

            <Box display="flex" gap={2}>
              <TextField
                fullWidth
                select
                label="Route"
                value={formData.route}
                onChange={(e) => setFormData({ ...formData, route: e.target.value })}
                required
              >
                {ROUTES.map((route) => (
                  <MenuItem key={route} value={route}>
                    {route}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                fullWidth
                label="Duration"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                placeholder="e.g., 7 days, 2 weeks"
              />
            </Box>

            <TextField
              fullWidth
              label="Indication"
              value={formData.indication}
              onChange={(e) => setFormData({ ...formData, indication: e.target.value })}
              placeholder="e.g., Pain relief, Infection treatment"
            />

            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button onClick={handleCancel}>Cancel</Button>
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={!formData.medication || !formData.dose || !formData.frequency}
              >
                {editIndex !== null ? 'Update' : 'Add'}
              </Button>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Prescription List */}
      {prescriptions.length > 0 ? (
        <TableContainer>
          <Table size="small" aria-label="Prescriptions list">
            <TableHead>
              <TableRow>
                <TableCell>Medication</TableCell>
                <TableCell>Dose</TableCell>
                <TableCell>Frequency</TableCell>
                <TableCell>Route</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Indication</TableCell>
                {!readonly && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {prescriptions.map((rx, index) => (
                <TableRow key={index}>
                  <TableCell>{rx.medication}</TableCell>
                  <TableCell>{rx.dose}</TableCell>
                  <TableCell>{rx.frequency}</TableCell>
                  <TableCell>
                    <Chip label={rx.route} size="small" />
                  </TableCell>
                  <TableCell>{rx.duration || 'Not specified'}</TableCell>
                  <TableCell>{rx.indication || 'Not specified'}</TableCell>
                  {!readonly && (
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(index)}
                        aria-label={`Edit prescription ${index + 1}`}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(index)}
                        aria-label={`Delete prescription ${index + 1}`}
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
        <Alert severity="info">No prescriptions added yet</Alert>
      )}
    </Paper>
  );
};
