<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-header class="app-header">
          <div class="logo">
            <div class="logo-icon">
              <el-icon :size="22"><Monitor /></el-icon>
            </div>
            <span class="logo-text">OpenClaw Agent Manager</span>
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
            <el-menu-item index="/gateway">
              <el-icon><Connection /></el-icon>
              <span>Gateway</span>
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
  background-color: var(--bg-color);
  background-image: var(--bg-pattern);
}

.app-header {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 0 32px;
  height: 64px;
  border-bottom: 1px solid rgba(64, 158, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: 10px;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  flex: 1;
  border-bottom: none;
  justify-content: flex-end;
  background: transparent;
  height: 100%;
}

.nav-menu :deep(.el-menu-item) {
  height: 64px;
  line-height: 64px;
  margin: 0 4px;
  border-radius: 8px;
  transition: all var(--transition-fast);
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(64, 158, 255, 0.08);
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: var(--primary-gradient-soft);
  border-bottom: 2px solid var(--primary-color);
}

.nav-menu :deep(.el-menu-item.is-active::after) {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 3px;
}

.app-main {
  padding: 24px 32px;
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}
</style>
