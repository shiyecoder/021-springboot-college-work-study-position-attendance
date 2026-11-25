<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="q.kw" placeholder="岗位名称 / 编号" clearable @keyup.enter="reload" />
          <el-select v-model="q.postType" placeholder="岗位类型" clearable>
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
          <el-select v-model="q.status" placeholder="招聘状态" clearable>
            <el-option v-for="s in statusList" :key="s" :label="statusText(s)" :value="s" />
          </el-select>
          <el-input v-model="q.workPeriod" placeholder="工作时段" clearable />
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" plain style="margin-left:auto" @click="openAdd">新建岗位</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>岗位列表</h2><span class="muted" style="margin-left:auto">共 {{ total }} 条</span></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column label="封面" width="86"><template #default="{ row }"><img class="thumb" :src="row.coverImage" alt="" /></template></el-table-column>
        <el-table-column prop="postNo" label="岗位编号" min-width="130" />
        <el-table-column prop="postName" label="岗位名称" min-width="190" />
        <el-table-column prop="deptName" label="用工部门" min-width="110" />
        <el-table-column prop="postType" label="类型" width="90" />
        <el-table-column label="人数" width="96"><template #default="{ row }"><span class="num">{{ row.hiredNum }}/{{ row.recruitNum }}</span></template></el-table-column>
        <el-table-column label="时薪" width="88"><template #default="{ row }"><span class="num">{{ row.hourRate }}</span></template></el-table-column>
        <el-table-column prop="workPeriod" label="工作时段" min-width="150" />
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="更新时间" min-width="160"><template #default="{ row }">{{ formatTime(row.updateTime) }}</template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'DRAFT' || row.status === 'REJECTED'" link type="primary" @click="trans(row, 'PENDING', '提交审核')">提交</el-button>
            <el-button v-if="row.status === 'RECRUITING'" link type="primary" @click="trans(row, 'FINISHED', '结束岗位')">结束</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，清空筛选或新建岗位" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10,20,50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="form.id ? '编辑岗位' : '新建岗位'" size="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="岗位名称" required><el-input v-model="form.postName" /></el-form-item>
        <el-form-item label="岗位类型" required>
          <el-select v-model="form.postType" style="width:220px">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作地点" required><el-input v-model="form.workPlace" /></el-form-item>
        <el-form-item label="招聘人数" required><el-input-number v-model="form.recruitNum" :min="1" :max="99" style="width:180px" /></el-form-item>
        <el-form-item label="时薪标准" required><el-input-number v-model="form.hourRate" :min="1" :precision="2" style="width:180px" /></el-form-item>
        <el-form-item label="工作时段"><el-input v-model="form.workPeriod" maxlength="100" show-word-limit placeholder="如：工作日 18:00-22:00" /></el-form-item>
        <el-form-item label="能力要求"><el-input v-model="form.abilityReq" maxlength="100" show-word-limit /></el-form-item>
        <el-form-item label="预算"><el-input-number v-model="form.budget" :min="0" :precision="2" style="width:200px" /></el-form-item>
        <el-form-item label="岗位职责"><el-input v-model="form.postDesc" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="岗位附图">
          <el-upload :show-file-list="false" :http-request="uploadCover">
            <img v-if="form.coverImage" :src="form.coverImage" class="thumb" alt="" />
            <el-button v-else size="small">上传图片</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const loading = ref(false); const saving = ref(false); const drawer = ref(false)
const types = ['助管', '助教', '助研', '志愿服务']
const statusList = ['DRAFT', 'PENDING', 'RECRUITING', 'FULL', 'FINISHED', 'REJECTED']
const q = reactive({ kw: '', postType: '', status: '', workPeriod: '' })
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/post/page', { params: { page: page.value, size: size.value, ...q } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { q.kw = ''; q.postType = ''; q.status = ''; q.workPeriod = ''; reload() }

function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, { recruitNum: 1, hourRate: 22, postType: '助管', postDesc: '' })
  drawer.value = true
}
function openEdit(row) {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, JSON.parse(JSON.stringify(row)))
  drawer.value = true
}
async function uploadCover(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.coverImage = d.path
}
async function save() {
  saving.value = true
  try {
    if (form.id) await request.put('/api/post/' + form.id, form)
    else await request.post('/api/post', form)
    ElMessage.success('保存成功')
    drawer.value = false
    load()
  } finally { saving.value = false }
}
async function trans(row, to, title) {
  const { value } = await ElMessageBox.prompt('请填写原因（不少于 5 个字）', title, { inputPlaceholder: '变更原因' })
  await request.post('/api/post/' + row.id + '/transition', { toStatus: to, reason: value })
  ElMessage.success('操作成功')
  load()
}
async function remove(row) {
  await ElMessageBox.confirm('删除后不可恢复，确认删除该岗位？', '删除确认', { type: 'warning' })
  await request.delete('/api/post/' + row.id)
  ElMessage.success('已删除')
  load()
}
onMounted(load)
</script>
