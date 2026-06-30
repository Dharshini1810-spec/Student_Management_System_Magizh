import client from './client';

const USERS_PREFIX = '/api/v1/users';

export const usersApi = {
  /** List users with optional search and filter parameters. */
  listUsers(params = {}) {
    return client.get(USERS_PREFIX, { params });
  },

  /** Get a specific user by ID. */
  getUser(userId) {
    return client.get(`${USERS_PREFIX}/${userId}`);
  },

  /** Create a new user (Super Admin only). */
  createUser(data) {
    return client.post(USERS_PREFIX, data);
  },

  /** Update user fields (e.g. is_active). */
  updateUser(userId, data) {
    return client.patch(`${USERS_PREFIX}/${userId}`, data);
  },

  /** Soft-delete / deactivate a user. */
  deactivateUser(userId) {
    return client.delete(`${USERS_PREFIX}/${userId}`);
  },

  /** Get a user's full permissions profile. */
  getUserPermissions(userId) {
    return client.get(`${USERS_PREFIX}/${userId}/permissions`);
  },

  /** Assign a direct permission to a user. */
  assignPermission(userId, permission) {
    return client.post(`${USERS_PREFIX}/${userId}/permissions`, { permission });
  },

  /** Revoke a direct permission from a user. */
  revokePermission(userId, permission) {
    return client.delete(`${USERS_PREFIX}/${userId}/permissions`, {
      data: { permission },
    });
  },

};

export default usersApi;
