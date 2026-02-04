import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RegisterForm from '../RegisterForm.vue'

describe('RegisterForm', () => {
  it('validates password match', async () => {
    const wrapper = mount(RegisterForm)
    
    await wrapper.find('input[placeholder="username"]').setValue('user')
    await wrapper.find('input[placeholder="your@email.com"]').setValue('test@test.com')
    await wrapper.find('input[placeholder="••••••••"]').setValue('pass1') // First password input
    // The second password input also has placeholder ••••••••, need to be specific.
    // The component uses id="confirmPassword"
    await wrapper.find('#confirmPassword').setValue('pass2')
    
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.text()).toContain('Passwords do not match')
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('emits submit with valid data', async () => {
    const wrapper = mount(RegisterForm)
    
    await wrapper.find('#username').setValue('user')
    await wrapper.find('#email').setValue('test@test.com')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('#confirmPassword').setValue('password123')
    
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(wrapper.emitted('submit')?.[0]).toEqual([{
      username: 'user',
      email: 'test@test.com',
      password: 'password123'
    }])
  })
})
