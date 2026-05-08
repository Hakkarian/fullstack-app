import React from 'react';
import { shallow, mount } from 'enzyme';
import TaskList from '../TaskList';

// Mock fetch API
global.fetch = jest.fn();

describe('TaskList', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementationOnce(() => new Promise(() => {}));
    const wrapper = shallow(<TaskList />);
    expect(wrapper.find('div').first().text()).toBe('Loading tasks...');
  });

  it('renders error state on fetch failure', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Failed to fetch tasks'))
    );

    const wrapper = mount(<TaskList />);
    await new Promise(resolve => setTimeout(resolve, 0));

    wrapper.update();
    expect(wrapper.find('div').first().text()).toContain('Error:');
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

    const wrapper = mount(<TaskList />);
    await new Promise(resolve => setTimeout(resolve, 0));

    wrapper.update();
    expect(wrapper.find('li')).toHaveLength(2);
    expect(wrapper.find('li').first().find('span').first().text()).toBe('Task 1');
  });

  it('renders "No tasks yet" when tasks array is empty', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      })
    );

    const wrapper = mount(<TaskList />);
    await new Promise(resolve => setTimeout(resolve, 0));

    wrapper.update();
    expect(wrapper.find('p').text()).toBe('No tasks yet.');
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

    const wrapper = mount(<TaskList />);
    await new Promise(resolve => setTimeout(resolve, 0));

    wrapper.update();
    const statusSpans = wrapper.find('.task-item span').at(1);
    expect(statusSpans.text()).toContain('Pending');
  });
});
