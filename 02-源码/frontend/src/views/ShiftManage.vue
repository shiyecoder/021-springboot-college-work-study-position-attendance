<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-select v-model="postId" placeholder="全部岗位" clearable style="width:220px" @change="reload">
            <el-option v-for="p in posts" :key="p.id" :label="p.postName" :value="p.id" />
          </el-select>
          <el-date-picker v-model="week" type="week" format="YYYY 第 ww 周" value-format="YYYY-MM-DD"
                          placeholder="选择周" :clearable="false" @change="reload" />
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button type="primary" plain style="margin-left:auto" @click="openAdd">新增班次</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h">
        <h2>本周排班</h2>
        <el-tag v-if="conflictCount" type="warning" effect="light" style="margin-left:10px">检测到 {{ conflictCount }} 处冲突</el-tag>
        <span class="muted" style="margin-left:auto">后端校验：同人同日重复班次 + 与登记可用时段冲突</span>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="studentName" label="学生" min-width="96" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column prop="shiftDate" label="日期" width="118" />
        <el-table-column label="时段" width="130"><template #default="{ row }"><span class="num">{{ row.startTime }}-{{ row.endTime }}</span></template></el-table-column>
        <el-table-column prop="workPlace" label="地点" min-width="150" />
        <el-table-column label="计划工时" width="96"><template #default="{ row }"><span class="num">{{ row.planHours }}</span></template></el-table-column>
        <el-table-column label="冲突校验" min-width="180">
          <template #default="{ row }">
            <el-tag v-if="row.conflictFlag" type="danger" effect="light">冲突</el-tag>
            <el-tag v-else type="success" effect="light">通过</el-tag>
            <span class="muted" style="margin-left:6px">{{ row.conflictReason || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.conflictFlag" link type="primary" @click="adjust(row)">调整</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="本周暂无排班，可新增班次" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="size" @current-change="load" />
      </div>
    </div>

    <el-dialog v-model="dlg" title="新增班次" width="520px">
      <el-form label-width="92px">
        <el-form-item label="岗位" required>
          <el-select v-model="form.postId" style="width:100%">
            <el-option v-for="p in posts" :key="p.id" :label="p.postName" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生" required>
          <el-select v-model="form.studentId" style="width:100%">
            <el-option v-for="s in students" :key="s.id" :label="s.realName + '（' + (s.orgName || '') + '）'" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.shiftDate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="时段">
          <el-input v-model="form.startTime" placeholder="18:00" style="width:100px" />
          <span style="margin:0 8px">至</span>
          <el-input v-model="form.endTime" placeholder="22:00" style="width:100px" />
        </el-form-item>
        <el-form-item label="地点"><el-input v-model="form.workPlace" /></el-form-item>
        <el-form-item label="计划工时"><el-input-number v-model="form.planHours" :min="0.5" :step="0.5" style="width:160px" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存并校验冲突</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(20)
const loading = ref(false); const dlg = ref(false); const conflictCount = ref(0)
const posts = ref([]); const students = ref([]); const postId = ref('')
const week = ref(startOfWeek(new Date()))
const form = reactive({})

function startOfWeek(d) {
  const x = new Date(d)
  const day = (x.getDay() + 6) % 7
  x.setDate(x.getDate() - day)
  return x.toISOString().slice(0, 10)
}

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/shift/page', { params: { page: page.value, size: size.value, postId: postId.value, weekStart: week.value } })
    rows.value = d.list || []; total.value = d.total || 0
    conflictCount.value = rows.value.filter((r) => r.conflictFlag).length
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, { postId: posts.value[0]?.id, startTime: '18:00', endTime: '22:00', planHours: 4, shiftDate: week.value })
  dlg.value = true
}
async function save() {
  try {
    const r = await request.post('/api/shift', form)
    ElMessage[r.conflictFlag ? 'warning' : 'success'](r.conflictFlag ? '已保存，但检测到冲突：' + r.conflictReason : '排班成功')
    dlg.value = false
    load()
  } catch (e) { /* 后端已提示 */ }
}
async function adjust(row) {
  const { value } = await ElMessageBox.prompt('调整后的时段（如 19:00）', '调整班次', { inputValue: row.startTime })
  await request.post('/api/shift/' + row.id + '/adjust', { startTime: value, endTime: row.endTime })
  ElMessage.success('已调整')
  load()
}
async function remove(row) {
  await ElMessageBox.confirm('确认删除该班次？', '删除确认', { type: 'warning' })
  await request.delete('/api/shift/' + row.id)
  ElMessage.success('已删除')
  load()
}
onMounted(async () => {
  const d = await request.get('/api/post/page', { params: { page: 1, size: 50 } })
  posts.value = d.list || []
  const u = await request.get('/api/user/page', { params: { page: 1, size: 50, roleId: 3 } })
  students.value = u.list || []
  load()
})
</script>
