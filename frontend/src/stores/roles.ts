import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Role, RoleCategory } from '../types'
import { rolesApi } from '../api/roles'

export const useRolesStore = defineStore('roles', () => {
  const roles = ref<Role[]>([])
  const categories = ref<RoleCategory[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchRoles() {
    loading.value = true
    error.value = null
    try {
      const response = await rolesApi.list()
      roles.value = response.items
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const response = await rolesApi.categories()
      categories.value = response.categories
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载分类失败'
    }
  }

  return {
    roles,
    categories,
    loading,
    error,
    fetchRoles,
    fetchCategories,
  }
})
