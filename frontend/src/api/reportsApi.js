import client from './client';

const PREFIX = '/api/v1/reports';

export const reportsApi = {
  attendance(params = {}) {
    return client.get(`${PREFIX}/attendance`, { params });
  },

  students() {
    return client.get(`${PREFIX}/students`);
  },

  projects() {
    return client.get(`${PREFIX}/projects`);
  },

  todos() {
    return client.get(`${PREFIX}/todos`);
  },

  activity(params = {}) {
    return client.get(`${PREFIX}/activity`, { params });
  },

  summary() {
    return client.get(`${PREFIX}/summary`);
  },
};

export default reportsApi;
