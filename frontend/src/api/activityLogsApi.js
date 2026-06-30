import client from './client';

const PREFIX = '/api/v1/activity-logs';

export const activityLogsApi = {
  list(params = {}) {
    return client.get(PREFIX, { params });
  },

  getMine() {
    return client.get(`${PREFIX}/me`);
  },
};

export default activityLogsApi;
