import api from './index'
import type { Team, TeamDetail, TeamCreate, TeamUpdate, ListResponse } from '../types'

export const teamsApi = {
  // Get all teams
  async list(): Promise<ListResponse<Team>> {
    const response = await api.get<ListResponse<Team>>('/teams')
    return response.data
  },

  // Get single team with details
  async get(id: string): Promise<TeamDetail> {
    const response = await api.get<TeamDetail>(`/teams/${id}`)
    return response.data
  },

  // Create team
  async create(data: TeamCreate): Promise<Team> {
    const response = await api.post<Team>('/teams', data)
    return response.data
  },

  // Update team
  async update(id: string, data: TeamUpdate): Promise<Team> {
    const response = await api.put<Team>(`/teams/${id}`, data)
    return response.data
  },

  // Delete team
  async delete(id: string): Promise<void> {
    await api.delete(`/teams/${id}`)
  },

  // Deploy team
  async deploy(id: string): Promise<{ message: string; team_id: string; result?: unknown }> {
    const response = await api.post(`/teams/${id}/deploy`)
    return response.data
  },

  // Teardown team
  async teardown(id: string): Promise<{ message: string; team_id: string; result?: unknown }> {
    const response = await api.post(`/teams/${id}/teardown`)
    return response.data
  },
}
