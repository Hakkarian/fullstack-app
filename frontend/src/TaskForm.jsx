import React, { useState } from 'react';

const TaskForm = ({ onTaskCreated }) => {
  const [title, setTitle] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, completed: false }),
      });
      if (!response.ok) throw new Error('Failed to create task');
      setTitle('');
      onTaskCreated?.();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="task-form">
      <h2>Add New Task</h2>
      {error && <div className="error">Error: {error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          required
        />
        <button type="submit">Add Task</button>
      </form>
    </div>
  );
};

export default TaskForm;
