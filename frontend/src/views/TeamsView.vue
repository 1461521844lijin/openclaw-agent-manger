<template>
  <div class="teams-view">
    <div class="page-header">
      <h1 class="page-title">团队管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
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
            <el-button type="success" size="small" @click="handleDeploy(team.id)">
              部署
            </el-button>
            <el-button type="warning" size="small" @click="handleTeardown(team.id)">
              清理
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(team.id)">
              删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="创建团队" width="600px">
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
              :label="agent.name"
              :value="agent.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
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

const teamsStore = useTeamsStore()
const agentsStore = useAgentsStore()

const showCreateDialog = ref(false)
const teamForm = reactive({
  name: '',
  description: '',
  agent_ids: [] as string[],
})

function getAgentName(id: string) {
  const agent = agentsStore.agents.find((a) => a.id === id)
  return agent?.name || id.slice(0, 8)
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

async function handleCreate() {
  if (!teamForm.name) {
    ElMessage.warning('请填写团队名称')
    return
  }

  try {
    await teamsApi.create({
      name: teamForm.name,
      description: teamForm.description,
      agent_ids: teamForm.agent_ids,
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    Object.assign(teamForm, { name: '', description: '', agent_ids: [] })
    teamsStore.fetchTeams()
  } catch (e) {
    ElMessage.error('创建失败')
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
