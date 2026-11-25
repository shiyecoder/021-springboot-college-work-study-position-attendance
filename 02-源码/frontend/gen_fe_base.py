# -*- coding: utf-8 -*-
"""NEW-021 前端基础文件：全局样式、请求封装、全局状态、路由、主框架、登录页。"""
import pathlib

FE = pathlib.Path(__file__).parent
F = {}


def add(rel, code):
    F[rel] = code.strip() + "\n"


add("index.html", """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>高校勤工助学岗位与考勤管理系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>""")

add("src/styles/global.css", """:root {
  --primary: #173B57;
  --secondary: #287271;
  --accent: #2F6B8A;
  --bg: #F4F7F9;
  --success: #287D4F;
  --danger: #B42318;
  --warning: #8A5A00;
  --border: #DFE7EC;
  --text: #1B2A35;
  --text2: #5A6B77;
  --text3: #8A99A5;
  --el-color-primary: #173B57;
  --el-color-success: #287D4F;
  --el-color-danger: #B42318;
  --el-color-warning: #8A5A00;
  --el-border-radius-base: 6px;
}
* { box-sizing: border-box; }
html, body, #app { height: 100%; margin: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  background: var(--bg); color: var(--text); font-size: 14px; line-height: 22px;
}
.num { font-variant-numeric: tabular-nums; }
.card { background: #fff; border: 1px solid var(--border); border-radius: 7px; margin-bottom: 16px; }
.card-h { height: 52px; display: flex; align-items: center; padding: 0 18px; gap: 12px; border-bottom: 1px solid var(--border); }
.card-h h2 { font-size: 14px; font-weight: 600; margin: 0; }
.card-b { padding: 16px 18px; }
.page-title { font-size: 18px; font-weight: 600; line-height: 26px; margin: 0 0 14px; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 12px 14px; align-items: center; }
.filter-bar .el-select, .filter-bar .el-input { width: 200px; }
.filter-bar .el-date-editor { width: 200px; }
.tbl-cell-sub { display: block; font-size: 12px; color: var(--text3); }
.el-table th.el-table__cell { background: #F8FAFB; color: var(--text2); font-weight: 500; }
.el-table .cell { line-height: 22px; }
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 12px; }
.kpi { background: #fff; border: 1px solid var(--border); border-radius: 7px; padding: 12px 16px; }
.kpi .k { font-size: 12px; color: var(--text2); }
.kpi .v { font-size: 22px; font-weight: 600; line-height: 30px; margin-top: 2px; color: var(--primary); }
.kpi .d { font-size: 11px; color: var(--text3); }
.up { color: var(--danger); }
.down { color: var(--success); }
.chart-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 12px; }
.chart-box { background: #fff; border: 1px solid var(--border); border-radius: 7px; padding: 10px 14px 4px; }
.chart-box h3 { font-size: 13px; margin: 0 0 4px; font-weight: 600; }
.chart { height: 168px; width: 100%; }
.thumb { width: 64px; height: 48px; border-radius: 4px; object-fit: cover; border: 1px solid var(--border); }
.muted { color: var(--text3); font-size: 12px; }
.hint { background: #EAF2F6; border-left: 3px solid var(--accent); padding: 9px 13px; border-radius: 4px; font-size: 12px; color: #254E66; line-height: 20px; }
.score-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 13px; }
.score-row .nm { width: 96px; color: var(--text2); }
.score-row .bar2 { flex: 1; height: 8px; background: #EDF2F5; border-radius: 4px; overflow: hidden; }
.score-row .bar2 i { display: block; height: 100%; background: var(--secondary); }
.timeline { padding-left: 4px; }
.tl { display: flex; gap: 12px; padding-bottom: 14px; position: relative; }
.tl:before { content: ''; position: absolute; left: 5px; top: 15px; bottom: 0; width: 1px; background: var(--border); }
.tl:last-child:before { display: none; }
.tl .dot { width: 11px; height: 11px; border-radius: 50%; background: #fff; border: 2px solid var(--secondary); margin-top: 4px; flex: none; }
.tl .txt b { font-size: 13px; display: block; }
.tl .txt span { font-size: 12px; color: var(--text3); }
""")

