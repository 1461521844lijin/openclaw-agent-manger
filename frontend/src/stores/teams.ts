import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Team, TeamDetail } from '../types'
import { teamsApi } from '../api/teams'

export const useTeamsStore = defineStore('teams', () => {
  const teams = ref<Team[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTeams() {
    loading.value = true
    error.value = null
    try {
      const response = await teamsApi.list()
      teams.value = response.items
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载失败'
    } finally {
      loading.value = false
    }
  }

  async function deleteTeam(id: string) {
    try {
      await teamsApi.delete(id)
      teams.value = teams.value.filter((t) => t.id !== id)
    } catch (e) {
      throw e
    }
  }

  return {
    teams,
    loading,
    error,
    fetchTeams,
    deleteTeam,
  }
})
