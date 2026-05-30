import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Lightweight wrapper around `MediaRecorder` for in-browser voice capture.
 * Captures into a single Blob (audio/webm) when stopped.
 */
export function useVoiceRecorder() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const startTimeRef = useRef<number>(0)
  const [isRecording, setIsRecording] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const cleanup = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    mediaRecorderRef.current = null
    chunksRef.current = []
  }, [])

  useEffect(() => () => cleanup(), [cleanup])

  const start = useCallback(async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/mp4',
      })
      mediaRecorderRef.current = recorder
      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.start()
      startTimeRef.current = Date.now()
      setIsRecording(true)
    } catch (e) {
      setError((e as Error).message || 'Microphone access denied')
      cleanup()
      throw e
    }
  }, [cleanup])

  const stop = useCallback((): Promise<{ blob: Blob; durationMs: number }> => {
    return new Promise((resolve, reject) => {
      const recorder = mediaRecorderRef.current
      if (!recorder) {
        reject(new Error('No active recorder'))
        return
      }
      const start = startTimeRef.current
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || 'audio/webm',
        })
        const durationMs = Date.now() - start
        cleanup()
        setIsRecording(false)
        resolve({ blob, durationMs })
      }
      recorder.stop()
    })
  }, [cleanup])

  const cancel = useCallback(() => {
    const recorder = mediaRecorderRef.current
    if (recorder && recorder.state !== 'inactive') {
      recorder.onstop = null
      recorder.stop()
    }
    cleanup()
    setIsRecording(false)
  }, [cleanup])

  return { isRecording, error, start, stop, cancel }
}
