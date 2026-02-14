/**
 * PermissionGuard Component
 * Conditionally renders children based on user permissions
 */

import React from 'react';
import { usePermissions } from '../hooks/usePermissions';
import { PermissionValue } from '../api/permissions';
import { Box, CircularProgress, Alert } from '@mui/material';

interface PermissionGuardProps {
  /** Single permission required */
  permission?: PermissionValue;

  /** Multiple permissions (ANY of these) */
  anyOf?: PermissionValue[];

  /** Multiple permissions (ALL of these) */
  allOf?: PermissionValue[];

  /** Fallback component when permission denied */
  fallback?: React.ReactNode;

  /** Show loading spinner while checking */
  showLoading?: boolean;

  /** Children to render if permission granted */
  children: React.ReactNode;
}

/**
 * PermissionGuard - Conditionally render based on RBAC permissions
 *
 * @example
 * // Single permission
 * <PermissionGuard permission={Permissions.MCQ_CREATE}>
 *   <Button>Create MCQ</Button>
 * </PermissionGuard>
 *
 * @example
 * // Any of multiple permissions
 * <PermissionGuard anyOf={[Permissions.MCQ_VIEW, Permissions.OSCE_VIEW]}>
 *   <ContentBrowser />
 * </PermissionGuard>
 *
 * @example
 * // All of multiple permissions
 * <PermissionGuard allOf={[Permissions.MCQ_UPDATE, Permissions.MCQ_DELETE]}>
 *   <AdvancedEditor />
 * </PermissionGuard>
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  anyOf,
  allOf,
  fallback = null,
  showLoading = true,
  children,
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isLoading } =
    usePermissions();

  // Show loading spinner while checking permissions
  if (isLoading && showLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={2}>
        <CircularProgress size={20} />
      </Box>
    );
  }

  // Check single permission
  if (permission) {
    if (!hasPermission(permission)) {
      return <>{fallback}</>;
    }
  }

  // Check ANY of multiple permissions
  if (anyOf && anyOf.length > 0) {
    if (!hasAnyPermission(...anyOf)) {
      return <>{fallback}</>;
    }
  }

  // Check ALL of multiple permissions
  if (allOf && allOf.length > 0) {
    if (!hasAllPermissions(...allOf)) {
      return <>{fallback}</>;
    }
  }

  // Permission granted - render children
  return <>{children}</>;
};

/**
 * PermissionAlert Component
 * Shows a permission denied alert message
 */
export const PermissionDeniedAlert: React.FC<{
  message?: string;
}> = ({ message = 'You do not have permission to access this feature.' }) => {
  return (
    <Box p={2}>
      <Alert severity="warning">{message}</Alert>
    </Box>
  );
};
