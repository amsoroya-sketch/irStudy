/**
 * Permissions API Client
 * Integrates with Week 3 RBAC system
 */

import axiosInstance from '../utils/axiosInstance';

export interface UserPermissionsResponse {
  user_id: number;
  role: string;
  permissions: string[];
}

export interface PermissionCheckResponse {
  permission: string;
  has_permission: boolean;
  user_role: string;
}

/**
 * Get current user's permissions
 * Used to show/hide UI elements based on role
 */
export const getMyPermissions = async (): Promise<UserPermissionsResponse> => {
  const response = await axiosInstance.get<UserPermissionsResponse>(
    '/permissions/me'
  );
  return response.data;
};

/**
 * Check if current user has a specific permission
 * @param permission - Permission string (e.g., "mcq.create")
 */
export const checkPermission = async (
  permission: string
): Promise<PermissionCheckResponse> => {
  const response = await axiosInstance.get<PermissionCheckResponse>(
    `/permissions/check/${permission}`
  );
  return response.data;
};

/**
 * Get all available permissions in the system
 */
export const getAllPermissions = async (): Promise<string[]> => {
  const response = await axiosInstance.get<string[]>('/permissions/all');
  return response.data;
};

/**
 * Permission constants for frontend use
 * Matches backend Permission enum
 */
export const Permissions = {
  // MCQ permissions
  MCQ_VIEW: 'mcq.view',
  MCQ_CREATE: 'mcq.create',
  MCQ_UPDATE: 'mcq.update',
  MCQ_DELETE: 'mcq.delete',
  MCQ_ATTEMPT: 'mcq.attempt',

  // OSCE permissions
  OSCE_VIEW: 'osce.view',
  OSCE_CREATE: 'osce.create',
  OSCE_UPDATE: 'osce.update',
  OSCE_DELETE: 'osce.delete',
  OSCE_ATTEMPT: 'osce.attempt',

  // User management
  USER_VIEW: 'user.view',
  USER_CREATE: 'user.create',
  USER_UPDATE: 'user.update',
  USER_DELETE: 'user.delete',

  // Progress tracking
  PROGRESS_VIEW_OWN: 'progress.view.own',
  PROGRESS_VIEW_ALL: 'progress.view.all',
  PROGRESS_GRADE: 'progress.grade',

  // Study cards
  STUDYCARD_VIEW: 'studycard.view',
  STUDYCARD_CREATE: 'studycard.create',
  STUDYCARD_UPDATE: 'studycard.update',
  STUDYCARD_DELETE: 'studycard.delete',

  // Administration
  ADMIN_PANEL: 'admin.panel',
  SYSTEM_CONFIG: 'system.config',
} as const;

export type PermissionKey = keyof typeof Permissions;
export type PermissionValue = (typeof Permissions)[PermissionKey];
