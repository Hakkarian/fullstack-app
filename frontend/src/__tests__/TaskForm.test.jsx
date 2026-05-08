import React from 'react';
import { shallow, mount } from 'enzyme';
import TaskForm from '../TaskForm';

// Mock fetch API
global.fetch = jest.fn();

describe('TaskForm', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders form with input and button', () => {
    const wrapper = shallow(<TaskForm />);
    expect(wrapper.find('input')).toHaveLength(1);
    expect(wrapper.find('button')).toHaveLength(1);
    expect(wrapper.find('button').text()).toBe('Add Task');
  });

  it('updates input value on change', () => {
    const wrapper = mount(<TaskForm />);
    const input = wrapper.find('input');

    input.instance().value = 'New Task';
    input.simulate('change');
    wrapper.update();

    expect(wrapper.find('input').instance().value).toBe('New Task');
  });

  it('calls fetch on form submission', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      })
    );

    const onTaskCreated = jest.fn();
    const wrapper = mount(<TaskForm onTaskCreated={onTaskCreated} />);

    const input = wrapper.find('input');
    const form = wrapper.find('form');

    input.instance().value = 'New Task';
    input.simulate('change');

    form.simulate('submit', { preventDefault: () => {} });

    await new Promise(resolve => setTimeout(resolve, 0));

    expect(fetch).toHaveBeenCalledWith('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'New Task', completed: false })
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
    const wrapper = mount(<TaskForm onTaskCreated={onTaskCreated} />);

    const input = wrapper.find('input');
    const form = wrapper.find('form');

    input.instance().value = 'New Task';
    input.simulate('change');

    form.simulate('submit', { preventDefault: () => {} });

    await new Promise(resolve => setTimeout(resolve, 0));

    expect(onTaskCreated).toHaveBeenCalled();
  });

  it('displays error message on fetch failure', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Failed to create task'))
    );

    const wrapper = mount(<TaskForm />);
    const input = wrapper.find('input');
    const form = wrapper.find('form');

    input.instance().value = 'New Task';
    input.simulate('change');

    form.simulate('submit', { preventDefault: () => {} });

    await new Promise(resolve => setTimeout(resolve, 0));
    wrapper.update();

    expect(wrapper.find('.error').text()).toContain('Error:');
  });

  it('does not submit when title is empty', () => {
    const wrapper = mount(<TaskForm />);
    const form = wrapper.find('form');

    form.simulate('submit', { preventDefault: () => {} });

    expect(fetch).not.toHaveBeenCalled();
  });
});
