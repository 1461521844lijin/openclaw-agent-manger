import api from './index'
import type { Agent, AgentCreate, AgentUpdate, ListResponse } from '../types'

export const agentsApi = {
  // Get all agents
  async list(params?: { status?: string; team_id?: string }): Promise<ListResponse<Agent>> {
    const response = await api.get<ListResponse<Agent>>('/agents', { params })
    return response.data
  },

  // Get single agent
  async get(id: string): Promise<Agent> {
    const response = await api.get<Agent>(`/agents/${id}`)
    return response.data
  },

  // Create agent
  async create(data: AgentCreate): Promise<Agent> {
    const response = await api.post<Agent>('/agents', data)
    return response.data
  },

  // Update agent
  async update(id: string, data: AgentUpdate): Promise<Agent> {
    const response = await api.put<Agent>(`/agents/${id}`, data)
    return response.data
  },

  // Delete agent
  async delete(id: string): Promise<void> {
    await api.delete(`/agents/${id}`)
  },

  // Start agent
  async start(id: string): Promise<{ message: string; agent_id: string }> {
    const response = await api.post(`/agents/${id}/start`)
    return response.data
  },

  // Stop agent
  async stop(id: string): Promise<{ message: string; agent_id: string }> {
    const response = await api.post(`/agents/${id}/stop`)
    return response.data
  },
}
