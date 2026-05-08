import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import TaskList from '../TaskList';

// Mock fetch API
global.fetch = jest.fn();

describe('TaskList', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementationOnce(() => new Promise(() => {}));
    render(<TaskList />);
    expect(screen.getByText('Loading tasks...')).toBeInTheDocument();
  });

  it('renders error state on fetch failure', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Failed to fetch tasks'))
    );

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });

  it('renders tasks when fetch succeeds', async () => {
    const mockTasks = [
      { id: 1, title: 'Task 1', completed: false },
      { id: 2, title: 'Task 2', completed: true }
    ];

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockTasks)
      })
    );

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });

    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
  });

  it('renders "No tasks yet" when tasks array is empty', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      })
    );

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('No tasks yet.')).toBeInTheDocument();
    });
  });

  it('displays task status correctly', async () => {
    const mockTasks = [
      { id: 1, title: 'Task 1', completed: false },
      { id: 2, title: 'Task 2', completed: true }
    ];

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockTasks)
      })
    );

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText(/Status: Pending/)).toBeInTheDocument();
      expect(screen.getByText(/Status: Done/)).toBeInTheDocument();
    });
  });
});