add("src/utils/format.js", """/**
 * 全局时间格式化：全系统统一调用，禁止各页面自行拼接
 * @param {string|Date} v 时间值
 * @param {boolean} dateOnly 是否只显示日期
 */
export function formatTime(v, dateOnly = false) {
  if (!v) return '-'
  const s = String(v).replace('T', ' ')
  const m = s.match(/^(\\d{4})-(\\d{2})-(\\d{2})[ ]?(\\d{2}):(\\d{2}):(\\d{2})/)
  if (m) {
    return dateOnly ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}`
  }
  return s
}

export function formatDate(v) {
  return formatTime(v, true)
}

/** 金额：两位小数 + 千分位 */
export function money(v) {
  if (v === null || v === undefined || v === '') return '-'
  return '¥ ' + Number(v).toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',')
}

/** 状态字典 → 中文标签 */
export const STATUS_TEXT = {
  // 岗位
  DRAFT: '草稿', PENDING: '待审核', RECRUITING: '招聘中', FULL: '已满额', FINISHED: '已结束', REJECTED: '已驳回',
  // 申请
  SCREENING: '待筛选', INTERVIEW: '待面试', EMPLOYED: '已录用', WITHDRAWN: '已撤回',
  // 考勤
  NORMAL: '正常', LATE: '迟到', EARLY: '早退', ABSENT: '缺勤', LEAVE: '请假', MAKEUP: '补卡', ING: '进行中',
  // 复核
  PASS: '已通过', REJECT: '已驳回', WAIT: '待发放',
  // 工时
  CONFIRMED: '已确认', OVER_LIMIT: '超上限',
  // 补贴
  AUDITING: '待审核', APPROVED: '已审核', PAID: '已发放', FAIL: '发放失败',
  // 排班
  ADJUST: '待调整',
  // 通用
  RUNNING: '进行中', ACCOUNT: '正常', ON: '启用', OFF: '停用', ACTIVE: '生效中', ARCHIVED: '已归档',
  // 评价
  WAIT_STUDENT: '待学生确认', DONE: '已完成',
  // 困难等级
  DIFFICULT_SPECIAL: '特别困难', DIFFICULT: '困难', NONE: '不困难'
}

export function statusText(s) {
  return STATUS_TEXT[s] || s || '-'
}

export function statusType(s) {
  if (['RECRUITING', 'NORMAL', 'PASS', 'CONFIRMED', 'PAID', 'DONE', 'ON', 'ACTIVE', 'EMPLOYED'].includes(s)) return 'success'
  if (['INTERVIEW', 'ING', 'APPROVED', 'RUNNING', 'SCREENING'].includes(s)) return 'primary'
  if (['PENDING', 'AUDITING', 'WAIT', 'WAIT_STUDENT', 'ADJUST', 'OVER_LIMIT', 'MAKEUP', 'LATE'].includes(s)) return 'warning'
  if (['REJECTED', 'ABSENT', 'FAIL', 'EARLY', 'REJECT'].includes(s)) return 'danger'
  return 'info'
}

export const DIFFICULTY_TEXT = {
  DIFFICULT_SPECIAL: '特别困难', DIFFICULT: '困难', NORMAL: '一般', NONE: '不困难'
}
""")

add("src/utils/request.js", """import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({ baseURL: '', timeout: 30000 })

service.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('ws_token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

service.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && typeof body.code !== 'undefined') {
      if (body.code === 0) return body.data
      if (body.code === 401) {
        localStorage.removeItem('ws_token')
        router.push('/login')
        ElMessage.error(body.msg || '登录已过期，请重新登录')
        return Promise.reject(new Error(body.msg))
      }
      ElMessage.error(body.msg || '请求失败')
      return Promise.reject(new Error(body.msg || '请求失败'))
    }
    return body
  },
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('ws_token')
      router.push('/login')
    }
    ElMessage.error(err.message || '网络异常')
    return Promise.reject(err)
  }
)

export default service
""")

add("src/store/user.js", """import { reactive } from 'vue'

/** 轻量全局状态：登录人、角色、动态菜单 */
export const store = reactive({
  user: JSON.parse(localStorage.getItem('ws_user') || 'null'),
  menus: JSON.parse(localStorage.getItem('ws_menus') || '[]'),
  setLogin(user, menus) {
    this.user = user
    this.menus = menus || []
    localStorage.setItem('ws_user', JSON.stringify(user || null))
    localStorage.setItem('ws_menus', JSON.stringify(menus || []))
  },
  setUser(user) {
    this.user = user
    localStorage.setItem('ws_user', JSON.stringify(user || null))
  },
  logout() {
    this.user = null
    this.menus = []
    localStorage.removeItem('ws_token')
    localStorage.removeItem('ws_user')
    localStorage.removeItem('ws_menus')
  }
})
""")

add("src/router/index.js", """import { createRouter, createWebHistory } from 'vue-router'

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
""")

print("fe base", len(F))
