<template>
  <div class="agents-view">
    <div class="page-header">
      <h1 class="page-title">智能体管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建智能体
      </el-button>
    </div>

    <div class="agents-grid" v-loading="agentsStore.loading">
      <div
        v-for="agent in agentsStore.agents"
        :key="agent.id"
        class="agent-card fade-in"
      >
        <div class="card-gradient-bar"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="agent-avatar">
              <span class="avatar-text">{{ agent.name.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="agent-info">
              <h3 class="agent-name">{{ agent.name }}</h3>
              <span class="agent-role">{{ agent.role }}</span>
            </div>
            <span :class="['status-tag', agent.status]">
              {{ getStatusLabel(agent.status) }}
            </span>
          </div>

          <p class="agent-desc">{{ agent.description || '暂无描述' }}</p>

          <div class="card-footer">
            <div class="action-buttons">
              <el-button
                v-if="agent.status !== 'running'"
                type="success"
                size="small"
                @click="handleStart(agent.id)"
              >
                <el-icon><VideoPlay /></el-icon>
                启动
              </el-button>
              <el-button
                v-else
                type="warning"
                size="small"
                @click="handleStop(agent.id)"
              >
                <el-icon><VideoPause /></el-icon>
                停止
              </el-button>
              <el-button
                type="info"
                size="small"
                :disabled="agent.status !== 'running'"
                @click="openMessageDialog(agent)"
              >
                <el-icon><ChatDotRound /></el-icon>
              </el-button>
              <el-button type="primary" size="small" @click="openBindDialog(agent)">
                <el-icon><Link /></el-icon>
              </el-button>
              <el-button size="small" @click="handleEdit(agent)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(agent.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!agentsStore.loading && agentsStore.agents.length === 0" class="empty-state">
        <el-empty description="暂无智能体，点击上方按钮创建" />
      </div>
    </div>

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
        <el-divider content-position="left">飞书机器人配置</el-divider>
        <el-form-item label="App ID">
          <el-input v-model="agentForm.feishu_app_id" placeholder="飞书应用 App ID" />
        </el-form-item>
        <el-form-item label="App Secret">
          <el-input
            v-model="agentForm.feishu_app_secret"
            type="password"
            :placeholder="editingAgent?.feishu_secret_configured ? '已配置，留空则不修改' : '飞书应用 App Secret'"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Message Dialog -->
    <el-dialog v-model="showMessageDialog" title="发送消息" width="500px">
      <el-form label-width="80px">
        <el-form-item label="智能体">
          <el-input :value="messagingAgent?.name" disabled />
        </el-form-item>
        <el-form-item label="消息内容" required>
          <el-input
            v-model="messageContent"
            type="textarea"
            rows="4"
            placeholder="请输入要发送的消息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMessageDialog = false">取消</el-button>
        <el-button type="primary" :loading="sendingMessage" @click="handleSendMessage">
          发送
        </el-button>
      </template>
    </el-dialog>

    <!-- Bind Channel Dialog -->
    <el-dialog v-model="showBindDialog" title="绑定通道" width="500px">
      <el-form label-width="80px">
        <el-form-item label="智能体">
          <el-input :value="bindingAgent?.name" disabled />
        </el-form-item>
        <el-form-item label="通道类型" required>
          <el-select v-model="bindForm.channel" placeholder="请选择通道类型" style="width: 100%">
            <el-option label="飞书 (Feishu)" value="feishu" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="Discord" value="discord" />
            <el-option label="WhatsApp" value="whatsapp" />
          </el-select>
        </el-form-item>
        <el-form-item label="账户 ID">
          <el-input v-model="bindForm.accountId" placeholder="可选，账户标识" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBindDialog = false">取消</el-button>
        <el-button type="primary" :loading="binding" @click="handleBind">绑定</el-button>
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
  feishu_app_id: '',
  feishu_app_secret: '',
})

// Message dialog state
const showMessageDialog = ref(false)
const messagingAgent = ref<Agent | null>(null)
const messageContent = ref('')
const sendingMessage = ref(false)

// Bind dialog state
const showBindDialog = ref(false)
const bindingAgent = ref<Agent | null>(null)
const bindForm = reactive({
  channel: '',
  accountId: '',
})
const binding = ref(false)

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
  agentForm.feishu_app_id = agent.feishu_app_id || ''
  agentForm.feishu_app_secret = ''
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

function openMessageDialog(agent: Agent) {
  messagingAgent.value = agent
  messageContent.value = ''
  showMessageDialog.value = true
}

async function handleSendMessage() {
  if (!messageContent.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }
  if (!messagingAgent.value) return

  sendingMessage.value = true
  try {
    await agentsApi.message(messagingAgent.value.id, messageContent.value)
    ElMessage.success('消息已发送')
    showMessageDialog.value = false
    messageContent.value = ''
  } catch (e) {
    ElMessage.error('发送失败')
  } finally {
    sendingMessage.value = false
  }
}

function openBindDialog(agent: Agent) {
  bindingAgent.value = agent
  bindForm.channel = ''
  bindForm.accountId = ''
  showBindDialog.value = true
}

async function handleBind() {
  if (!bindForm.channel) {
    ElMessage.warning('请选择通道类型')
    return
  }
  if (!bindingAgent.value) return

  binding.value = true
  try {
    await agentsApi.bind(
      bindingAgent.value.id,
      bindForm.channel,
      bindForm.accountId || undefined
    )
    ElMessage.success('绑定成功')
    showBindDialog.value = false
  } catch (e) {
    ElMessage.error('绑定失败')
  } finally {
    binding.value = false
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
    Object.assign(agentForm, {
      name: '',
      role: '',
      workspace: './workspace',
      description: '',
      feishu_app_id: '',
      feishu_app_secret: '',
    })
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

<style scoped>
.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.agent-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--surface-shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all var(--transition-normal);
  position: relative;
}

.agent-card:hover {
  box-shadow: var(--surface-shadow-hover);
  transform: translateY(-4px);
}

.card-gradient-bar {
  height: 4px;
  background: var(--primary-gradient);
}

.card-content {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.agent-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
}

.avatar-text {
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-role {
  font-size: 13px;
  color: var(--text-secondary);
}

.agent-desc {
  color: var(--text-regular);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 44px;
}

.card-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  border-radius: 8px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px 20px;
  text-align: center;
}

/* Animations */
.agent-card {
  animation: fadeIn 0.3s ease-out;
}

.agent-card:nth-child(1) { animation-delay: 0.05s; }
.agent-card:nth-child(2) { animation-delay: 0.1s; }
.agent-card:nth-child(3) { animation-delay: 0.15s; }
.agent-card:nth-child(4) { animation-delay: 0.2s; }
.agent-card:nth-child(5) { animation-delay: 0.25s; }
.agent-card:nth-child(6) { animation-delay: 0.3s; }
</style>
