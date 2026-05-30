import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, FileText, Music, Video } from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

const acceptedTypes = {
  'application/pdf': ['.pdf'],
  'audio/*': ['.mp3', '.wav', '.m4a'],
  'video/*': ['.mp4', '.mov'],
}

interface FileDropzoneProps {
  onFilesDrop: (files: File[]) => void
}

export default function FileDropzone({ onFilesDrop }: FileDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onFilesDrop(acceptedFiles)
      toast.success(`${acceptedFiles.length} file(s) added to upload queue`)
    },
    [onFilesDrop]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    multiple: true,
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <div
        {...getRootProps()}
        className={cn(
          'relative rounded-3xl border-2 border-dashed p-12 text-center transition-all duration-300 cursor-pointer',
          'hover:border-[#E8622A]/50',
          isDragActive && 'scale-[1.02]',
          isDragReject && 'border-red-400',
          'focus-ring'
        )}
        style={{
          backgroundColor: isDragActive ? 'rgba(232, 98, 42, 0.05)' : 'rgba(10, 10, 10, 0.5)',
          borderColor: isDragActive ? '#E8622A' : isDragReject ? '#ef4444' : 'rgba(255,255,255,0.1)',
        }}
      >
        <input {...getInputProps()} />

        <motion.div
          animate={isDragActive ? { y: [0, -10, 0] } : {}}
          transition={{ duration: 0.6, repeat: isDragActive ? Infinity : 0 }}
        >
          <div className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6" style={{ backgroundColor: 'rgba(232, 98, 42, 0.1)' }}>
            <Upload className="w-10 h-10" style={{ color: '#E8622A' }} />
          </div>
        </motion.div>

        <h3 className="text-xl font-display font-semibold mb-2" style={{ color: '#F2F0E8' }}>
          {isDragActive ? 'Drop files here' : 'Drop files here or click to browse'}
        </h3>
        <p className="text-sm mb-6" style={{ color: '#8A8A7A' }}>
          Support for PDF, MP3, MP4, WAV, MOV, M4A
        </p>

        <div className="flex items-center justify-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)' }}>
            <FileText className="w-5 h-5 text-red-400" />
            <span className="text-xs font-medium text-red-400">PDF</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}>
            <Music className="w-5 h-5 text-blue-400" />
            <span className="text-xs font-medium text-blue-400">Audio</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}>
            <Video className="w-5 h-5 text-green-400" />
            <span className="text-xs font-medium text-green-400">Video</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
