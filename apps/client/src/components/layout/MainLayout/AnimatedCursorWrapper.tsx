import {
  Cursor,
  CursorProvider,
} from '@/components/animate-ui/components/animate/cursor'

export default function AnimatedCursorWrapper() {
  return (
    <CursorProvider global>
      <Cursor />
    </CursorProvider>
  )
}
