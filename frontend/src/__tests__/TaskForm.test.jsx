import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskForm from '../TaskForm';

// Mock fetch API
global.fetch = jest.fn();

describe('TaskForm', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders form with input and button', () => {
    render(<TaskForm />);
    expect(screen.getByPlaceholderText('Enter task title')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add Task' })).toBeInTheDocument();
  });

  it('updates input value on change', async () => {
    render(<TaskForm />);
    const input = screen.getByPlaceholderText('Enter task title');

    await userEvent.type(input, 'New Task');

    expect(input).toHaveValue('New Task');
  });

  it('calls fetch on form submission', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      })
    );

    const onTaskCreated = jest.fn();
    render(<TaskForm onTaskCreated={onTaskCreated} />);

    const input = screen.getByPlaceholderText('Enter task title');
    const button = screen.getByRole('button', { name: 'Add Task' });

    await userEvent.type(input, 'New Task');
    await act(async () => {
      await userEvent.click(button);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Task', completed: false })
      });
    });
  });

  it('calls onTaskCreated callback after successful submission', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      })
    );

    const onTaskCreated = jest.fn();
    render(<TaskForm onTaskCreated={onTaskCreated} />);

    const input = screen.getByPlaceholderText('Enter task title');
    const button = screen.getByRole('button', { name: 'Add Task' });

    await userEvent.type(input, 'New Task');
    await act(async () => {
      await userEvent.click(button);
    });

    await waitFor(() => {
      expect(onTaskCreated).toHaveBeenCalled();
    });
  });

  it('displays error message on fetch failure', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Failed to create task'))
    );

    render(<TaskForm />);
    const input = screen.getByPlaceholderText('Enter task title');
    const button = screen.getByRole('button', { name: 'Add Task' });

    await userEvent.type(input, 'New Task');
    await act(async () => {
      await userEvent.click(button);
    });

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });

  it('does not submit when title is empty', async () => {
    render(<TaskForm />);
    const button = screen.getByRole('button', { name: 'Add Task' });

    await userEvent.click(button);

    expect(fetch).not.toHaveBeenCalled();
  });
});
