import api from './index'

export interface GatewayStatus {
  running: boolean
  port?: number
  url?: string
  error?: string
  details?: Record<string, unknown>
}

export const gatewayApi = {
  // Get gateway status
  async status(): Promise<GatewayStatus> {
    const response = await api.get<GatewayStatus>('/gateway/status')
    return response.data
  },

  // Start gateway
  async start(): Promise<{ success: boolean; message: string; error?: string }> {
    const response = await api.post('/gateway/start')
    return response.data
  },

  // Stop gateway
  async stop(): Promise<{ success: boolean; message: string; error?: string }> {
    const response = await api.post('/gateway/stop')
    return response.data
  },

  // Get OpenClaw agents
  async agents(): Promise<{ agents: Array<Record<string, unknown>> }> {
    const response = await api.get('/gateway/agents')
    return response.data
  },
}
