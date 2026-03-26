import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/agents',
    },
    {
      path: '/agents',
      name: 'agents',
      component: () => import('../views/AgentsView.vue'),
      meta: { title: '智能体管理' },
    },
    {
      path: '/teams',
      name: 'teams',
      component: () => import('../views/TeamsView.vue'),
      meta: { title: '团队管理' },
    },
    {
      path: '/roles',
      name: 'roles',
      component: () => import('../views/RolesView.vue'),
      meta: { title: '角色库' },
    },
  ],
})

export default router
