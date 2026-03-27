<template>
  <div class="gateway-view">
    <div class="page-header">
      <h1 class="page-title">Gateway 管理</h1>
    </div>

    <!-- Status Card -->
    <div class="status-card fade-in">
      <div class="card-gradient-bar" :class="{ running: status?.running }"></div>
      <div class="card-content">
        <div class="card-header">
          <div class="header-left">
            <div class="status-icon" :class="{ active: status?.running }">
              <el-icon :size="28"><Connection /></el-icon>
            </div>
            <div class="header-info">
              <h3>服务状态</h3>
              <span class="status-text">
                <span class="status-dot" :class="{ active: status?.running }"></span>
                {{ status?.running ? '运行中' : '已停止' }}
              </span>
            </div>
          </div>
          <el-button type="primary" size="small" @click="refreshStatus">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div v-loading="loading" class="status-details">
          <div class="detail-item" v-if="status?.port">
            <span class="detail-label">端口</span>
            <span class="detail-value port">{{ status.port }}</span>
          </div>

          <div class="detail-item" v-if="status?.url">
            <span class="detail-label">WebSocket URL</span>
            <code class="detail-value code">{{ status.url }}</code>
          </div>

          <div class="detail-item error" v-if="status?.error">
            <span class="detail-label">错误信息</span>
            <el-alert :title="status.error" type="error" :closable="false" show-icon />
          </div>
        </div>

        <div class="action-buttons">
          <el-button
            type="success"
            size="large"
            @click="handleStart"
            :disabled="status?.running"
            :loading="starting"
          >
            <el-icon><VideoPlay /></el-icon>
            启动 Gateway
          </el-button>
          <el-button
            type="danger"
            size="large"
            @click="handleStop"
            :disabled="!status?.running"
            :loading="stopping"
          >
            <el-icon><VideoPause /></el-icon>
            停止 Gateway
          </el-button>
        </div>
      </div>
    </div>

    <!-- OpenClaw Agents -->
    <div class="agents-card fade-in">
      <div class="card-gradient-bar agents"></div>
      <div class="card-content">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon agents">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <h3>OpenClaw 智能体列表</h3>
          </div>
          <el-button type="primary" size="small" @click="syncAgents">
            <el-icon><Refresh /></el-icon>
            同步到本地
          </el-button>
        </div>

        <el-table :data="openclawAgents" v-loading="agentsLoading" stripe class="agents-table">
          <el-table-column prop="id" label="ID" width="120">
            <template #default="{ row }">
              <code class="agent-id">{{ row.id?.slice(0, 8) }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="identityName" label="名称" width="150">
            <template #default="{ row }">
              <span class="agent-name">
                {{ row.identityEmoji }} {{ row.identityName }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="model" label="模型" min-width="200" show-overflow-tooltip />
          <el-table-column label="默认" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.isDefault" type="success" size="small" class="default-tag">是</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="workspace" label="工作目录" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <code class="workspace-path">{{ row.workspace }}</code>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { gatewayApi, type GatewayStatus } from '../api/gateway'
import { agentsApi } from '../api/agents'

const loading = ref(false)
const starting = ref(false)
const stopping = ref(false)
const agentsLoading = ref(false)

const status = ref<GatewayStatus | null>(null)
const openclawAgents = ref<Record<string, unknown>[]>([])

async function refreshStatus() {
  loading.value = true
  try {
    status.value = await gatewayApi.status()
  } catch (e) {
    ElMessage.error('获取状态失败')
  } finally {
    loading.value = false
  }
}

async function handleStart() {
  starting.value = true
  try {
    const result = await gatewayApi.start()
    if (result.success) {
      ElMessage.success('Gateway 已启动')
      await refreshStatus()
    } else {
      ElMessage.error(result.error || '启动失败')
    }
  } catch (e) {
    ElMessage.error('启动失败')
  } finally {
    starting.value = false
  }
}

async function handleStop() {
  stopping.value = true
  try {
    const result = await gatewayApi.stop()
    if (result.success) {
      ElMessage.success('Gateway 已停止')
      await refreshStatus()
    } else {
      ElMessage.error(result.error || '停止失败')
    }
  } catch (e) {
    ElMessage.error('停止失败')
  } finally {
    stopping.value = false
  }
}

async function fetchOpenclawAgents() {
  agentsLoading.value = true
  try {
    const result = await gatewayApi.agents()
    openclawAgents.value = result.agents
  } catch (e) {
    ElMessage.error('获取智能体列表失败')
  } finally {
    agentsLoading.value = false
  }
}

async function syncAgents() {
  try {
    const result = await agentsApi.sync()
    ElMessage.success(result.message)
  } catch (e) {
    ElMessage.error('同步失败')
  }
}

onMounted(() => {
  refreshStatus()
  fetchOpenclawAgents()
})
</script>

<style scoped>
.status-card,
.agents-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--surface-shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 24px;
}

.card-gradient-bar {
  height: 4px;
  background: linear-gradient(135deg, #909399 0%, #606266 100%);
  transition: background var(--transition-normal);
}

.card-gradient-bar.running {
  background: var(--success-gradient);
}

.card-gradient-bar.agents {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
}

.card-content {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(144, 147, 153, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--transition-normal);
}

.status-icon.active {
  background: rgba(103, 194, 58, 0.1);
  color: var(--success-color);
}

.header-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.status-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.status-dot.active {
  background: var(--success-color);
  animation: pulse 2s ease-in-out infinite;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-icon.agents {
  background: var(--primary-gradient);
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-details {
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item.error {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.detail-label {
  font-weight: 500;
  color: var(--text-secondary);
  min-width: 120px;
  font-size: 14px;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.detail-value.port {
  font-family: monospace;
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
}

.detail-value.code {
  background: rgba(64, 158, 255, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--primary-color);
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.action-buttons .el-button {
  border-radius: 10px;
  padding: 12px 24px;
}

.agents-table {
  margin-top: 16px;
}

.agent-id {
  font-family: monospace;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 8px;
  border-radius: 4px;
}

.agent-name {
  font-weight: 500;
}

.default-tag {
  border-radius: 12px;
}

.workspace-path {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

/* Animations */
.status-card,
.agents-card {
  animation: fadeIn 0.3s ease-out;
}

.agents-card {
  animation-delay: 0.1s;
}
</style>
