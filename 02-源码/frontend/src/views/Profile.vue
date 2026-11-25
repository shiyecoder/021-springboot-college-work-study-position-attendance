<template>
  <div class="grid">
    <div class="card">
      <div class="card-h"><h2>个人资料</h2></div>
      <div class="card-b">
        <div class="avatar-row">
          <el-upload :show-file-list="false" :http-request="uploadAvatar">
            <img class="big-avatar" :src="form.avatar || ''" alt="" />
          </el-upload>
          <div>
            <div><b>{{ form.realName }}</b> <span class="muted">{{ form.roleName }}</span></div>
            <div class="muted">{{ form.orgName }} · {{ form.studentNo || form.username }}</div>
            <el-button size="small" style="margin-top:8px" @click="$refs.up?.click()">更换头像</el-button>
          </div>
        </div>
        <el-form label-width="88px" style="margin-top:18px">
          <el-form-item label="姓名"><el-input v-model="form.realName" /></el-form-item>
          <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
          <el-form-item><el-button type="primary" @click="saveProfile">保存资料</el-button></el-form-item>
        </el-form>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>修改密码</h2></div>
      <div class="card-b">
        <el-form label-width="88px">
          <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" show-password /></el-form-item>
          <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" show-password placeholder="至少 6 位" /></el-form-item>
          <el-form-item label="确认密码"><el-input v-model="pwd.confirm" type="password" show-password /></el-form-item>
          <el-form-item><el-button type="primary" @click="savePwd">修改密码</el-button></el-form-item>
        </el-form>
        <div class="hint">密码使用 BCrypt 保存，任何接口与日志都不会返回密码字段。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'

const form = reactive({})
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })

async function load() {
  const me = await request.get('/api/auth/me')
  Object.assign(form, me)
  store.setUser(me)
}
async function uploadAvatar(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.avatar = d.path
  await request.put('/api/auth/profile', { realName: form.realName, phone: form.phone, email: form.email, avatar: form.avatar })
  ElMessage.success('头像已更新，右上角同步显示')
  load()
}
async function saveProfile() {
  await request.put('/api/auth/profile', { realName: form.realName, phone: form.phone, email: form.email, avatar: form.avatar })
  ElMessage.success('资料已保存')
  load()
}
async function savePwd() {
  if (pwd.newPassword !== pwd.confirm) { ElMessage.warning('两次输入的新密码不一致'); return }
  if (pwd.newPassword.length < 6) { ElMessage.warning('新密码至少 6 位'); return }
  await request.post('/api/auth/password', { oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
  ElMessage.success('密码已修改')
  pwd.oldPassword = ''; pwd.newPassword = ''; pwd.confirm = ''
}
onMounted(load)
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.avatar-row { display: flex; gap: 16px; align-items: center; }
.big-avatar { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); background: #E7EEF2; cursor: pointer; }
@media (max-width: 1000px) { .grid { grid-template-columns: 1fr; } }
</style>
