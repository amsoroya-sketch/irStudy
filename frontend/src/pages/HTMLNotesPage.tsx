/**
 * HTML OSCE Notes Page
 * Browse, filter, and view pre-generated HTML OSCE notes
 *
 * Features:
 * - Search by title/topics
 * - Filter by specialty and category
 * - Responsive grid of note cards
 * - Full-screen dialog with iframe viewer
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Tooltip,
  InputAdornment,
  useTheme,
} from '@mui/material';
import {
  Close as CloseIcon,
  Search as SearchIcon,
  LocalHospital as HospitalIcon,
  MenuBook as MenuBookIcon,
  AccessTime as TimeIcon,
  Storage as StorageIcon,
} from '@mui/icons-material';
import { useResponsive } from '../hooks/useResponsive';
import {
  useHTMLNotes,
  useHTMLNote,
  useHTMLNoteSpecialties,
  useHTMLNoteContent,
} from '../hooks/useHTMLNotes';
import type { HTMLNote } from '../types/api';

/**
 * Get unique categories from notes
 */
const getCategories = (notes: HTMLNote[]): string[] => {
  const set = new Set<string>();
  notes.forEach((note) => {
    if (note.category) set.add(note.category);
  });
  return Array.from(set).sort();
};

/**
 * HTML Note Viewer Dialog
 */
interface NoteViewerDialogProps {
  open: boolean;
  noteId: string | null;
  onClose: () => void;
}

const NoteViewerDialog: React.FC<NoteViewerDialogProps> = ({ open, noteId, onClose }) => {
  const { isMobile } = useResponsive();
  const { data: note } = useHTMLNote(noteId || '');
  const { data: htmlContent, isLoading: contentLoading } = useHTMLNoteContent(noteId || '');

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullScreen={isMobile}
      maxWidth="xl"
      fullWidth
      aria-labelledby="html-note-viewer-title"
    >
      <DialogTitle
        id="html-note-viewer-title"
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          pr: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, overflow: 'hidden' }}>
          <MenuBookIcon color="primary" />
          <Typography
            variant="h6"
            component="span"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={note?.title}
          >
            {note?.title || 'Loading...'}
          </Typography>
        </Box>
        <Tooltip title="Close">
          <IconButton onClick={onClose} edge="end" aria-label="Close viewer">
            <CloseIcon />
          </IconButton>
        </Tooltip>
      </DialogTitle>
      <DialogContent dividers sx={{ p: 0, bgcolor: '#f5f5f5' }}>
        {contentLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
            <CircularProgress />
          </Box>
        )}
        {htmlContent && (
          <iframe
            srcDoc={htmlContent}
            title={note?.title || 'HTML Note'}
            style={{
              width: '100%',
              height: isMobile ? 'calc(100vh - 120px)' : '70vh',
              border: 'none',
              backgroundColor: 'white',
            }}
            sandbox="allow-same-origin"
          />
        )}
      </DialogContent>
    </Dialog>
  );
};

/**
 * Note Card Component
 */
interface NoteCardProps {
  note: HTMLNote;
  onClick: () => void;
}

