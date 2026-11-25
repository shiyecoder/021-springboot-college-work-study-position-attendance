<template>
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
