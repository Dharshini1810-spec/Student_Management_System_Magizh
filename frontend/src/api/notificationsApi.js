import client from './client';

const PREFIX = '/api/v1/notifications';

export const notificationsApi = {
  list(params = {}) {
    return client.get(PREFIX, { params });
  },

  getUnreadCount() {
    return client.get(`${PREFIX}/unread-count`);
  },

  markRead(id) {
    return client.patch(`${PREFIX}/${id}/read`);
  },

  markAllRead() {
    return client.patch(`${PREFIX}/read-all`);
  },
};

export default notificationsApi;
