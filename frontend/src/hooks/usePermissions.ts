/**
 * usePermissions Hook
 * Provides RBAC functionality to React components
 */

import { useQuery } from '@tanstack/react-query';
import { getMyPermissions, Permissions, PermissionValue } from '../api/permissions';

export const usePermissions = () => {
  const {
    data: permissionsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['permissions', 'me'],
    queryFn: getMyPermissions,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });

  /**
   * Check if user has a specific permission
   * @param permission - Permission string to check
   * @returns true if user has permission, false otherwise
   */
  const hasPermission = (permission: PermissionValue): boolean => {
    if (!permissionsData) return false;
    return permissionsData.permissions.includes(permission);
  };

  /**
   * Check if user has ANY of the specified permissions (OR logic)
   * @param permissions - Array of permissions to check
   * @returns true if user has at least one permission
   */
  const hasAnyPermission = (...permissions: PermissionValue[]): boolean => {
    if (!permissionsData) return false;
    return permissions.some((perm) =>
      permissionsData.permissions.includes(perm)
    );
  };

  /**
   * Check if user has ALL of the specified permissions (AND logic)
   * @param permissions - Array of permissions to check
   * @returns true if user has all permissions
   */
  const hasAllPermissions = (...permissions: PermissionValue[]): boolean => {
    if (!permissionsData) return false;
    return permissions.every((perm) =>
      permissionsData.permissions.includes(perm)
    );
  };

  /**
   * Check if user is a student
   */
  const isStudent = (): boolean => {
    return permissionsData?.role === 'student';
  };

  /**
   * Check if user is an educator
   */
  const isEducator = (): boolean => {
    return permissionsData?.role === 'educator';
  };

  /**
   * Check if user is an admin
   */
  const isAdmin = (): boolean => {
    return permissionsData?.role === 'admin';
  };

  /**
   * Check if user can create content (MCQs/OSCEs)
   */
  const canCreateContent = (): boolean => {
    return hasAnyPermission(Permissions.MCQ_CREATE, Permissions.OSCE_CREATE);
  };

  /**
   * Check if user can grade/review
   */
  const canGrade = (): boolean => {
    return hasPermission(Permissions.PROGRESS_GRADE);
  };

  return {
    // Data
    permissions: permissionsData?.permissions || [],
    role: permissionsData?.role,
    userId: permissionsData?.user_id,

    // Loading states
    isLoading,
    error,

    // Permission checks
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // Role checks
    isStudent,
    isEducator,
    isAdmin,

    // Convenience methods
    canCreateContent,
    canGrade,
  };
};
