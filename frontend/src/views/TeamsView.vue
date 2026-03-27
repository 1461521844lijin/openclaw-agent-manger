<template>
  <div class="teams-view">
    <div class="page-header">
      <h1 class="page-title">团队管理</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建团队
      </el-button>
    </div>

    <div class="teams-grid">
      <div
        v-for="team in teamsStore.teams"
        :key="team.id"
        class="team-card fade-in"
      >
        <div class="card-gradient-bar"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="team-icon">
              <el-icon :size="24"><Collection /></el-icon>
            </div>
            <div class="team-info">
              <h3 class="team-name">{{ team.name }}</h3>
              <span class="team-count">{{ team.agents.length }} 个智能体</span>
            </div>
          </div>

          <p class="team-desc">{{ team.description || '暂无描述' }}</p>

          <div class="team-agents">
            <div
              v-for="agentId in team.agents.slice(0, 4)"
              :key="agentId"
              class="agent-chip"
            >
              {{ getAgentName(agentId) }}
            </div>
            <div v-if="team.agents.length > 4" class="agent-chip more">
              +{{ team.agents.length - 4 }}
            </div>
          </div>

          <div class="card-footer">
            <el-button type="primary" size="small" @click="openDetailDialog(team)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button size="small" @click="openEditDialog(team)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" size="small" @click="handleDeploy(team.id)">
              <el-icon><Promotion /></el-icon>
              部署
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(team.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!teamsStore.loading && teamsStore.teams.length === 0" class="empty-state">
        <el-empty description="暂无团队，点击上方按钮创建" />
      </div>
    </div>

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
        <el-divider content-position="left">协作规则</el-divider>
        <el-form-item label="">
          <div class="collaboration-rules">
            <div
              v-for="(rule, index) in teamForm.collaborations"
              :key="index"
              class="rule-item"
            >
              <el-select v-model="rule.source_id" placeholder="源智能体" size="small" style="width: 120px">
                <el-option
                  v-for="agent in selectedAgents"
                  :key="agent.id"
                  :label="agent.name"
                  :value="agent.id"
                />
              </el-select>
              <el-select v-model="rule.target_id" placeholder="目标智能体" size="small" style="width: 120px">
                <el-option
                  v-for="agent in selectedAgents"
                  :key="agent.id"
                  :label="agent.name"
                  :value="agent.id"
                />
              </el-select>
              <el-input v-model="rule.trigger" placeholder="触发条件" size="small" style="width: 150px" />
              <el-button type="danger" size="small" @click="removeRule(index)">
                删除
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addRule" :disabled="teamForm.agent_ids.length < 2">
              添加规则
            </el-button>
            <span v-if="teamForm.agent_ids.length < 2" class="rule-hint">
              （至少选择2个智能体才能添加协作规则）
            </span>
          </div>
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
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTeamsStore } from '../stores/teams'
import { useAgentsStore } from '../stores/agents'
import { teamsApi } from '../api/teams'
import type { Team, TeamDetail, CollaborationRule } from '../types'
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
  collaborations: [] as CollaborationRule[],
})

const selectedAgents = computed(() => {
  return agentsStore.agents.filter((a) => teamForm.agent_ids.includes(a.id))
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
  Object.assign(teamForm, { name: '', description: '', agent_ids: [], collaborations: [] })
  showFormDialog.value = true
}

function openEditDialog(team: Team) {
  editingTeam.value = team
  Object.assign(teamForm, {
    name: team.name,
    description: team.description || '',
    agent_ids: [...team.agents],
    collaborations: team.collaborations ? JSON.parse(JSON.stringify(team.collaborations)) : [],
  })
  showFormDialog.value = true
}

function addRule() {
  teamForm.collaborations.push({
    source_id: '',
    target_id: '',
    trigger: '',
  })
}

function removeRule(index: number) {
  teamForm.collaborations.splice(index, 1)
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
    const collaborations = teamForm.collaborations.filter(
      (r) => r.source_id && r.target_id && r.trigger
    )
    if (editingTeam.value) {
      await teamsApi.update(editingTeam.value.id, {
        name: teamForm.name,
        description: teamForm.description,
        agent_ids: teamForm.agent_ids,
        collaborations,
      })
      ElMessage.success('更新成功')
    } else {
      await teamsApi.create({
        name: teamForm.name,
        description: teamForm.description,
        agent_ids: teamForm.agent_ids,
        collaborations,
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
.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.team-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--surface-shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.team-card:hover {
  box-shadow: var(--surface-shadow-hover);
  transform: translateY(-4px);
}

.card-gradient-bar {
  height: 4px;
  background: linear-gradient(135deg, #67c23a 0%, #409eff 100%);
}

.card-content {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.team-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(64, 158, 255, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.team-info {
  flex: 1;
  min-width: 0;
}

.team-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.team-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.team-desc {
  color: var(--text-regular);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
  min-height: 44px;
}

.team-agents {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.agent-chip {
  padding: 4px 12px;
  background: var(--primary-gradient-soft);
  border-radius: 20px;
  font-size: 12px;
  color: var(--primary-color);
  border: 1px solid rgba(64, 158, 255, 0.2);
}

.agent-chip.more {
  background: rgba(144, 147, 153, 0.1);
  color: var(--text-secondary);
  border-color: rgba(144, 147, 153, 0.2);
}

.card-footer {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.card-footer .el-button {
  border-radius: 8px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px 20px;
  text-align: center;
}

.collaboration-rules {
  width: 100%;
}

.rule-item {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.rule-hint {
  color: var(--text-secondary);
  font-size: 12px;
  margin-left: 8px;
}

/* Animations */
.team-card {
  animation: fadeIn 0.3s ease-out;
}

.team-card:nth-child(1) { animation-delay: 0.05s; }
.team-card:nth-child(2) { animation-delay: 0.1s; }
.team-card:nth-child(3) { animation-delay: 0.15s; }
.team-card:nth-child(4) { animation-delay: 0.2s; }
.team-card:nth-child(5) { animation-delay: 0.25s; }
.team-card:nth-child(6) { animation-delay: 0.3s; }
</style>
