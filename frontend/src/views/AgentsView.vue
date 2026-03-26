<template>
  <div class="agents-view">
    <div class="page-header">
      <h1 class="page-title">智能体管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建智能体
      </el-button>
    </div>

    <el-table :data="agentsStore.agents" v-loading="agentsStore.loading" stripe>
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status !== 'running'"
            type="success"
            size="small"
            @click="handleStart(row.id)"
          >
            启动
          </el-button>
          <el-button
            v-else
            type="warning"
            size="small"
            @click="handleStop(row.id)"
          >
            停止
          </el-button>
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingAgent ? '编辑智能体' : '创建智能体'"
      width="500px"
    >
      <el-form :model="agentForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="agentForm.name" placeholder="请输入智能体名称" />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="agentForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="role in rolesStore.roles"
              :key="role.id"
              :label="`${role.emoji || ''} ${role.name}`"
              :value="role.name_en"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工作目录">
          <el-input v-model="agentForm.workspace" placeholder="./workspace" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="agentForm.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAgentsStore } from '../stores/agents'
import { useRolesStore } from '../stores/roles'
import { agentsApi } from '../api/agents'
import type { Agent, AgentStatus } from '../types'

const agentsStore = useAgentsStore()
const rolesStore = useRolesStore()

const showCreateDialog = ref(false)
const editingAgent = ref<Agent | null>(null)
const agentForm = reactive({
  name: '',
  role: '',
  workspace: './workspace',
  description: '',
})

function getStatusType(status: AgentStatus) {
  const types: Record<AgentStatus, string> = {
    running: 'success',
    stopped: 'info',
    error: 'danger',
    starting: 'warning',
  }
  return types[status] || 'info'
}

function getStatusLabel(status: AgentStatus) {
  const labels: Record<AgentStatus, string> = {
    running: '运行中',
    stopped: '已停止',
    error: '错误',
    starting: '启动中',
  }
  return labels[status] || status
}

async function handleStart(id: string) {
  try {
    await agentsStore.startAgent(id)
    ElMessage.success('智能体已启动')
  } catch (e) {
    ElMessage.error('启动失败')
  }
}

async function handleStop(id: string) {
  try {
    await agentsStore.stopAgent(id)
    ElMessage.success('智能体已停止')
  } catch (e) {
    ElMessage.error('停止失败')
  }
}

function handleEdit(agent: Agent) {
  editingAgent.value = agent
  agentForm.name = agent.name
  agentForm.role = agent.role
  agentForm.workspace = agent.workspace
  agentForm.description = agent.description || ''
  showCreateDialog.value = true
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个智能体吗？', '提示', {
      type: 'warning',
    })
    await agentsStore.deleteAgent(id)
    ElMessage.success('删除成功')
  } catch {
    // User cancelled
  }
}

async function handleSubmit() {
  if (!agentForm.name || !agentForm.role) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    if (editingAgent.value) {
      await agentsApi.update(editingAgent.value.id, agentForm)
      ElMessage.success('更新成功')
    } else {
      await agentsApi.create(agentForm)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingAgent.value = null
    Object.assign(agentForm, { name: '', role: '', workspace: './workspace', description: '' })
    agentsStore.fetchAgents()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  agentsStore.fetchAgents()
  rolesStore.fetchRoles()
})
</script>
