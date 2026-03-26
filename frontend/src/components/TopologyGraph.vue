<template>
  <div class="topology-container">
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :default-viewport="{ zoom: 1 }"
      :min-zoom="0.5"
      :max-zoom="2"
      fit-view-on-init
      class="topology-flow"
    >
      <Background pattern-color="#aaa" :gap="20" />
      <Controls />

      <!-- Custom node template -->
      <template #node-agent="nodeProps">
        <div class="agent-node" :class="{ active: nodeProps.data.active }">
          <div class="agent-emoji">{{ nodeProps.data.emoji || '🤖' }}</div>
          <div class="agent-info">
            <div class="agent-name">{{ nodeProps.data.name }}</div>
            <div class="agent-role">{{ nodeProps.data.role }}</div>
          </div>
          <div class="agent-status" :class="nodeProps.data.status"></div>
        </div>
      </template>
    </VueFlow>

    <div v-if="agents.length === 0" class="empty-state">
      <el-empty description="暂无智能体，请先添加智能体到团队" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { VueFlow, useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/background/dist/style.css'

interface AgentData {
  id: string
  name: string
  role: string
  status?: string
  emoji?: string
  active?: boolean
}

interface Collaboration {
  source_id: string
  target_id: string
  trigger: string
}

const props = defineProps<{
  agents: AgentData[]
  collaborations?: Collaboration[]
}>()

const { fitView } = useVueFlow()

// Generate nodes from agents
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])

// Role emoji mapping
const roleEmojis: Record<string, string> = {
  steward: '🧑‍💼',
  dev: '👨‍💻',
  content: '✍️',
  ops: '📊',
  law: '⚖️',
  finance: '💰',
}

// Position nodes in a circle layout
function generateLayout() {
  const centerX = 300
  const centerY = 250
  const radius = Math.min(200, 50 + props.agents.length * 30)

  nodes.value = props.agents.map((agent, index) => {
    const angle = (2 * Math.PI * index) / props.agents.length - Math.PI / 2
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)

    return {
      id: agent.id,
      type: 'agent',
      position: { x, y },
      data: {
        ...agent,
        emoji: roleEmojis[agent.role] || agent.emoji || '🤖',
      },
    }
  })

  // Generate edges from collaborations
  if (props.collaborations && props.collaborations.length > 0) {
    edges.value = props.collaborations.map((collab, index) => ({
      id: `edge-${index}`,
      source: collab.source_id,
      target: collab.target_id,
      label: collab.trigger,
      animated: true,
      style: { stroke: '#409eff' },
      labelStyle: { fill: '#409eff', fontWeight: 700 },
    }))
  } else {
    // If no collaborations defined, connect all agents in a ring
    edges.value = props.agents.map((agent, index) => {
      const nextIndex = (index + 1) % props.agents.length
      return {
        id: `edge-${index}`,
        source: agent.id,
        target: props.agents[nextIndex].id,
        animated: false,
        style: { stroke: '#dcdfe6', strokeDasharray: '5 5' },
      }
    })
  }

  // Fit view after nodes are generated
  setTimeout(() => fitView(), 100)
}

// Watch for changes in agents
watch(() => props.agents, generateLayout, { immediate: true, deep: true })

onMounted(() => {
  generateLayout()
})
</script>

<style scoped>
.topology-container {
  width: 100%;
  height: 500px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #fafafa;
}

.topology-flow {
  width: 100%;
  height: 100%;
}

.agent-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  transition: all 0.3s;
}

.agent-node:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.agent-node.active {
  border-color: #67c23a;
  background: #f0f9eb;
}

.agent-emoji {
  font-size: 24px;
}

.agent-info {
  flex: 1;
}

.agent-name {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.agent-role {
  font-size: 12px;
  color: #909399;
}

.agent-status {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #909399;
}

.agent-status.running {
  background: #67c23a;
  animation: pulse 2s infinite;
}

.agent-status.stopped {
  background: #909399;
}

.agent-status.error {
  background: #f56c6c;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
