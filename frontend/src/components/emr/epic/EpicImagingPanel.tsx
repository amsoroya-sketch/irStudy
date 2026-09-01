/**
 * Epic Imaging Panel Component
 *
 * Australian MBS diagnostic imaging ordering interface.
 *
 * Features:
 * - MBS imaging study selection (X-ray, CT, MRI, US, etc.)
 * - Study indication and urgency
 * - Study list with edit/delete
 * - Australian MBS item codes
 * - WCAG 2.2 AA accessible
 *
 * Mirrors EpicPathologyPanel (same add/remove/edit-rows UX) for the
 * `imaging_orders` slice of the SOAP note draft.
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
import { ImagingOrderDraft } from '../../../types/emr';

interface EpicImagingPanelProps {
  imagingOrders: ImagingOrderDraft[];
  onChange: (orders: ImagingOrderDraft[]) => void;
  readonly?: boolean;
}

// Common Australian MBS diagnostic imaging studies
const COMMON_IMAGING_STUDIES = [
  'Chest X-ray',
  'Abdominal X-ray',
  'X-ray (Limb/Extremity)',
  'CT Brain (non-contrast)',
  'CT Chest',
  'CT Abdomen/Pelvis',
  'CT Pulmonary Angiogram (CTPA)',
  'MRI Brain',
  'MRI Spine',
  'Ultrasound Abdomen',
  'Ultrasound Pelvis',
  'Ultrasound Doppler (Lower Limb)',
  'Echocardiogram',
  'Mammogram',
  'DEXA (Bone Densitometry)',
  'Nuclear Medicine (V/Q Scan)',
];

export const EpicImagingPanel: React.FC<EpicImagingPanelProps> = ({
  imagingOrders,
  onChange,
  readonly = false,
}) => {
  const [isAdding, setIsAdding] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [formData, setFormData] = useState<ImagingOrderDraft>({
    imaging_type: '',
    indication: '',
    urgency: 'routine',
  });

  const handleAddNew = () => {
    setIsAdding(true);
    setEditIndex(null);
    setFormData({
      imaging_type: '',
      indication: '',
      urgency: 'routine',
    });
  };

  const handleEdit = (index: number) => {
    setIsAdding(true);
    setEditIndex(index);
    setFormData(imagingOrders[index]);
  };

  const handleSave = () => {
    if (!formData.imaging_type || !formData.indication) {
      return; // Validation: required fields
    }

    const updatedOrders = [...imagingOrders];
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
    const updatedOrders = imagingOrders.filter((_, i) => i !== index);
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
          Imaging Orders
        </Typography>
        {!readonly && !isAdding && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddNew}
            aria-label="Add new imaging order"
          >
            Add Imaging Study
          </Button>
        )}
      </Box>

      {/* Australian MBS Note */}
      <Alert severity="info" sx={{ mb: 2 }}>
        <Typography variant="body2">
          Australian MBS diagnostic imaging. Indicate clinical justification for study ordering.
        </Typography>
      </Alert>

      {/* Imaging Order Form */}
      {isAdding && (
        <Paper variant="outlined" sx={{ p: 2, mb: 2, backgroundColor: 'background.default' }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            {editIndex !== null ? 'Edit Imaging Order' : 'New Imaging Order'}
          </Typography>

          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              fullWidth
              select
              label="Imaging Study"
              value={formData.imaging_type}
              onChange={(e) => setFormData({ ...formData, imaging_type: e.target.value })}
              required
              helperText="Select from common MBS imaging studies"
            >
              {COMMON_IMAGING_STUDIES.map((study) => (
                <MenuItem key={study} value={study}>
                  {study}
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
              placeholder="e.g., Suspected pneumonia, exclude fracture"
              helperText="Justify why this study is clinically indicated"
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
                disabled={!formData.imaging_type || !formData.indication}
              >
                {editIndex !== null ? 'Update' : 'Add'}
              </Button>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Imaging Orders List */}
      {imagingOrders.length > 0 ? (
        <TableContainer>
          <Table size="small" aria-label="Imaging orders list">
            <TableHead>
              <TableRow>
                <TableCell>Imaging Study</TableCell>
                <TableCell>Clinical Indication</TableCell>
                <TableCell>Urgency</TableCell>
                {!readonly && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {imagingOrders.map((order, index) => (
                <TableRow key={index}>
                  <TableCell>{order.imaging_type}</TableCell>
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
                        aria-label={`Edit imaging order ${index + 1}`}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(index)}
                        aria-label={`Delete imaging order ${index + 1}`}
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
        <Alert severity="info">No imaging orders added yet</Alert>
      )}
    </Paper>
  );
};
