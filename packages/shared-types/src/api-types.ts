/**
 * Auto-generated types from OpenAPI specification.
 * Do not edit manually - run `npm run generate` to update.
 */

// Placeholder - will be generated from openapi.yaml
export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T = unknown> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ErrorResponse {
  detail: string;
  status: number;
  type?: string;
}
