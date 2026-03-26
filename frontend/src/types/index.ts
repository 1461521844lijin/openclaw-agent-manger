// API Types - match backend schemas

export type AgentStatus = 'stopped' | 'running' | 'error' | 'starting'

export interface Agent {
  id: string
  name: string
  role: string
  workspace: string
  agent_dir?: string
  description?: string
  config?: Record<string, unknown>
  status: AgentStatus
  team_id?: string
  created_at: string
  updated_at: string
}

export interface AgentCreate {
  name: string
  role: string
  workspace?: string
  agent_dir?: string
  description?: string
  config?: Record<string, unknown>
  team_id?: string
}

export interface AgentUpdate {
  name?: string
  role?: string
  workspace?: string
  agent_dir?: string
  description?: string
  config?: Record<string, unknown>
  team_id?: string
}

export interface CollaborationRule {
  source_id: string
  target_id: string
  trigger: string
}

export interface Team {
  id: string
  name: string
  description?: string
  collaborations?: CollaborationRule[]
  agents: string[]
  created_at: string
  updated_at: string
}

export interface TeamDetail extends Team {
  agent_details: Array<{
    id: string
    name: string
    role: string
    status: string
  }>
}

export interface TeamCreate {
  name: string
  description?: string
  collaborations?: CollaborationRule[]
  agent_ids: string[]
}

export interface TeamUpdate {
  name?: string
  description?: string
  collaborations?: CollaborationRule[]
  agent_ids?: string[]
}

export interface Role {
  id: string
  name: string
  name_en: string
  emoji?: string
  description?: string
  description_en?: string
  core_mission?: string
  critical_rules?: string
  category?: string
  is_builtin: boolean
  created_at: string
  updated_at: string
}

export interface RoleCreate {
  name: string
  name_en: string
  emoji?: string
  description?: string
  description_en?: string
  core_mission?: string
  critical_rules?: string
  category?: string
}

export interface RoleCategory {
  id: string
  label: string
  items: Role[]
}

// API Response types
export interface ApiResponse<T> {
  items?: T[]
  total?: number
  message?: string
  result?: T
}

export interface ListResponse<T> {
  items: T[]
  total: number
}
