<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>我的工时</h2>
        <el-date-picker v-model="month" type="month" value-format="YYYY-MM" style="margin-left:auto;width:160px" @change="load" />
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="summaryMonth" label="月份" width="100" />
        <el-table-column prop="postName" label="岗位" min-width="200" />
        <el-table-column label="计划工时" width="100"><template #default="{ row }"><span class="num">{{ row.planHours }}</span></template></el-table-column>
        <el-table-column label="实际工时" width="100"><template #default="{ row }"><span class="num">{{ row.actualHours }}</span></template></el-table-column>
        <el-table-column label="有效工时" width="100"><template #default="{ row }"><span class="num">{{ row.validHours }}</span></template></el-table-column>
        <el-table-column label="月上限" width="92"><template #default="{ row }"><span class="num">{{ row.limitHours }}</span></template></el-table-column>
        <el-table-column label="状态" width="112"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openAppeal(row)">工时申诉</el-button></template>
        </el-table-column>
        <template #empty><el-empty description="该月份暂无工时记录" /></template>
      </el-table>
    </div>

    <div class="card">
      <div class="card-h"><h2>我的申诉</h2></div>
      <el-table :data="appeals" border>
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column label="申诉工时" width="100"><template #default="{ row }"><span class="num">{{ row.appealHours }}</span></template></el-table-column>
        <el-table-column prop="reason" label="原因" min-width="260" show-overflow-tooltip />
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="处理意见" min-width="200"><template #default="{ row }"><span class="muted">{{ row.handleRemark || '-' }}</span></template></el-table-column>
        <el-table-column label="提交时间" min-width="160"><template #default="{ row }">{{ formatTime(row.createTime) }}</template></el-table-column>
        <template #empty><el-empty description="暂无申诉记录" /></template>
      </el-table>
    </div>

    <el-dialog v-model="dlg" title="工时申诉" width="460px">
      <el-form label-width="92px">
        <el-form-item label="汇总月份"><span class="num">{{ cur.summaryMonth }}</span></el-form-item>
        <el-form-item label="当前有效工时"><span class="num">{{ cur.validHours }} 小时</span></el-form-item>
        <el-form-item label="申诉工时" required><el-input-number v-model="form.hours" :min="0.5" :step="0.5" /></el-form-item>
        <el-form-item label="申诉原因" required><el-input v-model="form.reason" type="textarea" :rows="3" placeholder="不少于 5 个字，说明实际出勤情况" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="submit">提交申诉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const rows = ref([]); const appeals = ref([]); const loading = ref(false)
const month = ref(''); const dlg = ref(false); const cur = ref({})
const form = reactive({ hours: 1, reason: '' })

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/hour/summary/page', { params: { page: 1, size: 20, mine: true, month: month.value } })
    rows.value = d.list || []
    const a = await request.get('/api/hour/appeal/page', { params: { page: 1, size: 20, mine: true } })
    appeals.value = a.list || []
  } finally { loading.value = false }
}
function openAppeal(row) { cur.value = row; form.hours = 1; form.reason = ''; dlg.value = true }
async function submit() {
  if (form.reason.trim().length < 5) { ElMessage.warning('申诉原因不少于 5 个字'); return }
  await request.post('/api/hour/appeal', { summaryId: String(cur.value.id), hours: String(form.hours), reason: form.reason })
  ElMessage.success('申诉已提交')
  dlg.value = false
  load()
}
onMounted(load)
</script>
