import client from './client';

export const rolesApi = {
  /** List all system roles with their permissions. */
  listRoles() {
    return client.get('/api/v1/roles');
  },

  /** List all system permissions. */
  listPermissions() {
    return client.get('/api/v1/permissions');
  },
};

export default rolesApi;
