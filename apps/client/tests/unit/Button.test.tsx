import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import Button from '@/components/ui/Button/Button'

describe('Button', () => {
  it('renders its children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('fires onClick when pressed', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Go</Button>)
    await userEvent.click(screen.getByRole('button', { name: 'Go' }))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('shows a loading state and disables interaction', async () => {
    const onClick = vi.fn()
    render(
      <Button isLoading onClick={onClick}>
        Submit
      </Button>,
    )
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveTextContent('Loading...')
    await userEvent.click(button)
    expect(onClick).not.toHaveBeenCalled()
  })

  it('respects the disabled prop', () => {
    render(<Button disabled>Nope</Button>)
    expect(screen.getByRole('button', { name: 'Nope' })).toBeDisabled()
  })
})
