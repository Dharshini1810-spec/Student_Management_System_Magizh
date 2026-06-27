import client from './client';

const PREFIX = '/api/v1/referral-links';

export const referralLinksApi = {
  list(params = {}) {
    return client.get(PREFIX, { params });
  },

  get(id) {
    return client.get(`${PREFIX}/${id}`);
  },

  create(data) {
    return client.post(PREFIX, data);
  },

  deactivate(id) {
    return client.delete(`${PREFIX}/${id}`);
  },
};

export default referralLinksApi;
