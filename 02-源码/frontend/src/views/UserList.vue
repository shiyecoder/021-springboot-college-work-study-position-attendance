<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="kw" placeholder="姓名 / 账号 / 学号" clearable @keyup.enter="reload" />
          <el-select v-model="roleId" placeholder="全部角色" clearable style="width:180px" @change="reload">
            <el-option v-for="r in roles" :key="r.id" :label="r.roleName" :value="r.id" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button type="primary" plain style="margin-left:auto" @click="openAdd">新建用户</el-button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>用户列表</h2><span class="muted" style="margin-left:auto">共 {{ total }} 条</span></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column label="头像" width="72"><template #default="{ row }"><img class="avatar" :src="row.avatar" alt="" /></template></el-table-column>
        <el-table-column prop="username" label="账号" min-width="130" />
        <el-table-column prop="realName" label="姓名" min-width="92" />
        <el-table-column prop="roleName" label="角色" min-width="130" />
        <el-table-column prop="orgName" label="所属部门/学院" min-width="150" />
        <el-table-column prop="studentNo" label="学号" width="130" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column label="状态" width="90"><template #default="{ row }"><el-tag :type="row.status === '1' ? 'success' : 'info'" effect="light">{{ row.status === '1' ? '启用' : '停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="resetPwd(row)">重置密码</el-button>
            <el-button link :type="row.status === '1' ? 'danger' : 'success'" @click="toggle(row)">{{ row.status === '1' ? '停用' : '启用' }}</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无用户" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10,20,50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-dialog v-model="dlg" :title="form.id ? '编辑用户' : '新建用户'" width="520px">
      <el-form label-width="96px">
        <el-form-item label="账号" required><el-input v-model="form.username" :disabled="!!form.id" /></el-form-item>
        <el-form-item label="姓名" required><el-input v-model="form.realName" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.roleId" style="width:100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.roleName" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门/学院">
          <el-select v-model="form.orgId" style="width:100%">
            <el-option v-for="o in orgs" :key="o.id" :label="o.orgName" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学号"><el-input v-model="form.studentNo" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item v-if="!form.id" label="初始密码"><el-input v-model="form.password" placeholder="留空默认 123456" /></el-form-item>
        <el-form-item label="头像">
          <el-upload :show-file-list="false" :http-request="uploadAvatar">
            <img v-if="form.avatar" class="avatar" :src="form.avatar" alt="" />
            <el-button v-else size="small">上传头像</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const rows = ref([]); const roles = ref([]); const orgs = ref([])
const total = ref(0); const page = ref(1); const size = ref(10)
const kw = ref(''); const roleId = ref(''); const loading = ref(false); const dlg = ref(false)
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/user/page', { params: { page: page.value, size: size.value, kw: kw.value, roleId: roleId.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function openAdd() { Object.keys(form).forEach((k) => delete form[k]); form.roleId = 3; dlg.value = true }
function openEdit(row) { Object.keys(form).forEach((k) => delete form[k]); Object.assign(form, JSON.parse(JSON.stringify(row))); dlg.value = true }
async function uploadAvatar(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.avatar = d.path
}
async function save() {
  if (form.id) await request.put('/api/user/' + form.id, form)
  else await request.post('/api/user', form)
  ElMessage.success('已保存')
  dlg.value = false; load()
}
async function resetPwd(row) {
  await ElMessageBox.confirm('将重置为初始密码 123456，确认？', '重置密码', { type: 'warning' })
  await request.post('/api/user/' + row.id + '/reset')
  ElMessage.success('已重置')
}
async function toggle(row) {
  await request.put('/api/user/' + row.id, { status: row.status === '1' ? '0' : '1', realName: row.realName, phone: row.phone, email: row.email })
  ElMessage.success('已更新')
  load()
}
onMounted(async () => {
  roles.value = await request.get('/api/role/list')
  orgs.value = await request.get('/api/user/orgs')
  load()
})
</script>

<style scoped>
.avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); }
</style>
