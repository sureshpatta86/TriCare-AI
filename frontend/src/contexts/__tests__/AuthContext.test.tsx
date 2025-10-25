/**
 * Unit tests for AuthContext
 */
import React from 'react'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api-client'
import type { User, TokenResponse } from '@/types/auth'

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }
}))

const mockApi = api as jest.Mocked<typeof api>

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorageMock.clear()
  })

  describe('useAuth hook', () => {
    it('should throw error when used outside AuthProvider', () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation()
      
      expect(() => {
        renderHook(() => useAuth())
      }).toThrow('useAuth must be used within an AuthProvider')
      
      consoleError.mockRestore()
    })

    it('should provide auth context when used within AuthProvider', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current).toBeDefined()
      expect(result.current).toHaveProperty('user')
      expect(result.current).toHaveProperty('isAuthenticated')
      expect(result.current).toHaveProperty('login')
      expect(result.current).toHaveProperty('logout')
      expect(result.current).toHaveProperty('register')
    })
  })

  describe('Authentication State', () => {
    it('should initialize with no user', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('Login', () => {
    it('should login successfully and set user', async () => {
      const mockTokenResponse: TokenResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'bearer'
      }

      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2023-01-01T00:00:00Z',
      }

      mockApi.post.mockResolvedValueOnce({ data: mockTokenResponse })
      mockApi.get.mockResolvedValueOnce({ data: mockUser })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'password123'
        })
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.isAuthenticated).toBe(true)
      })
    })

    it('should handle login failure', async () => {
      mockApi.post.mockRejectedValueOnce({
        response: { data: { detail: 'Invalid credentials' } }
      })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      await expect(
        act(async () => {
          await result.current.login({
            email: 'test@example.com',
            password: 'wrong_password'
          })
        })
      ).rejects.toMatchObject({
        response: expect.objectContaining({
          data: expect.objectContaining({
            detail: 'Invalid credentials'
          })
        })
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('Register', () => {
    it('should register and auto-login successfully', async () => {
      const mockTokenResponse: TokenResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'bearer'
      }

      const mockUser: User = {
        id: 1,
        email: 'newuser@example.com',
        username: 'newuser',
        full_name: 'New User',
        is_active: true,
        is_verified: false,
        created_at: '2023-01-01T00:00:00Z',
      }

      mockApi.post
        .mockResolvedValueOnce({ data: mockTokenResponse })
        .mockResolvedValueOnce({ data: mockTokenResponse })
      mockApi.get.mockResolvedValueOnce({ data: mockUser })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      await act(async () => {
        await result.current.register({
          email: 'newuser@example.com',
          username: 'newuser',
          password: 'password123',
          full_name: 'New User'
        })
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.isAuthenticated).toBe(true)
      })
    })
  })

  describe('Logout', () => {
    it('should logout and clear user data', async () => {
      const mockTokenResponse: TokenResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'bearer'
      }

      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2023-01-01T00:00:00Z',
      }

      mockApi.post.mockResolvedValueOnce({ data: mockTokenResponse })
      mockApi.get.mockResolvedValueOnce({ data: mockUser })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      // First login
      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'password123'
        })
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
      })

      // Then logout
      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorageMock.getItem('tricare_access_token')).toBeNull()
      expect(localStorageMock.getItem('tricare_refresh_token')).toBeNull()
    })
  })

  describe('Update Profile', () => {
    it('should update user profile successfully', async () => {
      const mockTokenResponse: TokenResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'bearer'
      }

      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        is_active: true,
        is_verified: false,
        created_at: '2023-01-01T00:00:00Z',
      }

      const updatedUser: User = {
        ...mockUser,
        full_name: 'Updated Name',
        age: 30
      }

      mockApi.post.mockResolvedValueOnce({ data: mockTokenResponse })
      mockApi.get.mockResolvedValueOnce({ data: mockUser })
      mockApi.put.mockResolvedValueOnce({ data: updatedUser })

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      // Login first
      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'password123'
        })
      })

      // Update profile
      await act(async () => {
        await result.current.updateProfile({
          full_name: 'Updated Name',
          age: 30
        })
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(updatedUser)
      })
    })
  })
})
