<template>
  <div class="roles-view">
    <div class="page-header">
      <h1 class="page-title">角色库</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        创建角色
      </el-button>
    </div>

    <el-collapse v-model="activeCategories" v-loading="rolesStore.loading">
      <el-collapse-item
        v-for="category in rolesStore.categories"
        :key="category.id"
        :name="category.id"
      >
        <template #title>
          <span class="category-title">{{ category.label }}</span>
          <el-tag size="small" class="category-count">{{ category.items.length }}</el-tag>
        </template>

        <el-row :gutter="16">
          <el-col :span="8" v-for="role in category.items" :key="role.id">
            <el-card class="role-card" shadow="hover">
              <div class="role-header">
                <span class="role-emoji">{{ role.emoji || '🤖' }}</span>
                <div class="role-info">
                  <div class="role-name">{{ role.name }}</div>
                  <div class="role-name-en">{{ role.name_en }}</div>
                </div>
                <el-tag v-if="role.is_builtin" size="small" type="info">内置</el-tag>
              </div>
              <p class="role-desc">{{ role.description }}</p>
              <div class="role-mission" v-if="role.core_mission">
                <strong>核心使命：</strong>{{ role.core_mission }}
              </div>
              <div class="role-actions" v-if="!role.is_builtin">
                <el-button type="primary" size="small" @click="handleEdit(role)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(role.id)">
                  删除
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
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
.category-title {
  font-weight: 600;
  font-size: 16px;
}

.category-count {
  margin-left: 8px;
}

.role-card {
  margin-bottom: 16px;
}

.role-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.role-emoji {
  font-size: 32px;
}

.role-info {
  flex: 1;
}

.role-name {
  font-weight: 600;
  font-size: 16px;
}

.role-name-en {
  color: #909399;
  font-size: 12px;
}

.role-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.role-mission {
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
}

.role-actions {
  margin-top: 12px;
  text-align: right;
}
</style>
