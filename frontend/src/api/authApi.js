import client from './client';

const AUTH_PREFIX = '/api/v1/auth';

export const authApi = {
  /**
   * Authenticate user and receive JWT token.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{access_token, token_type, user, must_change_password}>}
   */
  login(email, password) {
    return client.post(`${AUTH_PREFIX}/login`, { email, password });
  },

  /**
   * Get the currently authenticated user's profile.
   */
  getMe() {
    return client.get(`${AUTH_PREFIX}/me`);
  },

  /**
   * Change password (first-login forced or voluntary).
   * @param {string} currentPassword
   * @param {string} newPassword
   */
  changePassword(currentPassword, newPassword) {
    return client.post(`${AUTH_PREFIX}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },


};

export default authApi;
