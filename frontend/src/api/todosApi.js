import client from './client';

const PREFIX = '/api/v1/todos';

export const todosApi = {
  list(params = {}) {
    return client.get(PREFIX, { params });
  },

  get(id) {
    return client.get(`${PREFIX}/${id}`);
  },

  create(data) {
    return client.post(PREFIX, data);
  },

  update(id, data) {
    return client.put(`${PREFIX}/${id}`, data);
  },

  updateStatus(id, status) {
    return client.patch(`${PREFIX}/${id}/status`, { status });
  },

  listPendingApproval() {
    return client.get(`${PREFIX}/pending-approval`);
  },

  approve(id) {
    return client.patch(`${PREFIX}/${id}/approve`);
  },

  reject(id) {
    return client.patch(`${PREFIX}/${id}/reject`, { approval_status: 'rejected' });
  },

  delete(id) {
    return client.delete(`${PREFIX}/${id}`);
  },
};

export default todosApi;
