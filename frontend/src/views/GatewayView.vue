<template>
  <div class="gateway-view">
    <div class="page-header">
      <h1 class="page-title">Gateway 管理</h1>
    </div>

    <!-- Status Card -->
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span>服务状态</span>
          <el-button type="primary" size="small" @click="refreshStatus">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <div v-loading="loading" class="status-content">
        <div class="status-item">
          <span class="label">运行状态：</span>
          <el-tag :type="status?.running ? 'success' : 'danger'" size="large">
            {{ status?.running ? '运行中' : '已停止' }}
          </el-tag>
        </div>

        <div class="status-item" v-if="status?.port">
          <span class="label">端口：</span>
          <span class="value">{{ status.port }}</span>
        </div>

        <div class="status-item" v-if="status?.url">
          <span class="label">WebSocket URL：</span>
          <el-tag type="info">{{ status.url }}</el-tag>
        </div>

        <div class="status-item" v-if="status?.error">
          <span class="label">错误信息：</span>
          <el-alert :title="status.error" type="error" :closable="false" />
        </div>

        <div class="actions">
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
    </el-card>

    <!-- OpenClaw Agents -->
    <el-card class="agents-card">
      <template #header>
        <div class="card-header">
          <span>OpenClaw 智能体列表</span>
          <el-button type="primary" size="small" @click="syncAgents">
            <el-icon><Refresh /></el-icon>
            同步到本地
          </el-button>
        </div>
      </template>

      <el-table :data="openclawAgents" v-loading="agentsLoading" stripe>
        <el-table-column prop="id" label="ID" width="120" />
        <el-table-column prop="identityName" label="名称" width="150">
          <template #default="{ row }">
            {{ row.identityEmoji }} {{ row.identityName }}
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" min-width="200" show-overflow-tooltip />
        <el-table-column label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.isDefault" type="success" size="small">是</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="workspace" label="工作目录" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>
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
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-content {
  padding: 20px 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-item .label {
  font-weight: 500;
  color: #606266;
  min-width: 120px;
}

.status-item .value {
  font-family: monospace;
  color: #303133;
}

.actions {
  margin-top: 24px;
  display: flex;
  gap: 16px;
}
</style>
