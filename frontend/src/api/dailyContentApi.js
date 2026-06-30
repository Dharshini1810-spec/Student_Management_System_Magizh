import client from './client';

const PREFIX = '/api/v1/daily-content';

export const dailyContentApi = {
  list(params = {}) {
    return client.get(PREFIX, { params });
  },

  getToday() {
    return client.get(`${PREFIX}/today`);
  },

  get(id) {
    return client.get(`${PREFIX}/${id}`);
  },

  create(data) {
    return client.post(PREFIX, data);
  },

  update(id, data) {
    return client.patch(`${PREFIX}/${id}`, data);
  },

  delete(id) {
    return client.delete(`${PREFIX}/${id}`);
  },
};

export default dailyContentApi;
