# -*- coding: utf-8 -*-
"""NEW-021 主框架（按角色切换 后台/门户）与登录页。"""
import pathlib

FE = pathlib.Path(__file__).parent
F = {}


def add(rel, code):
    F[rel] = code.strip() + "\n"


add("src/layout/MainLayout.vue", """<template>
  <!-- 学生走门户式布局（顶部导航 + 内容流），教职工走后台布局（侧边栏 + 顶栏） -->
  <div v-if="isStudent" class="portal">
    <header class="p-top">
      <div class="p-brand"><span class="logo">勤</span>勤工助学 · 学生服务</div>
      <nav class="p-nav">
        <a v-for="m in menus" :key="m.id" :class="{ on: route.path === m.path }" @click="go(m.path)">{{ m.name }}</a>
      </nav>
      <div class="p-right">
        <el-badge :value="unread" :hidden="unread === 0">
          <el-icon class="bell" @click="msgVisible = true"><Bell /></el-icon>
        </el-badge>
        <el-dropdown @command="onCommand">
          <span class="who">
            <img class="avatar" :src="avatarUrl" alt="" />
            <b>{{ store.user?.realName }}</b>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    <main class="p-content"><router-view /></main>
  </div>

  <div v-else class="layout">
    <aside class="side" :class="{ fold }">
      <div class="brand"><span class="logo">勤</span><span v-show="!fold">勤工助学管理</span></div>
      <el-menu :default-active="route.path" :collapse="fold" :collapse-transition="false"
               background-color="#173B57" text-color="rgba(255,255,255,.78)"
               active-text-color="#fff" router class="menu">
        <template v-for="g in groups" :key="g.name">
          <div class="grp" v-show="!fold">{{ g.name }}</div>
          <el-menu-item v-for="m in g.items" :key="m.id" :index="m.path">
            <el-icon><component :is="iconOf(m.icon)" /></el-icon>
            <template #title>{{ m.name }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </aside>

    <div class="main">
      <header class="top">
        <el-icon class="fold-btn" @click="fold = !fold"><Fold v-if="!fold" /><Expand v-else /></el-icon>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>{{ roleName }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="right">
          <span class="muted">{{ today }}</span>
          <el-badge :value="unread" :hidden="unread === 0">
            <el-icon class="bell" @click="msgVisible = true"><Bell /></el-icon>
          </el-badge>
          <el-dropdown @command="onCommand">
            <span class="who">
              <img class="avatar" :src="avatarUrl" alt="" />
              <span><b>{{ store.user?.realName }}</b><i>{{ store.user?.roleName }}</i></span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="content"><router-view /></main>
    </div>

    <el-drawer v-model="msgVisible" title="站内消息" size="420px">
      <div v-for="m in messages" :key="m.id" class="msg" @click="readMsg(m)">
        <div class="msg-t"><b>{{ m.title }}</b><span class="muted">{{ formatTime(m.createTime) }}</span></div>
        <div class="msg-c">{{ m.content }}</div>
      </div>
      <el-empty v-if="!messages.length" description="暂无消息" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { store } from '@/store/user'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const fold = ref(false)
const messages = ref([])
const unread = ref(0)
const msgVisible = ref(false)

const isStudent = computed(() => store.user?.roleCode === 'STUDENT')
const roleName = computed(() => store.user?.roleName || '工作台')
const menus = computed(() => store.menus || [])
const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
const avatarUrl = computed(() => store.user?.avatar || '')

/** 侧边栏按业务域分组，分组顺序固定，未列出的菜单落到「其他」 */
const SECTIONS = [
  ['工作台', ['工作台', '我的待办']],
  ['岗位与申请', ['岗位广场', '我的申请', '岗位管理', '岗位审批']],
  ['录用与排班', ['录用审核台', '排班管理', '我的排班']],
  ['考勤与工时', ['考勤复核', '签到签退', '工时复核', '我的工时']],
  ['补贴与评价', ['补贴核算', '发放登记', '学期评价']],
  ['配置与统计', ['学期与标准', '匹配规则', '计算留痕', '用工分析']],
  ['系统', ['用户管理', '角色管理', '菜单管理']]
]
const groups = computed(() => {
  const used = new Set()
  const out = []
  for (const [name, names] of SECTIONS) {
    const items = menus.value.filter((m) => names.includes(m.name))
    items.forEach((m) => used.add(m.id))
    if (items.length) out.push({ name, items })
  }
  const rest = menus.value.filter((m) => !used.has(m.id))
  if (rest.length) out.push({ name: '其他', items: rest })
  return out
})

const ICONS = { dashboard: 'DataBoard', todo: 'Tickets', post: 'Postcard', apply: 'Document',
  audit: 'Stamp', employ: 'UserFilled', shift: 'Calendar', attend: 'Clock', hours: 'Histogram',
  subsidy: 'Money', pay: 'Wallet', evaluate: 'Star', standard: 'SetUp', rule: 'Operation',
  score: 'DataLine', report: 'TrendCharts', user: 'User', role: 'Avatar', menu: 'Menu' }
function iconOf(name) { return ICONS[name] || 'Menu' }

function go(path) {
  if (path) router.push(path)
}

async function loadMessages() {
  try {
    const d = await request.get('/api/message/page', { params: { page: 1, size: 20 } })
    messages.value = d.list || []
    unread.value = messages.value.filter((m) => m.readFlag === 0).length
  } catch (e) { /* 消息失败不影响主流程 */ }
}
async function readMsg(m) {
  if (m.readFlag === 0) {
    await request.post('/api/message/' + m.id + '/read')
    m.readFlag = 1
    unread.value = messages.value.filter((x) => x.readFlag === 0).length
  }
}
function onCommand(c) {
  if (c === 'profile') router.push('/profile')
  else { store.logout(); router.push('/login') }
}
onMounted(loadMessages)
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }
.side { width: 220px; background: #173B57; display: flex; flex-direction: column; transition: width .2s; flex: none; }
.side.fold { width: 64px; }
.brand {
  height: 56px; display: flex; align-items: center; gap: 10px; padding: 0 18px;
  color: #fff; font-weight: 600; font-size: 15px; border-bottom: 1px solid rgba(255,255,255,.1);
}
.logo {
  width: 22px; height: 22px; border-radius: 5px; background: #287271; color: #fff;
  display: inline-flex; align-items: center; justify-content: center; font-size: 12px;
}
.menu { border: none; flex: 1; overflow-y: auto; }
.grp { padding: 13px 18px 5px; font-size: 11px; color: rgba(255,255,255,.45); letter-spacing: 1px; }
.main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.top { height: 56px; background: #fff; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 16px; padding: 0 24px; }
.fold-btn { cursor: pointer; font-size: 18px; color: var(--text2); }
.right { margin-left: auto; display: flex; align-items: center; gap: 18px; }
.bell { font-size: 18px; color: var(--text2); cursor: pointer; }
.who { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 12px; color: var(--text3); }
.who b { display: block; font-size: 13px; color: var(--text); font-weight: 500; }
.who i { font-style: normal; font-size: 11px; }
.avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); background: #E7EEF2; }
.content { flex: 1; overflow-y: auto; padding: 24px; }
.msg { padding: 12px 0; border-bottom: 1px solid var(--border); cursor: pointer; }
.msg-t { display: flex; justify-content: space-between; font-size: 14px; gap: 10px; }
.msg-c { font-size: 13px; color: var(--text2); margin-top: 4px; }

/* 学生门户 */
.portal { min-height: 100vh; background: var(--bg); }
.p-top {
  height: 60px; background: #fff; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 28px; padding: 0 32px; position: sticky; top: 0; z-index: 10;
}
.p-brand { font-size: 15px; font-weight: 600; color: var(--primary); display: flex; align-items: center; gap: 10px; }
.p-nav { display: flex; gap: 4px; }
.p-nav a { padding: 6px 14px; border-radius: 6px; font-size: 14px; color: var(--text2); cursor: pointer; }
.p-nav a:hover { background: #F1F7FA; color: var(--primary); }
.p-nav a.on { background: #EAF2F6; color: var(--primary); font-weight: 500; }
.p-right { margin-left: auto; display: flex; align-items: center; gap: 18px; }
.p-content { max-width: 1200px; margin: 0 auto; padding: 24px 32px 40px; }
</style>
""")

