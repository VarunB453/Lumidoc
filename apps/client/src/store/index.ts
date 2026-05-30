import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import {
  authApi,
  chatApi,
  filesApi,
  refreshTokens,
  tokenStore,
  userApi,
} from '@/lib/api'
import type {
  Conversation,
  FileMetadata,
  User,
  UserPreferences,
} from '@/types'

interface AppState {
  // ---------- Auth ----------
  user: User | null
  isAuthenticated: boolean
  authReady: boolean
  setUser: (user: User | null) => void
  hydrate: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>

  // ---------- Conversations ----------
  conversations: Conversation[]
  activeConversationId: string | null
  setActiveConversation: (id: string | null) => void
  loadConversations: () => Promise<void>
  createConversation: (payload: { title?: string; file_ids?: string[] }) => Promise<Conversation>
  updateConversation: (
    id: string,
    payload: { title?: string; is_favorite?: boolean; file_ids?: string[] },
  ) => Promise<Conversation>
  removeConversation: (id: string) => Promise<void>
  upsertConversation: (conv: Conversation) => void

  // ---------- Files ----------
  files: FileMetadata[]
  loadFiles: () => Promise<void>
  upsertFile: (file: FileMetadata) => void
  removeFile: (id: string) => Promise<void>

  // ---------- UI state ----------
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  sidebarTab: 'history' | 'favorites'
  setSidebarTab: (tab: 'history' | 'favorites') => void

  // ---------- Preferences ----------
  preferences: UserPreferences
  updatePreferences: (preferences: Partial<UserPreferences>) => void
}

const defaultPreferences: UserPreferences = {
  theme: 'dark',
  language: 'en',
  notifications: { email: true, push: true, sound: false },
}

export const useStore = create<AppState>()(
  persist(
    (set, _get) => ({
      // ---------- Auth ----------
      user: null,
      isAuthenticated: false,
      authReady: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      hydrate: async () => {
        // No access token at all → user is anonymous; don't hit /users/me.
        const access = tokenStore.getAccess()
        if (!access) {
          set({ authReady: true, isAuthenticated: false, user: null })
          return
        }
        // Access token is already expired (or about to be). Refresh first so
        // we don't fire a guaranteed-401 GET /users/me on every cold load.
        if (tokenStore.isAccessExpired()) {
          const tokens = await refreshTokens()
          if (!tokens) {
            tokenStore.clear()
            set({ user: null, isAuthenticated: false, authReady: true })
            return
          }
        }
        try {
          const me = await userApi.me()
          set({ user: me, isAuthenticated: true, authReady: true })
        } catch {
          tokenStore.clear()
          set({ user: null, isAuthenticated: false, authReady: true })
        }
      },

      login: async (email, password) => {
        const { user, tokens } = await authApi.login(email, password)
        tokenStore.set(tokens)
        set({ user, isAuthenticated: true, authReady: true })
      },

      signup: async (name, email, password) => {
        const { user, tokens } = await authApi.register(name, email, password)
        tokenStore.set(tokens)
        set({ user, isAuthenticated: true, authReady: true })
      },

      logout: async () => {
        const refresh = tokenStore.getRefresh()
        if (refresh) {
          try {
            await authApi.logout(refresh)
          } catch {
            // ignore — best-effort
          }
        }
        tokenStore.clear()
        set({
          user: null,
          isAuthenticated: false,
          conversations: [],
          files: [],
          activeConversationId: null,
        })
      },

      // ---------- Conversations ----------
      conversations: [],
      activeConversationId: null,
      setActiveConversation: (id) => set({ activeConversationId: id }),

      loadConversations: async () => {
        const list = await chatApi.listConversations()
        set({ conversations: list })
      },

      createConversation: async (payload) => {
        const conv = await chatApi.createConversation(payload)
        set((state) => ({ conversations: [conv, ...state.conversations] }))
        return conv
      },

      updateConversation: async (id, payload) => {
        const updated = await chatApi.updateConversation(id, payload)
        set((state) => ({
          conversations: state.conversations.map((c) => (c.id === id ? updated : c)),
        }))
        return updated
      },

      removeConversation: async (id) => {
        await chatApi.deleteConversation(id)
        set((state) => ({
          conversations: state.conversations.filter((c) => c.id !== id),
          activeConversationId:
            state.activeConversationId === id ? null : state.activeConversationId,
        }))
      },

      upsertConversation: (conv) =>
        set((state) => {
          const exists = state.conversations.some((c) => c.id === conv.id)
          return {
            conversations: exists
              ? state.conversations.map((c) => (c.id === conv.id ? conv : c))
              : [conv, ...state.conversations],
          }
        }),

      // ---------- Files ----------
      files: [],

      loadFiles: async () => {
        const list = await filesApi.list()
        set({ files: list })
      },

      upsertFile: (file) =>
        set((state) => {
          const exists = state.files.some((f) => f.id === file.id)
          return {
            files: exists
              ? state.files.map((f) => (f.id === file.id ? file : f))
              : [file, ...state.files],
          }
        }),

      removeFile: async (id) => {
        await filesApi.remove(id)
        set((state) => ({ files: state.files.filter((f) => f.id !== id) }))
      },

      // ---------- UI ----------
      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      sidebarTab: 'history',
      setSidebarTab: (tab) => set({ sidebarTab: tab }),

      // ---------- Preferences ----------
      preferences: defaultPreferences,
      updatePreferences: (prefs) =>
        set((state) => ({ preferences: { ...state.preferences, ...prefs } })),
    }),
    {
      name: 'lumidoc-store',
      partialize: (state) => ({
        preferences: state.preferences,
        sidebarCollapsed: state.sidebarCollapsed,
        sidebarTab: state.sidebarTab,
      }),
    },
  ),
)
