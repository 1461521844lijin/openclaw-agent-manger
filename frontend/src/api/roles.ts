import api from './index'
import type { Role, RoleCreate, RoleCategory, ListResponse } from '../types'

export const rolesApi = {
  // Get all roles
  async list(params?: { category?: string }): Promise<ListResponse<Role>> {
    const response = await api.get<ListResponse<Role>>('/roles', { params })
    return response.data
  },

  // Get role categories
  async categories(): Promise<{ categories: RoleCategory[] }> {
    const response = await api.get<{ categories: RoleCategory[] }>('/roles/categories')
    return response.data
  },

  // Get single role
  async get(id: string): Promise<Role> {
    const response = await api.get<Role>(`/roles/${id}`)
    return response.data
  },

  // Create custom role
  async create(data: RoleCreate): Promise<Role> {
    const response = await api.post<Role>('/roles', data)
    return response.data
  },

  // Update role
  async update(id: string, data: Partial<RoleCreate>): Promise<Role> {
    const response = await api.put<Role>(`/roles/${id}`, data)
    return response.data
  },

  // Delete role
  async delete(id: string): Promise<void> {
    await api.delete(`/roles/${id}`)
  },
}
