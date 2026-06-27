import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import studentNotesApi from '../api/studentNotesApi';
import usersApi from '../api/usersApi';

export default function StudentNotesPage() {
  const { studentId } = useParams();
  const { user } = useAuth();
  const toast = useToast();

  const [notes, setNotes] = useState([]);
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [newNote, setNewNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchNotes = useCallback(async () => {
    if (!studentId) return;
    setLoading(true);
    try {
      const [notesRes, studentRes] = await Promise.all([
        studentNotesApi.list(studentId),
        usersApi.getUser(studentId).catch(() => null),
      ]);
      setNotes(notesRes.data.notes || []);
      if (studentRes?.data) setStudent(studentRes.data);
    } catch (err) {
      toast.error(err.message || 'Failed to load notes');
    } finally {
      setLoading(false);
    }
  }, [studentId, toast]);

  useEffect(() => { fetchNotes(); }, [fetchNotes]);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) { toast.warning('Please enter note content'); return; }
    setSubmitting(true);
    try {
      await studentNotesApi.create(studentId, newNote.trim());
      toast.success('Note added');
      setNewNote('');
      await fetchNotes();
    } catch (err) {
      toast.error(err.message || 'Failed to add note');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (noteId) => {
    if (!window.confirm('Delete this note?')) return;
    setActionLoading(`del-${noteId}`);
    try {
      await studentNotesApi.delete(studentId, noteId);
      toast.success('Note deleted');
      await fetchNotes();
    } catch (err) {
      toast.error(err.message || 'Failed to delete note');
    } finally {
      setActionLoading(null);
    }
  };

  const canDelete = (note) => {
    if (user?.role === 'SUPER_ADMIN') return true;
    return note.written_by === user?.id;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
          <p className="text-sm text-white/50">Loading notes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Student Notes</h1>
        {student && (
          <p className="text-sm text-white/50 mt-1">
            Notes for {student.email} · {notes.length} note{notes.length !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      <form onSubmit={handleAddNote} className="card">
        <label className="block text-sm font-medium text-white/80 mb-2">Add a Note</label>
        <textarea
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          className="input-field mb-3"
          rows={3}
          placeholder="Write your note here..."
        />
        <button type="submit" disabled={submitting || !newNote.trim()} className="btn-primary text-sm">
          {submitting ? 'Adding...' : 'Add Note'}
        </button>
      </form>

      {notes.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-white/50 text-sm">No notes yet for this student</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notes.map((note, i) => (
            <div key={note.id} className="card animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white/90 whitespace-pre-wrap">{note.content}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-white/40">
                    <span>By {note.author_name || 'Unknown'}</span>
                    <span>{new Date(note.created_at).toLocaleString()}</span>
                  </div>
                </div>
                {canDelete(note) && (
                  <button
                    onClick={() => handleDelete(note.id)}
                    disabled={actionLoading === `del-${note.id}`}
                    className="text-xs px-2 py-1 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors flex-shrink-0"
                  >
                    {actionLoading === `del-${note.id}` ? '...' : 'Delete'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
