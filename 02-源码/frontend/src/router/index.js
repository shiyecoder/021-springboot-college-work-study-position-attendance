import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'todo', component: () => import('@/views/Todo.vue'), meta: { title: '我的待办' } },
      { path: 'post-square', component: () => import('@/views/PostSquare.vue'), meta: { title: '岗位广场' } },
      { path: 'post/:id', component: () => import('@/views/PostDetail.vue'), meta: { title: '岗位详情' } },
      { path: 'my-apply', component: () => import('@/views/MyApply.vue'), meta: { title: '我的申请' } },
      { path: 'post-mgr', component: () => import('@/views/PostList.vue'), meta: { title: '岗位管理' } },
      { path: 'post-audit', component: () => import('@/views/PostAudit.vue'), meta: { title: '岗位审批' } },
      { path: 'employment', component: () => import('@/views/Employment.vue'), meta: { title: '录用审核台' } },
      { path: 'shift', component: () => import('@/views/ShiftManage.vue'), meta: { title: '排班管理' } },
      { path: 'my-shift', component: () => import('@/views/MyShift.vue'), meta: { title: '我的排班' } },
      { path: 'attendance', component: () => import('@/views/AttendanceReview.vue'), meta: { title: '考勤复核' } },
      { path: 'check', component: () => import('@/views/CheckIn.vue'), meta: { title: '签到签退' } },
      { path: 'hours', component: () => import('@/views/HourReview.vue'), meta: { title: '工时复核' } },
      { path: 'my-hours', component: () => import('@/views/MyHours.vue'), meta: { title: '我的工时' } },
      { path: 'subsidy', component: () => import('@/views/Subsidy.vue'), meta: { title: '补贴核算' } },
      { path: 'pay', component: () => import('@/views/PayList.vue'), meta: { title: '发放登记' } },
      { path: 'evaluate', component: () => import('@/views/Evaluate.vue'), meta: { title: '学期评价' } },
      { path: 'standard', component: () => import('@/views/Standard.vue'), meta: { title: '学期与标准' } },
      { path: 'rule', component: () => import('@/views/RuleConfig.vue'), meta: { title: '匹配规则' } },
      { path: 'score', component: () => import('@/views/ScoreList.vue'), meta: { title: '计算留痕' } },
      { path: 'report', component: () => import('@/views/Report.vue'), meta: { title: '用工分析' } },
      { path: 'user', component: () => import('@/views/UserList.vue'), meta: { title: '用户管理' } },
      { path: 'role', component: () => import('@/views/RoleList.vue'), meta: { title: '角色管理' } },
      { path: 'menu', component: () => import('@/views/MenuList.vue'), meta: { title: '菜单管理' } },
      { path: 'profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta && to.meta.public) return true
  const token = localStorage.getItem('ws_token')
  if (!token) return '/login'
  return true
})

export default router
