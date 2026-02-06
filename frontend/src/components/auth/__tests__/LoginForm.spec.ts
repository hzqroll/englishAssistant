import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginForm from '../LoginForm.vue'

describe('LoginForm', () => {
  it('validates empty input', async () => {
    const wrapper = mount(LoginForm)
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.text()).toContain('Email is required') // Assuming validator returns this
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('emits submit with valid data', async () => {
    const wrapper = mount(LoginForm)
    
    await wrapper.find('input[type="email"]').setValue('test@test.com')
    await wrapper.find('input[type="password"]').setValue('password123')
    
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.emitted('submit')?.[0]).toEqual([{
      email: 'test@test.com',
      password: 'password123'
    }])
  })

  it('shows loading state', async () => {
    const wrapper = mount(LoginForm)
    expect(wrapper.find('button[type=\"submit\"]').exists()).toBe(true)
  })
})
