<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-date-picker v-model="month" type="month" value-format="YYYY-MM" placeholder="汇总月份" @change="reload" />
          <el-select v-model="status" placeholder="全部状态" clearable style="width:180px" @change="reload">
            <el-option label="待确认" value="PENDING" />
            <el-option label="已确认" value="CONFIRMED" />
            <el-option label="超上限" value="OVER_LIMIT" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button type="success" plain :disabled="!selected.length" @click="batchConfirm">批量确认（{{ selected.length }}）</el-button>
          <span class="muted" style="margin-left:auto">批量操作逐条返回结果，不整批静默失败</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>月度工时汇总</h2></div>
      <el-table :data="rows" v-loading="loading" border @selection-change="(v) => (selected = v)">
        <el-table-column type="selection" width="46" />
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column prop="summaryMonth" label="月份" width="96" />
        <el-table-column label="计划工时" width="96"><template #default="{ row }"><span class="num">{{ row.planHours }}</span></template></el-table-column>
        <el-table-column label="实际工时" width="96"><template #default="{ row }"><span class="num">{{ row.actualHours }}</span></template></el-table-column>
        <el-table-column label="有效工时" width="96"><template #default="{ row }"><span class="num">{{ row.validHours }}</span></template></el-table-column>
        <el-table-column label="月上限" width="88"><template #default="{ row }"><span class="num">{{ row.limitHours }}</span></template></el-table-column>
        <el-table-column label="状态" width="112"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'PENDING'" link type="primary" @click="confirm(row)">确认</el-button>
            <el-button v-if="row.status === 'OVER_LIMIT'" link type="warning" @click="approve(row)">特别审批</el-button>
            <el-button link type="primary" @click="$router.push('/my-hours')">明细</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="该月份暂无工时汇总" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10,20,50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>工时申诉</h2><span class="muted" style="margin-left:auto">学生申诉需在期限内处理</span></div>
      <el-table :data="appeals" border>
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="month" label="月份" width="92" />
        <el-table-column label="申诉工时" width="96"><template #default="{ row }"><span class="num">{{ row.appealHours }}</span></template></el-table-column>
        <el-table-column prop="reason" label="申诉原因" min-width="240" show-overflow-tooltip />
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="提交时间" min-width="160"><template #default="{ row }">{{ formatTime(row.createTime) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'PENDING'" link type="primary" @click="handle(row, 'PASS')">通过</el-button>
            <el-button v-if="row.status === 'PENDING'" link type="danger" @click="handle(row, 'REJECT')">驳回</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无申诉" /></template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const rows = ref([]); const appeals = ref([]); const total = ref(0)
const page = ref(1); const size = ref(10); const month = ref(''); const status = ref('')
const loading = ref(false); const selected = ref([])

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/hour/summary/page', { params: { page: page.value, size: size.value, month: month.value, status: status.value } })
    rows.value = d.list || []; total.value = d.total || 0
    const a = await request.get('/api/hour/appeal/page', { params: { page: 1, size: 10 } })
    appeals.value = a.list || []
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
async function confirm(row) {
  await request.post('/api/hour/summary/' + row.id + '/confirm')
  ElMessage.success('已确认')
  load()
}
async function batchConfirm() {
  const r = await request.post('/api/hour/summary/batch-confirm', selected.value.map((x) => x.id))
  const ok = r.filter((x) => x.ok).length
  const bad = r.filter((x) => !x.ok)
  ElMessage[bad.length ? 'warning' : 'success'](`成功 ${ok} 条${bad.length ? '，失败 ' + bad.length + ' 条：' + bad.map((b) => b.msg).join('；') : ''}`)
  load()
}
async function approve(row) {
  await request.post('/api/hour/summary/' + row.id + '/confirm')
  ElMessage.success('已提交特别审批并确认')
  load()
}
async function handle(row, s) {
  let remark = ''
  if (s === 'REJECT') {
    const r = await ElMessageBox.prompt('请填写驳回原因（不少于 5 个字）', '驳回申诉', { inputPlaceholder: '原因' })
    remark = r.value
  }
  await request.post('/api/hour/appeal/' + row.id + '/handle', { status: s, remark })
  ElMessage.success('已处理')
  load()
}
onMounted(load)
</script>
