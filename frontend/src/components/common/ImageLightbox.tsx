/**
 * Image Lightbox Component
 * Display medical images with thumbnail grid and full-size preview
 *
 * ACCESSIBILITY:
 * - Alt text for all images
 * - Keyboard navigation (Escape to close)
 * - Focus management
 * - ARIA labels for screen readers
 */

import { useState } from 'react';
import {
  Box,
  Dialog,
  DialogContent,
  IconButton,
  ImageList,
  ImageListItem,
} from '@mui/material';
import { Close as CloseIcon, ZoomIn as ZoomInIcon } from '@mui/icons-material';

export interface ImageLightboxProps {
  /** Array of image URLs */
  images: string[];
  /** Alt text prefix (e.g., "Medical image") */
  altPrefix?: string;
}

/**
 * Image Lightbox Component
 *
 * Features:
 * - Thumbnail grid display
 * - Click to open full-size dialog
 * - Zoom icon on hover
 * - Keyboard accessible
 */
export const ImageLightbox: React.FC<ImageLightboxProps> = ({
  images,
  altPrefix = 'Medical image',
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const handleOpen = (imageUrl: string) => {
    setSelectedImage(imageUrl);
  };

  const handleClose = () => {
    setSelectedImage(null);
  };

  // If no images, return null
  if (!images || images.length === 0) {
    return null;
  }

  // Determine grid columns based on number of images
  const cols = images.length === 1 ? 1 : images.length === 2 ? 2 : 3;

  return (
    <>
      {/* Thumbnail Grid */}
      <ImageList
        cols={cols}
        gap={8}
        sx={{ width: '100%', maxHeight: 300, mb: 0 }}
        aria-label="Medical images thumbnail gallery"
      >
        {images.map((imageUrl, index) => (
          <ImageListItem
            key={imageUrl}
            sx={{
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden',
              borderRadius: 1,
              border: 1,
              borderColor: 'divider',
              '&:hover': {
                opacity: 0.8,
                '& .zoom-icon': {
                  opacity: 1,
                },
              },
            }}
            onClick={() => handleOpen(imageUrl)}
          >
            <img
              src={imageUrl}
              alt={`${altPrefix} ${index + 1}`}
              loading="lazy"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
            {/* Zoom icon overlay */}
            <Box
              className="zoom-icon"
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                opacity: 0,
                transition: 'opacity 0.2s',
                backgroundColor: 'rgba(0, 0, 0, 0.6)',
                borderRadius: '50%',
                padding: 1,
                display: 'flex',
                alignItems: 'centre',
                justifyContent: 'centre',
              }}
              aria-hidden="true"
            >
              <ZoomInIcon sx={{ color: 'white', fontSize: 32 }} />
            </Box>
          </ImageListItem>
        ))}
      </ImageList>

      {/* Full-size Dialog */}
      <Dialog
        open={selectedImage !== null}
        onClose={handleClose}
        maxWidth="lg"
        fullWidth
        aria-labelledby="image-dialog-title"
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(0, 0, 0, 0.95)',
            boxShadow: 'none',
          },
        }}
      >
        <DialogContent
          sx={{
            position: 'relative',
            padding: 2,
            display: 'flex',
            alignItems: 'centre',
            justifyContent: 'centre',
            minHeight: 400,
          }}
        >
          {/* Close button */}
          <IconButton
            onClick={handleClose}
            aria-label="Close image"
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              color: 'white',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
              },
            }}
          >
            <CloseIcon />
          </IconButton>

          {/* Full-size image */}
          {selectedImage && (
            <img
              src={selectedImage}
              alt="Full size medical image"
              style={{
                maxWidth: '100%',
                maxHeight: '80vh',
                objectFit: 'contain',
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ImageLightbox;