add("src/views/Login.vue", """<template>
  <div class="login-page">
    <div class="bg"><img src="/login-bg.jpg" alt="" /></div>
    <div class="wrap">
      <section class="intro">
        <div class="mark"><span>勤</span></div>
        <h1>高校勤工助学<br />岗位与考勤管理系统</h1>
        <p>岗位申报 · 资格审核 · 排班考勤 · 工时复核 · 补贴核算<br />全流程线上留痕，补贴发放可追溯</p>
        <div class="pill">2026 秋季学期 · 学生资助管理中心</div>
        <ul class="feat">
          <li><i></i>岗位审批与录用按人数硬校验，杜绝超额录用</li>
          <li><i></i>排班自动检测课程与重复班次冲突</li>
          <li><i></i>工时申诉、补贴批次全流程留痕</li>
        </ul>
      </section>

      <section class="panel">
        <h2>账号登录</h2>
        <p class="sub">使用学号或工号登录，连续 5 次失败将锁定 10 分钟</p>
        <el-form @submit.prevent="submit">
          <div class="fld">
            <label>账号</label>
            <el-input v-model="form.username" size="large" placeholder="请输入账号" autocomplete="username" />
          </div>
          <div class="fld">
            <label>密码</label>
            <el-input v-model="form.password" type="password" size="large" show-password
                      placeholder="请输入密码" autocomplete="current-password" @keyup.enter="submit" />
          </div>
          <el-button type="primary" size="large" class="btn-login" :loading="loading" @click="submit">登 录</el-button>
        </el-form>
        <div class="roles">
          <span @click="fill('s_2023010214')">学生 s_2023010214</span>
          <span @click="fill('t_zhou')">用工老师 t_zhou</span>
          <span @click="fill('admin')">资助中心 admin</span>
          <span @click="fill('fin_liu')">财务 fin_liu</span>
        </div>
        <p class="tip">默认密码 admin123，登录后可在个人中心修改</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

function fill(u) {
  form.username = u
  form.password = 'admin123'
}

async function submit() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    const d = await request.post('/api/auth/login', { username: form.username, password: form.password })
    localStorage.setItem('ws_token', d.token)
    store.setLogin(d.user, d.menus)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { position: relative; min-height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.bg { position: absolute; inset: 0; }
.bg img { width: 100%; height: 100%; object-fit: cover; }
.bg:after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(115deg, rgba(15,42,61,.94) 0%, rgba(23,59,87,.86) 46%, rgba(40,114,113,.66) 100%);
}
.wrap { position: relative; display: flex; align-items: center; gap: 80px; padding: 40px; }
.intro { color: #fff; max-width: 520px; }
.mark { width: 46px; height: 46px; border-radius: 11px; background: #287271; display: flex; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 22px; }
.intro h1 { font-size: 32px; line-height: 1.42; font-weight: 600; margin: 0 0 14px; letter-spacing: .5px; }
.intro p { color: rgba(255,255,255,.74); font-size: 14px; line-height: 2; margin: 0; }
.pill { display: inline-block; margin-top: 24px; padding: 6px 14px; border: 1px solid rgba(255,255,255,.28); border-radius: 20px; font-size: 12px; color: rgba(255,255,255,.86); }
.feat { list-style: none; padding: 0; margin: 30px 0 0; color: rgba(255,255,255,.72); font-size: 13px; line-height: 2.1; }
.feat li { display: flex; align-items: center; gap: 10px; }
.feat i { width: 5px; height: 5px; border-radius: 50%; background: #7FB2C9; flex: none; }
.panel { width: 388px; background: #fff; border-radius: 12px; padding: 34px 32px 26px; box-shadow: 0 20px 56px rgba(8,24,36,.34); }
.panel h2 { font-size: 20px; margin: 0 0 6px; color: #173B57; }
.panel .sub { font-size: 12px; color: #8A99A5; margin: 0 0 24px; line-height: 1.7; }
.fld { margin-bottom: 16px; }
.fld label { display: block; font-size: 12px; color: #5A6B77; margin-bottom: 6px; }
.btn-login { width: 100%; height: 44px; font-size: 15px; letter-spacing: 2px; margin-top: 6px; }
.roles { display: flex; gap: 6px; margin-top: 18px; flex-wrap: wrap; }
.roles span { font-size: 11px; padding: 3px 9px; border: 1px solid #DFE7EC; border-radius: 12px; color: #5A6B77; cursor: pointer; }
.roles span:hover { border-color: #2F6B8A; color: #173B57; }
.tip { font-size: 11px; color: #8A99A5; margin: 14px 0 0; }
@media (max-width: 980px) {
  .wrap { flex-direction: column; gap: 28px; padding: 24px; }
  .intro { max-width: 100%; }
  .intro h1 { font-size: 24px; }
  .feat { display: none; }
}
</style>
""")

print("fe layout", len(F))
