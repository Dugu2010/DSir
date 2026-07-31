'use client';

import { create } from 'zustand';
import { api } from './api';

interface User {
  id: string;
  email: string;
  username: string;
  display_name: string;
  avatar_url: string | null;
  bio: string | null;
  role: string;
  email_verified: boolean;
  last_login_at: string | null;
  created_at: string;
}

interface UserStats {
  total_xp: number;
  current_level: number;
  current_streak: number;
  longest_streak: number;
  lessons_completed: number;
  exercises_completed: number;
  projects_completed: number;
  total_time_spent_seconds: number;
}

interface AuthState {
  user: User | null;
  stats: UserStats | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setStats: (stats: UserStats | null) => void;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, username: string, displayName: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  stats: null,
  isLoading: true,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setStats: (stats) => set({ stats }),

  login: async (email: string, password: string) => {
    const data = await api.post<{ access_token: string; refresh_token: string }>('/auth/login', { email, password });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    await get().fetchUser();
  },

  signup: async (email: string, username: string, displayName: string, password: string) => {
    const data = await api.post<{ access_token: string; refresh_token: string }>('/auth/signup', {
      email, username, display_name: displayName, password,
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    await get().fetchUser();
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch { /* ignore */ }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, stats: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    try {
      const user = await api.get<User>('/auth/me');
      set({ user, isAuthenticated: true });
      try {
        const stats = await api.get<UserStats>('/users/me/stats');
        set({ stats });
      } catch { /* stats may not exist yet */ }
    } catch {
      set({ user: null, isAuthenticated: false });
    }
  },

  initialize: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isLoading: false });
      return;
    }
    try {
      await get().fetchUser();
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      set({ isLoading: false });
    }
  },
}));
