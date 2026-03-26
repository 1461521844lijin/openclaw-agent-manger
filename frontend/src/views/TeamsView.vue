<template>
  <div class="teams-view">
    <div class="page-header">
      <h1 class="page-title">团队管理</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建团队
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="team in teamsStore.teams" :key="team.id">
        <el-card class="team-card" shadow="hover">
          <template #header>
            <div class="team-header">
              <span class="team-name">{{ team.name }}</span>
              <el-tag size="small">{{ team.agents.length }} 个智能体</el-tag>
            </div>
          </template>
          <p class="team-desc">{{ team.description || '暂无描述' }}</p>
          <div class="team-agents">
            <el-tag
              v-for="agentId in team.agents.slice(0, 3)"
              :key="agentId"
              size="small"
              class="agent-tag"
            >
              {{ getAgentName(agentId) }}
            </el-tag>
            <el-tag v-if="team.agents.length > 3" size="small" type="info">
              +{{ team.agents.length - 3 }}
            </el-tag>
          </div>
          <div class="team-actions">
            <el-button type="primary" size="small" @click="openDetailDialog(team)">
              详情
            </el-button>
            <el-button type="info" size="small" @click="openEditDialog(team)">
              编辑
            </el-button>
            <el-button type="success" size="small" @click="handleDeploy(team.id)">
              部署
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(team.id)">
              删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showFormDialog"
      :title="editingTeam ? '编辑团队' : '创建团队'"
      width="600px"
    >
      <el-form :model="teamForm" label-width="80px">
        <el-form-item label="团队名称" required>
          <el-input v-model="teamForm.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="teamForm.description" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="智能体">
          <el-select v-model="teamForm.agent_ids" multiple placeholder="选择智能体" style="width: 100%">
            <el-option
              v-for="agent in agentsStore.agents"
              :key="agent.id"
              :label="`${agent.name} (${agent.role})`"
              :value="agent.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingTeam ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog with Topology -->
    <el-dialog v-model="showDetailDialog" :title="detailTeam?.name" width="900px">
      <div v-if="detailTeam">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="团队名称">{{ detailTeam.name }}</el-descriptions-item>
          <el-descriptions-item label="智能体数量">{{ detailTeam.agents.length }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ detailTeam.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin: 20px 0 10px">协作拓扑</h4>
        <TopologyGraph
          :agents="detailTeam.agent_details.map(a => ({
            id: a.id,
            name: a.name,
            role: a.role,
            status: a.status
          }))"
          :collaborations="detailTeam.collaborations"
        />

        <h4 style="margin: 20px 0 10px">智能体列表</h4>
        <el-table :data="detailTeam.agent_details" stripe size="small">
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="role" label="角色" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button type="success" @click="handleDeploy(detailTeam?.id || '')">
          部署团队
        </el-button>
        <el-button type="warning" @click="handleTeardown(detailTeam?.id || '')">
          清理团队
        </el-button>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTeamsStore } from '../stores/teams'
import { useAgentsStore } from '../stores/agents'
import { teamsApi } from '../api/teams'
import type { Team, TeamDetail } from '../types'
import TopologyGraph from '../components/TopologyGraph.vue'

const teamsStore = useTeamsStore()
const agentsStore = useAgentsStore()

const showFormDialog = ref(false)
const showDetailDialog = ref(false)
const submitting = ref(false)
const editingTeam = ref<Team | null>(null)
const detailTeam = ref<TeamDetail | null>(null)

const teamForm = reactive({
  name: '',
  description: '',
  agent_ids: [] as string[],
})

function getAgentName(id: string) {
  const agent = agentsStore.agents.find((a) => a.id === id)
  return agent?.name || id.slice(0, 8)
}

function getStatusType(status: string) {
  const types: Record<string, string> = {
    running: 'success',
    stopped: 'info',
    error: 'danger',
    starting: 'warning',
  }
  return types[status] || 'info'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    running: '运行中',
    stopped: '已停止',
    error: '错误',
    starting: '启动中',
  }
  return labels[status] || status
}

function openCreateDialog() {
  editingTeam.value = null
  Object.assign(teamForm, { name: '', description: '', agent_ids: [] })
  showFormDialog.value = true
}

function openEditDialog(team: Team) {
  editingTeam.value = team
  Object.assign(teamForm, {
    name: team.name,
    description: team.description || '',
    agent_ids: [...team.agents],
  })
  showFormDialog.value = true
}

async function openDetailDialog(team: Team) {
  try {
    detailTeam.value = await teamsApi.get(team.id)
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('获取团队详情失败')
  }
}

async function handleSubmit() {
  if (!teamForm.name) {
    ElMessage.warning('请填写团队名称')
    return
  }

  submitting.value = true
  try {
    if (editingTeam.value) {
      await teamsApi.update(editingTeam.value.id, {
        name: teamForm.name,
        description: teamForm.description,
        agent_ids: teamForm.agent_ids,
      })
      ElMessage.success('更新成功')
    } else {
      await teamsApi.create({
        name: teamForm.name,
        description: teamForm.description,
        agent_ids: teamForm.agent_ids,
      })
      ElMessage.success('创建成功')
    }
    showFormDialog.value = false
    teamsStore.fetchTeams()
  } catch (e) {
    ElMessage.error(editingTeam.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeploy(id: string) {
  try {
    await teamsApi.deploy(id)
    ElMessage.success('团队部署成功')
  } catch (e) {
    ElMessage.error('部署失败')
  }
}

async function handleTeardown(id: string) {
  try {
    await teamsApi.teardown(id)
    ElMessage.success('团队清理成功')
  } catch (e) {
    ElMessage.error('清理失败')
  }
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个团队吗？', '提示', {
      type: 'warning',
    })
    await teamsStore.deleteTeam(id)
    ElMessage.success('删除成功')
  } catch {
    // User cancelled
  }
}

onMounted(() => {
  teamsStore.fetchTeams()
  agentsStore.fetchAgents()
})
</script>

<style scoped>
.team-card {
  margin-bottom: 20px;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-name {
  font-weight: 600;
  font-size: 16px;
}

.team-desc {
  color: #909399;
  font-size: 14px;
  margin-bottom: 12px;
}

.team-agents {
  margin-bottom: 12px;
}

.agent-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.team-actions {
  display: flex;
  gap: 8px;
}
</style>
