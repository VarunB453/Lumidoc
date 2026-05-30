import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Camera, Loader2 } from 'lucide-react'
import { useStore } from '@/store'
import MainLayout from '@/components/layout/MainLayout'
import { cn } from '@/lib/utils'
import { extractError, userApi } from '@/lib/api'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

const DOMAINS = [
  'AR & VR',
  'Auto & Transportation',
  'eCommerce & Retail',
  'Finance & Insurance',
  'Government',
  'Health & Life Sciences',
  'Logistics',
  'Manufacturing',
  'Robotics',
  'Technology',
  'Other',
]

const INTERESTS = [
  'AI Policy & Governance',
  'Computer Vision',
  'Enterprise AI',
  'MLOps & Infra',
  'NLP',
  'Research & Industry',
]

const PRONOUNS = ['she/her', 'he/him', 'they/them', 'Rather not say']

export default function SettingsPage() {
  const navigate = useNavigate()
  const { user, setUser } = useStore()
  const [saving, setSaving] = useState(false)
  const [avatarUploading, setAvatarUploading] = useState(false)
  const avatarInputRef = useRef<HTMLInputElement>(null)

  const [form, setForm] = useState({
    firstName: user?.name?.split(' ')[0] || '',
    lastName: user?.name?.split(' ').slice(1).join(' ') || '',
    jobTitle: '',
    company: '',
    location: '',
    bio: '',
    linkedinUrl: '',
    domains: [] as string[],
    interests: [] as string[],
    pronouns: '',
  })

  useEffect(() => {
    if (user?.name) {
      setForm((f) => ({
        ...f,
        firstName: user.name?.split(' ')[0] || f.firstName,
        lastName: user.name?.split(' ').slice(1).join(' ') || f.lastName,
      }))
    }
  }, [user?.name])

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      toast.error('Only image files are accepted')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Avatar must be under 5 MB')
      return
    }
    setAvatarUploading(true)
    try {
      const { avatar_url } = await userApi.uploadAvatar(file)
      if (user) setUser({ ...user, avatar_url })
      toast.success('Avatar updated')
    } catch (err) {
      toast.error(extractError(err))
    } finally {
      setAvatarUploading(false)
      if (avatarInputRef.current) avatarInputRef.current.value = ''
    }
  }

  const toggleTag = (list: string[], value: string) => {
    return list.includes(value) ? list.filter((v) => v !== value) : [...list, value]
  }

  const handleSave = async () => {
    const name = `${form.firstName.trim()} ${form.lastName.trim()}`.trim()
    if (!name) {
      toast.error('Name is required')
      return
    }
    setSaving(true)
    try {
      const updated = await userApi.updateProfile({ name })
      setUser(updated)
      toast.success('Profile saved')
    } catch (err) {
      toast.error(extractError(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <MainLayout className="overflow-y-auto" hideGhostCursor>
      <div className="max-w-3xl mx-auto px-6 py-10" style={{ backgroundColor: '#000000', minHeight: '100vh' }}>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-8"
        >
          {/* Headshot */}
          <div>
            <Label required>Headshot</Label>
            <div className="flex items-center gap-4 mt-2">
              <div className="relative">
                <div
                  className="w-20 h-20 rounded-full overflow-hidden"
                  style={{
                    background: 'linear-gradient(135deg, #a78bfa, #60a5fa, #f472b6, #fbbf24)',
                  }}
                >
                  {user?.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full" />
                  )}
                </div>
              </div>
              <input
                ref={avatarInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleAvatarUpload}
              />
              <button
                onClick={() => avatarInputRef.current?.click()}
                disabled={avatarUploading}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                style={{
                  backgroundColor: '#0A0A0A',
                  border: '1px solid rgba(255,255,255,0.1)',
                  color: '#F2F0E8',
                }}
              >
                {avatarUploading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Camera className="w-4 h-4" />
                )}
                Upload image
              </button>
            </div>
          </div>

          {/* Name fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <Label required>First Name</Label>
              <TextInput
                value={form.firstName}
                onChange={(v) => setForm({ ...form, firstName: v })}
                placeholder="John"
              />
            </div>
            <div>
              <Label required>Last Name</Label>
              <TextInput
                value={form.lastName}
                onChange={(v) => setForm({ ...form, lastName: v })}
                placeholder="Doe"
              />
            </div>
          </div>

          {/* Job Title & Company */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <Label required>Job Title</Label>
              <TextInput
                value={form.jobTitle}
                onChange={(v) => setForm({ ...form, jobTitle: v })}
                placeholder="Job"
              />
            </div>
            <div>
              <Label required>Company</Label>
              <TextInput
                value={form.company}
                onChange={(v) => setForm({ ...form, company: v })}
                placeholder="Company"
              />
            </div>
          </div>

          {/* Location */}
          <div>
            <Label>Location</Label>
            <TextInput
              value={form.location}
              onChange={(v) => setForm({ ...form, location: v })}
              placeholder="San Francisco, CA, USA"
            />
          </div>

          {/* Bio */}
          <div>
            <Label>Bio</Label>
            <textarea
              value={form.bio}
              onChange={(e) => setForm({ ...form, bio: e.target.value })}
              rows={4}
              placeholder="Tell us about yourself..."
              className="w-full mt-2 px-4 py-3 rounded-lg text-sm resize-none focus:outline-none focus:ring-1 focus:ring-[#E8622A]/50"
              style={{
                backgroundColor: '#0A0A0A',
                border: '1px solid rgba(255,255,255,0.08)',
                color: '#F2F0E8',
              }}
            />
          </div>

          {/* LinkedIn */}
          <div>
            <Label>LinkedIn Url</Label>
            <TextInput
              value={form.linkedinUrl}
              onChange={(v) => setForm({ ...form, linkedinUrl: v })}
              placeholder="https://www.linkedin.com/in/xxx"
            />
          </div>

          {/* Domain */}
          <div>
            <Label required>Domain</Label>
            <p className="text-[11px] mt-0.5" style={{ color: '#5A5A4E' }}>
              (Multiple Selection)
            </p>
            <div className="flex flex-wrap gap-2 mt-3">
              {DOMAINS.map((d) => (
                <TagButton
                  key={d}
                  label={d}
                  selected={form.domains.includes(d)}
                  onClick={() => setForm({ ...form, domains: toggleTag(form.domains, d) })}
                />
              ))}
            </div>
          </div>

          {/* Interests */}
          <div>
            <Label required>Interests</Label>
            <p className="text-[11px] mt-0.5" style={{ color: '#5A5A4E' }}>
              (Multiple Selection)
            </p>
            <div className="flex flex-wrap gap-2 mt-3">
              {INTERESTS.map((i) => (
                <TagButton
                  key={i}
                  label={i}
                  selected={form.interests.includes(i)}
                  onClick={() => setForm({ ...form, interests: toggleTag(form.interests, i) })}
                />
              ))}
            </div>
          </div>

          {/* Pronouns */}
          <div>
            <Label>Preferred Pronouns</Label>
            <div className="flex flex-wrap gap-2 mt-3">
              {PRONOUNS.map((p) => (
                <TagButton
                  key={p}
                  label={p}
                  selected={form.pronouns === p}
                  onClick={() => setForm({ ...form, pronouns: form.pronouns === p ? '' : p })}
                />
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4 pb-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2.5 rounded-full text-sm font-medium transition-colors"
              style={{
                border: '1px solid rgba(255,255,255,0.12)',
                color: '#F2F0E8',
                backgroundColor: 'transparent',
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2.5 rounded-full text-sm font-medium text-white transition-colors disabled:opacity-60"
              style={{ backgroundColor: '#E8622A' }}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </motion.div>
      </div>
    </MainLayout>
  )
}

/* ---------- Sub-components ---------- */

function Label({ children, required }: { children: React.ReactNode; required?: boolean }) {
  return (
    <label className="block text-sm font-semibold" style={{ color: '#F2F0E8' }}>
      {children}
      {required && <span style={{ color: '#E8622A' }}> *</span>}
    </label>
  )
}

function TextInput({
  value,
  onChange,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full mt-2 px-4 py-3 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-[#E8622A]/50"
      style={{
        backgroundColor: '#0A0A0A',
        border: '1px solid rgba(255,255,255,0.08)',
        color: '#F2F0E8',
      }}
    />
  )
}

function TagButton({
  label,
  selected,
  onClick,
}: {
  label: string
  selected: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150',
      )}
      style={{
        backgroundColor: selected ? 'rgba(232, 98, 42, 0.15)' : 'transparent',
        border: selected
          ? '1px solid rgba(232, 98, 42, 0.5)'
          : '1px solid rgba(255,255,255,0.12)',
        color: selected ? '#F0845A' : '#9A9A8A',
      }}
    >
      {label}
    </button>
  )
}
