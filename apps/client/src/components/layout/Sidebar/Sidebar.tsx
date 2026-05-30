import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Home,
  Layout,
  Settings,
  Trash2,
  ChevronDown,
  Plus,
  LogOut,
  Zap,
  CheckSquare,
} from 'lucide-react'
import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import Avatar from '@/components/ui/Avatar'
import toast from 'react-hot-toast'

const navItems = [
  { icon: Home, label: 'Home', path: '/dashboard' },
  { icon: CheckSquare, label: 'Remember', path: '/files' },
  { icon: Settings, label: 'Settings', path: '/settings' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const {
    conversations,
    user,
    logout,
    loadConversations,
    createConversation,
    removeConversation,
    sidebarCollapsed,
    toggleSidebar,
  } = useStore()
  useEffect(() => {
    loadConversations().catch(() => {})
  }, [loadConversations])

  const filteredConversations = conversations

  const today = filteredConversations.filter((c) => {
    const diff = Date.now() - new Date(c.updated_at).getTime()
    return diff < 86400000
  })
  const older = filteredConversations.filter((c) => {
    const diff = Date.now() - new Date(c.updated_at).getTime()
    return diff >= 86400000
  })

  const handleNavClick = (item: typeof navItems[0]) => {
    if (item.path) {
      navigate(item.path)
    }
  }

  const handleChatClick = (chatId: string) => {
    navigate(`/chat/${chatId}`)
  }

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    try {
      await removeConversation(id)
      toast.success('Chat deleted')
      if (location.pathname === `/chat/${id}`) navigate('/dashboard')
    } catch {
      toast.error('Failed to delete')
    }
  }

  const handleNewChat = async () => {
    try {
      const conv = await createConversation({ title: 'New conversation' })
      navigate(`/chat/${conv.id}`)
    } catch {
      toast.error('Failed to create chat')
    }
  }

  const renderGroup = (label: string, items: typeof filteredConversations) => {
    if (items.length === 0) return null
    return (
      <div className="mb-4">
        <h3
          className="text-[11px] font-bold uppercase tracking-wider mb-2 px-3"
          style={{ color: '#E8622A' }}
        >
          {label}
        </h3>
        <div className="space-y-0.5">
          {items.map((chat) => (
            <div
              key={chat.id}
              role="button"
              tabIndex={0}
              onClick={() => handleChatClick(chat.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  handleChatClick(chat.id)
                }
              }}
              className={cn(
                'w-full text-left px-3 py-2 rounded-lg transition-all duration-150 group cursor-pointer',
                location.pathname === `/chat/${chat.id}`
                  ? 'bg-white/[0.06]'
                  : 'hover:bg-white/[0.03]',
              )}
            >
              <div className="flex items-center justify-between">
                <p
                  className="text-[13px] truncate flex-1"
                  style={{ color: '#D4D4C8' }}
                >
                  {chat.title}
                </p>
                <button
                  onClick={(e) => handleDelete(e, chat.id)}
                  className="opacity-0 group-hover:opacity-100 w-6 h-6 rounded flex items-center justify-center transition-all flex-shrink-0 ml-2"
                  style={{ color: '#5A5A4E' }}
                  aria-label="Delete chat"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <aside
      className="fixed left-0 top-0 h-full z-40 flex flex-col overflow-hidden transition-[width] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]"
      style={{
        width: sidebarCollapsed ? 60 : 240,
        backgroundColor: 'rgba(0, 0, 0, 0.97)',
        borderRight: '1px solid rgba(255, 255, 255, 0.05)',
      }}
    >
      {/* Logo + New button */}
      <div className={cn("px-4 pt-5 pb-3 flex items-center", sidebarCollapsed ? "justify-center" : "justify-between")}>
        {!sidebarCollapsed && (
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: '#E8622A' }}
            />
            <span className="text-xs font-medium" style={{ color: '#5A5A4E' }}>
              LumiDoc
            </span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <button
            onClick={toggleSidebar}
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5"
            style={{ color: '#5A5A4E' }}
            aria-label="Toggle sidebar"
          >
            <Layout className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 mb-4">
        {sidebarCollapsed ? (
          <button
            onClick={handleNewChat}
            className="w-7 h-7 mx-auto rounded-lg flex items-center justify-center transition-all duration-200 hover:bg-white/[0.03]"
            style={{ border: '1px solid rgba(255, 255, 255, 0.1)' }}
            aria-label="New chat"
          >
            <Plus className="w-4 h-4" style={{ color: '#E8622A' }} />
          </button>
        ) : (
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl transition-all duration-200 hover:bg-white/[0.03]"
            style={{
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <span className="text-sm font-semibold" style={{ color: '#F2F0E8' }}>
              NEW
            </span>
            <Zap className="w-4 h-4" style={{ color: '#E8622A' }} />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="px-3 mb-4">
        {navItems.map((item) => {
          const isActive = item.path && location.pathname === item.path
          return (
            <button
              key={item.label}
              onClick={() => handleNavClick(item)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-150 mb-0.5',
                sidebarCollapsed && 'justify-center px-0',
                isActive
                  ? 'bg-white/[0.06]'
                  : 'hover:bg-white/[0.03]',
              )}
              style={{
                border: isActive ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid transparent',
              }}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <item.icon
                className="w-4 h-4 flex-shrink-0"
                style={{ color: isActive ? '#F2F0E8' : '#8A8A7A' }}
              />
              {!sidebarCollapsed && (
                <span
                  className="text-[13px] font-medium"
                  style={{ color: isActive ? '#F2F0E8' : '#8A8A7A' }}
                >
                  {item.label}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Divider */}
      <div className="mx-4 mb-3" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }} />

      {/* Chat history */}
      {!sidebarCollapsed && (
        <div className="flex-1 overflow-y-auto scrollbar-thin px-1">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-6 px-4">
              <p className="text-xs" style={{ color: '#5A5A4E' }}>
                No conversations yet
              </p>
            </div>
          ) : (
            <>
              {renderGroup('Today', today)}
              {renderGroup('Previous', older)}
            </>
          )}
        </div>
      )}

      {sidebarCollapsed && <div className="flex-1" />}

      {/* User profile at bottom */}
      <div
        className="px-4 py-3 mt-auto"
        style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
      >
        {sidebarCollapsed ? (
          <div className="flex justify-center">
            <Avatar
              src={user?.avatar_url || undefined}
              name={user?.name}
              size="sm"
            />
          </div>
        ) : (
          <>
            <div className="flex items-center gap-3 mb-3">
              <Avatar
                src={user?.avatar_url || undefined}
                name={user?.name}
                size="sm"
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate" style={{ color: '#F2F0E8' }}>
                  {user?.name || 'User'}
                </p>
                <p className="text-[11px] truncate" style={{ color: '#5A5A4E' }}>
                  Free Plan
                </p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" style={{ color: '#5A5A4E' }} />
            </div>
            <button
              onClick={() => {
                logout()
                navigate('/login')
              }}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-all duration-150 hover:bg-white/[0.04]"
            >
              <LogOut className="w-4 h-4" style={{ color: '#E8622A' }} />
              <span className="text-[13px] font-medium" style={{ color: '#E8622A' }}>
                Logout
              </span>
            </button>
          </>
        )}
      </div>
    </aside>
  )
}
