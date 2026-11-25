<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-select v-model="status" placeholder="全部状态" clearable style="width:180px" @change="reload">
            <el-option v-for="s in ['NORMAL','LATE','EARLY','ABSENT','LEAVE','MAKEUP']" :key="s" :label="statusText(s)" :value="s" />
          </el-select>
          <el-date-picker v-model="month" type="month" value-format="YYYY-MM" placeholder="考勤月份" @change="reload" />
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <span class="muted" style="margin-left:auto">异常记录需逐条复核，通过后计入工时</span>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>考勤记录</h2><span class="muted" style="margin-left:auto">共 {{ total }} 条</span></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="postName" label="岗位" min-width="170" />
        <el-table-column prop="workDate" label="日期" width="116" />
        <el-table-column label="签到" min-width="156"><template #default="{ row }">{{ formatTime(row.checkInTime) }}</template></el-table-column>
        <el-table-column label="签退" min-width="156"><template #default="{ row }">{{ formatTime(row.checkOutTime) }}</template></el-table-column>
        <el-table-column label="有效工时" width="92"><template #default="{ row }"><span class="num">{{ row.validHours }}</span></template></el-table-column>
        <el-table-column label="状态" width="92"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="异常证据" width="96">
          <template #default="{ row }"><img v-if="row.evidenceImage" class="thumb" :src="row.evidenceImage" alt="" /><span v-else class="muted">-</span></template>
        </el-table-column>
        <el-table-column label="复核" width="96"><template #default="{ row }"><el-tag :type="row.verifyStatus === 'PASS' ? 'success' : row.verifyStatus === 'REJECT' ? 'danger' : 'warning'" effect="light">{{ statusText(row.verifyStatus) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="verify(row, true)">通过</el-button>
            <el-button link type="danger" @click="verify(row, false)">驳回</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10,20,50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const status = ref(''); const month = ref(''); const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/attendance/page', { params: { page: page.value, size: size.value, status: status.value, month: month.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { status.value = ''; month.value = ''; reload() }
async function verify(row, pass) {
  let reason = ''
  if (!pass) {
    const r = await ElMessageBox.prompt('请填写驳回原因（不少于 5 个字）', '驳回考勤', { inputPlaceholder: '驳回原因' })
    reason = r.value
  }
  await request.post('/api/attendance/' + row.id + '/verify', { pass: String(pass), reason })
  ElMessage.success('已处理')
  load()
}
onMounted(load)
</script>
