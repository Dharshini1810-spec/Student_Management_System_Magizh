import client from './client';

const PREFIX = '/api/v1/attendance';

export const attendanceApi = {
  checkIn(reason) {
    return client.post(`${PREFIX}/check-in`, { reason });
  },

  checkOut(reason) {
    return client.post(`${PREFIX}/check-out`, { reason });
  },

  list(params = {}) {
    return client.get(PREFIX, { params });
  },

  listRequests() {
    return client.get(`${PREFIX}/requests`);
  },

  approveRequest(id) {
    return client.post(`${PREFIX}/requests/${id}/approve`);
  },

  rejectRequest(id) {
    return client.post(`${PREFIX}/requests/${id}/reject`);
  },

  getSettings() {
    return client.get(`${PREFIX}/settings`);
  },

  getStudentHistory(studentId) {
    return client.get(`${PREFIX}/${studentId}`);
  },
};

export default attendanceApi;
