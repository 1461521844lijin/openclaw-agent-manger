import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Agent } from '../types'
import { agentsApi } from '../api/agents'

export const useAgentsStore = defineStore('agents', () => {
  const agents = ref<Agent[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAgents() {
    loading.value = true
    error.value = null
    try {
      const response = await agentsApi.list()
      agents.value = response.items
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载失败'
    } finally {
      loading.value = false
    }
  }

  async function startAgent(id: string) {
    try {
      await agentsApi.start(id)
      const agent = agents.value.find((a) => a.id === id)
      if (agent) agent.status = 'running'
    } catch (e) {
      throw e
    }
  }

  async function stopAgent(id: string) {
    try {
      await agentsApi.stop(id)
      const agent = agents.value.find((a) => a.id === id)
      if (agent) agent.status = 'stopped'
    } catch (e) {
      throw e
    }
  }

  async function deleteAgent(id: string) {
    try {
      await agentsApi.delete(id)
      agents.value = agents.value.filter((a) => a.id !== id)
    } catch (e) {
      throw e
    }
  }

  return {
    agents,
    loading,
    error,
    fetchAgents,
    startAgent,
    stopAgent,
    deleteAgent,
  }
})
