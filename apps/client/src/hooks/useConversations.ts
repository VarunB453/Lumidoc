/**
 * TanStack Query hooks for conversation operations.
 * Replaces raw useEffect-based data fetching with proper caching,
 * background refetching, and optimistic updates.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatApi } from '@/lib/api'
import type { Conversation } from '@/types'

export const conversationKeys = {
  all: ['conversations'] as const,
  list: (favorites?: boolean) => [...conversationKeys.all, 'list', { favorites }] as const,
  detail: (id: string) => [...conversationKeys.all, 'detail', id] as const,
  messages: (id: string) => [...conversationKeys.all, 'messages', id] as const,
}

/**
 * Fetch all conversations (optionally filtered to favorites).
 */
export function useConversations(favorites = false) {
  return useQuery({
    queryKey: conversationKeys.list(favorites),
    queryFn: () => chatApi.listConversations(favorites),
    staleTime: 15_000, // 15s
  })
}

/**
 * Fetch a single conversation by ID.
 */
export function useConversation(id: string | undefined) {
  return useQuery({
    queryKey: conversationKeys.detail(id!),
    queryFn: () => chatApi.getConversation(id!),
    enabled: !!id,
  })
}

/**
 * Fetch messages for a conversation.
 */
export function useMessages(conversationId: string | undefined) {
  return useQuery({
    queryKey: conversationKeys.messages(conversationId!),
    queryFn: () => chatApi.listMessages(conversationId!),
    enabled: !!conversationId,
  })
}

/**
 * Create a new conversation. Invalidates the list on success.
 */
export function useCreateConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: { title?: string; file_ids?: string[] }) =>
      chatApi.createConversation(payload),
    onSuccess: (newConv) => {
      queryClient.invalidateQueries({ queryKey: conversationKeys.list() })
      queryClient.setQueryData(conversationKeys.detail(newConv.id), newConv)
    },
  })
}

/**
 * Update a conversation (title, favorite, file_ids).
 */
export function useUpdateConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string
      payload: { title?: string; is_favorite?: boolean; file_ids?: string[] }
    }) => chatApi.updateConversation(id, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(conversationKeys.detail(updated.id), updated)
      queryClient.invalidateQueries({ queryKey: conversationKeys.list() })
    },
  })
}

/**
 * Delete a conversation. Optimistically removes from cached list.
 */
export function useDeleteConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => chatApi.deleteConversation(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: conversationKeys.list() })
      const previous = queryClient.getQueryData<Conversation[]>(conversationKeys.list())
      queryClient.setQueryData<Conversation[]>(conversationKeys.list(), (old) =>
        old ? old.filter((c) => c.id !== id) : [],
      )
      return { previous }
    },
    onError: (_err, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(conversationKeys.list(), context.previous)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: conversationKeys.list() })
    },
  })
}
