import client from './client';

export const studentNotesApi = {
  list(studentId) {
    return client.get(`/api/v1/students/${studentId}/notes`);
  },

  create(studentId, content) {
    return client.post(`/api/v1/students/${studentId}/notes`, { content });
  },

  delete(studentId, noteId) {
    return client.delete(`/api/v1/students/${studentId}/notes/${noteId}`);
  },
};

export default studentNotesApi;
