/**
 * TanStack Query hooks for file operations.
 * Replaces raw useEffect-based data fetching with proper caching,
 * background refetching, and optimistic updates.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { filesApi } from '@/lib/api'
import type { FileMetadata } from '@/types'

export const fileKeys = {
  all: ['files'] as const,
  list: () => [...fileKeys.all, 'list'] as const,
  detail: (id: string) => [...fileKeys.all, 'detail', id] as const,
}

/**
 * Fetch the full list of user files with caching and background refetch.
 */
export function useFiles() {
  return useQuery({
    queryKey: fileKeys.list(),
    queryFn: () => filesApi.list(),
    staleTime: 30_000, // 30s before background refetch
  })
}

/**
 * Fetch a single file's metadata.
 */
export function useFile(id: string | undefined) {
  return useQuery({
    queryKey: fileKeys.detail(id!),
    queryFn: () => filesApi.get(id!),
    enabled: !!id,
  })
}

/**
 * Upload a file with progress tracking. Invalidates the file list on success.
 */
export function useUploadFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      file,
      onProgress,
      signal,
    }: {
      file: File
      onProgress?: (percent: number) => void
      signal?: AbortSignal
    }) => filesApi.upload(file, onProgress, signal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fileKeys.list() })
    },
  })
}

/**
 * Delete a file. Optimistically removes it from the cached list.
 */
export function useDeleteFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => filesApi.remove(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: fileKeys.list() })
      const previous = queryClient.getQueryData<FileMetadata[]>(fileKeys.list())
      queryClient.setQueryData<FileMetadata[]>(fileKeys.list(), (old) =>
        old ? old.filter((f) => f.id !== id) : [],
      )
      return { previous }
    },
    onError: (_err, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(fileKeys.list(), context.previous)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: fileKeys.list() })
    },
  })
}
