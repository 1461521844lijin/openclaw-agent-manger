<template>
  <div class="roles-view">
    <div class="page-header">
      <h1 class="page-title">角色库</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建角色
      </el-button>
    </div>

    <el-collapse v-model="activeCategories" v-loading="rolesStore.loading" class="category-collapse">
      <el-collapse-item
        v-for="category in rolesStore.categories"
        :key="category.id"
        :name="category.id"
        class="category-item"
      >
        <template #title>
          <div class="category-header">
            <span class="category-title">{{ category.label }}</span>
            <span class="category-count">{{ category.items.length }}</span>
          </div>
        </template>

        <div class="roles-grid">
          <div
            v-for="role in category.items"
            :key="role.id"
            class="role-card fade-in"
          >
            <div class="card-gradient-bar"></div>
            <div class="card-content">
              <div class="role-header">
                <div class="role-emoji">{{ role.emoji || '🤖' }}</div>
                <div class="role-info">
                  <h3 class="role-name">{{ role.name }}</h3>
                  <span class="role-name-en">{{ role.name_en }}</span>
                </div>
                <el-tag v-if="role.is_builtin" size="small" type="info" class="builtin-tag">内置</el-tag>
              </div>

              <p class="role-desc">{{ role.description || '暂无描述' }}</p>

              <div class="role-mission" v-if="role.core_mission">
                <el-icon class="mission-icon"><Aim /></el-icon>
                <span>{{ role.core_mission }}</span>
              </div>

              <div class="role-actions" v-if="!role.is_builtin">
                <el-button type="primary" size="small" @click="handleEdit(role)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(role.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingRole ? '编辑角色' : '创建自定义角色'"
      width="500px"
    >
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="roleForm.name" placeholder="中文名称" />
        </el-form-item>
        <el-form-item label="英文名" required>
          <el-input v-model="roleForm.name_en" placeholder="english_name" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="roleForm.emoji" placeholder="🤖" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="核心使命">
          <el-input v-model="roleForm.core_mission" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="roleForm.category" placeholder="自定义分类" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">
          {{ editingRole ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRolesStore } from '../stores/roles'
import { rolesApi } from '../api/roles'
import type { Role } from '../types'

const rolesStore = useRolesStore()

const activeCategories = ref<string[]>([])
const showCreateDialog = ref(false)
const editingRole = ref<Role | null>(null)
const roleForm = reactive({
  name: '',
  name_en: '',
  emoji: '',
  description: '',
  core_mission: '',
  category: '',
})

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '提示', {
      type: 'warning',
    })
    await rolesApi.delete(id)
    ElMessage.success('删除成功')
    rolesStore.fetchCategories()
  } catch {
    // User cancelled
  }
}

function openCreateDialog() {
  editingRole.value = null
  Object.assign(roleForm, {
    name: '',
    name_en: '',
    emoji: '',
    description: '',
    core_mission: '',
    category: '',
  })
  showCreateDialog.value = true
}

function handleEdit(role: Role) {
  editingRole.value = role
  roleForm.name = role.name
  roleForm.name_en = role.name_en
  roleForm.emoji = role.emoji || ''
  roleForm.description = role.description || ''
  roleForm.core_mission = role.core_mission || ''
  roleForm.category = role.category || ''
  showCreateDialog.value = true
}

async function handleSubmit() {
  if (!roleForm.name || !roleForm.name_en) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    if (editingRole.value) {
      await rolesApi.update(editingRole.value.id, roleForm)
      ElMessage.success('更新成功')
    } else {
      await rolesApi.create(roleForm)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingRole.value = null
    Object.assign(roleForm, {
      name: '',
      name_en: '',
      emoji: '',
      description: '',
      core_mission: '',
      category: '',
    })
    rolesStore.fetchCategories()
  } catch (e) {
    ElMessage.error(editingRole.value ? '更新失败' : '创建失败')
  }
}

onMounted(async () => {
  await rolesStore.fetchCategories()
  // Expand all categories by default
  activeCategories.value = rolesStore.categories.map((c) => c.id)
})
</script>

<style scoped>
.category-collapse {
  border: none;
}

.category-item {
  margin-bottom: 20px;
  border: none;
}

.category-item :deep(.el-collapse-item__header) {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 0 20px;
  height: 56px;
  border: 1px solid var(--border-color);
  box-shadow: var(--surface-shadow);
  transition: all var(--transition-normal);
}

.category-item :deep(.el-collapse-item__header:hover) {
  box-shadow: var(--surface-shadow-hover);
}

.category-item :deep(.el-collapse-item__wrap) {
  border: none;
  background: transparent;
}

.category-item :deep(.el-collapse-item__content) {
  padding-top: 16px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-title {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.category-count {
  background: var(--primary-gradient);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.role-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--surface-shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.role-card:hover {
  box-shadow: var(--surface-shadow-hover);
  transform: translateY(-2px);
}

.card-gradient-bar {
  height: 3px;
  background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%);
}

.card-content {
  padding: 16px;
}

.role-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.role-emoji {
  font-size: 36px;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.1) 0%, rgba(245, 108, 108, 0.1) 100%);
  border-radius: 12px;
}

.role-info {
  flex: 1;
  min-width: 0;
}

.role-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.role-name-en {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: monospace;
}

.builtin-tag {
  border-radius: 12px;
}

.role-desc {
  color: var(--text-regular);
  font-size: 13px;
  margin-bottom: 12px;
  line-height: 1.6;
  min-height: 40px;
}

.role-mission {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: var(--primary-gradient-soft);
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-regular);
  border: 1px solid rgba(64, 158, 255, 0.1);
  margin-bottom: 12px;
}

.mission-icon {
  color: var(--primary-color);
  flex-shrink: 0;
  margin-top: 2px;
}

.role-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.role-actions .el-button {
  border-radius: 8px;
  flex: 1;
}

/* Animations */
.role-card {
  animation: fadeIn 0.3s ease-out;
}

.role-card:nth-child(1) { animation-delay: 0.02s; }
.role-card:nth-child(2) { animation-delay: 0.04s; }
.role-card:nth-child(3) { animation-delay: 0.06s; }
.role-card:nth-child(4) { animation-delay: 0.08s; }
.role-card:nth-child(5) { animation-delay: 0.1s; }
.role-card:nth-child(6) { animation-delay: 0.12s; }
</style>
