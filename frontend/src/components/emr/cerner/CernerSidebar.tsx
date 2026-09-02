/**
 * Cerner Sidebar Component
 *
 * Dark-themed PowerChart navigation sidebar.
 * Reuses Epic Sidebar logic with Cerner styling.
 */

import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
} from '@mui/material';
import {
  Description as ChartIcon,
  Assignment as OrdersIcon,
  Assessment as ResultsIcon,
} from '@mui/icons-material';

type SidebarSection = 'chart' | 'orders' | 'results';

interface CernerSidebarProps {
  activeSection: SidebarSection;
  onSectionChange: (section: SidebarSection) => void;
  open?: boolean;
}

const SIDEBAR_WIDTH = 240;

const navigationItems = [
  {
    id: 'chart' as SidebarSection,
    label: 'Chart Review',
    icon: ChartIcon,
    description: 'Patient chart and SOAP notes',
  },
  {
    id: 'orders' as SidebarSection,
    label: 'Orders',
    icon: OrdersIcon,
    description: 'Prescriptions and tests',
  },
  {
    id: 'results' as SidebarSection,
    label: 'Results',
    icon: ResultsIcon,
    description: 'Lab and imaging results',
  },
];

export const CernerSidebar: React.FC<CernerSidebarProps> = ({
  activeSection,
  onSectionChange,
  open = true,
}) => {
  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: SIDEBAR_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: SIDEBAR_WIDTH,
          boxSizing: 'border-box',
          top: '64px',
          height: 'calc(100vh - 64px)',
        },
      }}
      role="navigation"
      aria-label="PowerChart section navigation"
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="overline" color="text.secondary">
          Navigation
        </Typography>
      </Box>

      <Divider />

      <List>
        {navigationItems.map((item) => {
          const isActive = activeSection === item.id;
          const Icon = item.icon;

          return (
            <ListItem key={item.id} disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                selected={isActive}
                onClick={() => onSectionChange(item.id)}
                sx={{
                  mx: 1,
                  mb: 0.5,
                  borderRadius: 1,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
                aria-current={isActive ? 'page' : undefined}
                aria-label={`${item.label}: ${item.description}`}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'primary.contrastText' : 'primary.main',
                    minWidth: 40,
                  }}
                >
                  <Icon />
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  secondary={!isActive ? item.description : undefined}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                    variant: 'body2',
                  }}
                  secondaryTypographyProps={{
                    variant: 'caption',
                    sx: { fontSize: '0.75rem' },
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ mt: 2 }} />

      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          AMC Clinical Examination Practice
        </Typography>
      </Box>
    </Drawer>
  );
};
