/**
 * Centralized API configuration
 * Single source of truth for API base URL
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Common fetch wrapper with error handling
 */
export async function apiFetch<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const errorText = await response.text().catch(() => response.statusText);
    throw new Error(`HTTP ${response.status}: ${errorText}`);
  }
  
  return response.json();
}
