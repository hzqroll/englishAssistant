import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorHighlight from '../ErrorHighlight.vue'
import type { ErrorDetail } from '@/stores/types'

describe('ErrorHighlight', () => {
  const originalText = 'what is you nama'
  const correctedText = 'What are you name'
  const errors: ErrorDetail[] = [
    {
      id: 'err-1',
      type: 'grammar',
      severity: 'medium',
      originalText: 'what',
      correctedText: 'What',
      message: 'Sentence start',
      startPosition: 0,
      endPosition: 4
    },
    {
      id: 'err-2',
      type: 'grammar',
      severity: 'medium',
      originalText: 'is',
      correctedText: 'are',
      message: 'Verb agreement',
      startPosition: 5,
      endPosition: 7
    },
    {
      id: 'err-3',
      type: 'spelling',
      severity: 'low',
      originalText: 'nama',
      correctedText: 'name',
      message: 'Spelling',
      startPosition: 12,
      endPosition: 16
    }
  ]

  it('renders original text with highlights correctly', () => {
    const wrapper = mount(ErrorHighlight, {
      props: {
        originalText,
        correctedText,
        errors,
        viewMode: 'original-only'
      }
    })

    const spans = wrapper.findAll('span[data-error-id]')
    expect(spans).toHaveLength(3)
    expect(spans[0].text()).toBe('what')
    expect(spans[1].text()).toBe('is')
    expect(spans[2].text()).toBe('nama')
  })

  it('renders corrected text with highlights correctly', () => {
    // This verifies the fix: constructing corrected view using original indices but corrected content
    const wrapper = mount(ErrorHighlight, {
      props: {
        originalText,
        correctedText,
        errors,
        viewMode: 'corrected-only'
      }
    })

    // The text content should match the full corrected sentence
    expect(wrapper.text()).toContain('What')
    expect(wrapper.text()).toContain('are')
    expect(wrapper.text()).toContain('name')
    
    // Check specific spans
    const spans = wrapper.findAll('span[data-error-id]')
    expect(spans).toHaveLength(3)
    
    // Verify span content is from correctedText
    expect(spans[0].text()).toBe('What')
    expect(spans[1].text()).toBe('are')
    expect(spans[2].text()).toBe('name')

    // Verify surrounding text is preserved/reconstructed correctly
    // The component renders HTML, so let's check the full text content of the container
    const container = wrapper.find('.whitespace-pre-wrap')
    // We expect "What are you name" (with possible extra spaces depending on rendering)
    // "What" + " " + "are" + " you " + "name"
    // Note: The component logic concatenates: 
    // "" + Span(What) + " " + Span(are) + " you " + Span(name) + ""
    // Text: "What are you name"
    expect(container.text().replace(/\s+/g, ' ').trim()).toBe('What are you name')
  })

  it('emits events on interaction', async () => {
    const wrapper = mount(ErrorHighlight, {
      props: {
        originalText,
        correctedText,
        errors,
        viewMode: 'original-only'
      }
    })

    const span = wrapper.find('span[data-error-id="err-1"]')
    
    await span.trigger('click')
    expect(wrapper.emitted('errorClick')?.[0]).toEqual([errors[0]])

    // Use mouseover because we use event delegation with bubbling
    await span.trigger('mouseover')
    expect(wrapper.emitted('errorHover')?.[0]).toEqual([errors[0]])
    
    // Trigger mouseover on the container (to simulate leaving the span but staying in container)
    // OR trigger mouseleave on container
    // Our component logic handles "move to null" when hovering something without data-error-id
    // But testing that via span trigger is tricky.
    // Let's test the container mouseleave
    const container = wrapper.find('.whitespace-pre-wrap')
    await container.trigger('mouseleave')
    expect(wrapper.emitted('errorHover')?.[1]).toEqual([null])
  })
})
