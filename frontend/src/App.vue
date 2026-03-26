<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-header class="app-header">
          <div class="logo">
            <el-icon :size="24"><Monitor /></el-icon>
            <span>OpenClaw Agent Manager</span>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="nav-menu"
          >
            <el-menu-item index="/agents">
              <el-icon><User /></el-icon>
              <span>智能体</span>
            </el-menu-item>
            <el-menu-item index="/teams">
              <el-icon><Collection /></el-icon>
              <span>团队</span>
            </el-menu-item>
            <el-menu-item index="/roles">
              <el-icon><Avatar /></el-icon>
              <span>角色库</span>
            </el-menu-item>
          </el-menu>
        </el-header>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  display: flex;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.nav-menu {
  flex: 1;
  border-bottom: none;
  justify-content: flex-end;
}

.app-main {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>