const NoteCard: React.FC<NoteCardProps> = ({ note, onClick }) => {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardActionArea onClick={onClick} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
        <CardContent sx={{ flexGrow: 1 }}>
          {/* Badges */}
          <Box sx={{ mb: 1.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            <Chip
              label={note.specialty}
              color="primary"
              size="small"
              variant="outlined"
            />
            <Chip
              label={note.category}
              color="secondary"
              size="small"
              variant="outlined"
            />
          </Box>

          {/* Title */}
          <Typography variant="h6" component="h3" gutterBottom>
            {note.title}
          </Typography>

          {/* Preview */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              mb: 2,
            }}
          >
            {note.preview_text || 'No preview available'}
          </Typography>

          {/* Topics */}
          {note.topics && note.topics.length > 0 && (
            <Box sx={{ mb: 1.5 }}>
              {note.topics.slice(0, 3).map((topic, idx) => (
                <Chip
                  key={idx}
                  label={topic}
                  size="small"
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              ))}
              {note.topics.length > 3 && (
                <Chip
                  label={`+${note.topics.length - 3}`}
                  size="small"
                  variant="outlined"
                  sx={{ mb: 0.5 }}
                />
              )}
            </Box>
          )}

          {/* Meta info */}
          <Box sx={{ display: 'flex', gap: 2, mt: 'auto' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <TimeIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                {note.estimated_reading_minutes} min
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <StorageIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                {note.file_size_kb} KB
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

/**
 * HTML Notes Page Component
 */
const HTMLNotesPage: React.FC = () => {
  const theme = useTheme();
  const { isMobile } = useResponsive();

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  // Viewer state
  const [viewerNoteId, setViewerNoteId] = useState<string | null>(null);
  const [viewerOpen, setViewerOpen] = useState(false);

  // Data fetching
  const {
    data: notes,
    isLoading: notesLoading,
    error: notesError,
  } = useHTMLNotes({
    specialty: selectedSpecialty || undefined,
    category: selectedCategory || undefined,
    limit: 100,
  });

  const { data: specialtiesData } = useHTMLNoteSpecialties();

  useEffect(() => {
    document.title = 'HTML OSCE Notes - AMC Clinical Exam';
  }, []);

  // Derive categories from loaded notes
  const categories = useMemo(() => getCategories(notes || []), [notes]);

  // Filter notes by search query (client-side)
  const filteredNotes = useMemo(() => {
    if (!notes) return [];
    if (!searchQuery.trim()) return notes;

    const q = searchQuery.toLowerCase();
    return notes.filter(
      (note) =>
        note.title.toLowerCase().includes(q) ||
        note.topics?.some((t) => t.toLowerCase().includes(q)) ||
        note.category?.toLowerCase().includes(q) ||
        note.specialty?.toLowerCase().includes(q)
    );
  }, [notes, searchQuery]);

  const handleOpenViewer = (noteId: string) => {
    setViewerNoteId(noteId);
    setViewerOpen(true);
  };

  const handleCloseViewer = () => {
    setViewerOpen(false);
    setTimeout(() => setViewerNoteId(null), 300);
  };

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header */}
      <Box
        sx={{
          mb: 4,
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          justifyContent: 'space-between',
          alignItems: { xs: 'flex-start', sm: 'center' },
          gap: { xs: 2, sm: 0 },
        }}
      >
        <Box>
          <Typography variant="h4" component="h1">
            HTML OSCE Notes
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Dr. Amir&apos;s method — pre-generated notes for offline study
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <HospitalIcon color="primary" />
          <Typography variant="body2" color="text.secondary">
            {notes?.length || 0} notes available
          </Typography>
        </Box>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 5 }}>
            <TextField
              fullWidth
              label="Search"
              placeholder="Search by title, topic, or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 3.5 }}>
            <FormControl fullWidth>
              <InputLabel>Specialty</InputLabel>
              <Select
                value={selectedSpecialty}
                onChange={(e) => setSelectedSpecialty(e.target.value)}
                label="Specialty"
              >
                <MenuItem value="">All Specialties</MenuItem>
                {specialtiesData?.map((s) => (
                  <MenuItem key={s.specialty} value={s.specialty}>
                    {s.specialty} ({s.count})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 3.5 }}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat} value={cat}>
                    {cat}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Loading */}
      {notesLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error */}
      {notesError && (
        <Alert severity="error" sx={{ mb: 4 }}>
          Failed to load HTML notes. Please try again later.
        </Alert>
      )}

      {/* Notes Grid */}
      {!notesLoading && !notesError && (
        <>
          <Grid container spacing={3}>
            {filteredNotes.map((note) => (
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={note.note_id}>
                <NoteCard note={note} onClick={() => handleOpenViewer(note.note_id)} />
              </Grid>
            ))}
          </Grid>

          {/* Empty state */}
          {filteredNotes.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <MenuBookIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No notes found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your filters or search query
              </Typography>
            </Box>
          )}
        </>
      )}

      {/* Viewer Dialog */}
      <NoteViewerDialog
        open={viewerOpen}
        noteId={viewerNoteId}
        onClose={handleCloseViewer}
      />
    </Container>
  );
};

export default HTMLNotesPage;
