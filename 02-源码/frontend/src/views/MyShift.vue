<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>我的排班</h2>
        <el-tag v-if="conflict" type="danger" effect="light" style="margin-left:10px">存在冲突班次，请联系老师调整</el-tag>
        <el-date-picker v-model="week" type="week" format="YYYY 第 ww 周" value-format="YYYY-MM-DD"
                        style="margin-left:auto;width:180px" :clearable="false" @change="load" />
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="shiftDate" label="日期" width="120" />
        <el-table-column label="时段" width="130"><template #default="{ row }"><span class="num">{{ row.startTime }}-{{ row.endTime }}</span></template></el-table-column>
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column prop="workPlace" label="地点" min-width="150" />
        <el-table-column label="计划工时" width="96"><template #default="{ row }"><span class="num">{{ row.planHours }}</span></template></el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.conflictFlag ? 'danger' : statusType(row.status)" effect="light">
              {{ row.conflictFlag ? '冲突' : statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="说明" min-width="180"><template #default="{ row }"><span class="muted">{{ row.conflictReason || '-' }}</span></template></el-table-column>
        <template #empty><el-empty description="本周暂无排班" /></template>
      </el-table>
    </div>
    <div class="card">
      <div class="card-h"><h2>我的工时与补贴</h2></div>
      <div class="card-b">
        <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin:0">
          <div class="kpi"><div class="k">本月有效工时</div><div class="v num">{{ sum.validHours || 0 }}</div><div class="d">上限 40 小时</div></div>
          <div class="kpi"><div class="k">预计补贴</div><div class="v num">{{ money(sum.validHours ? sum.validHours * 22 : 0) }}</div><div class="d">按 22 元/时估算</div></div>
          <div class="kpi"><div class="k">累计工时</div><div class="v num">{{ sum.planHours || 0 }}</div><div class="d">本月计划</div></div>
          <div class="kpi"><div class="k">考勤异常</div><div class="v num">{{ abnormal }}</div><div class="d">迟到/早退/缺勤</div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { money, statusText, statusType } from '@/utils/format'

const rows = ref([]); const loading = ref(false); const conflict = ref(false)
const sum = ref({}); const abnormal = ref(0)
const week = ref(startOfWeek(new Date()))

function startOfWeek(d) {
  const x = new Date(d); const day = (x.getDay() + 6) % 7
  x.setDate(x.getDate() - day)
  return x.toISOString().slice(0, 10)
}
async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/shift/page', { params: { page: 1, size: 50, mine: true, weekStart: week.value } })
    rows.value = d.list || []
    conflict.value = rows.value.some((r) => r.conflictFlag)
  } finally { loading.value = false }
}
onMounted(async () => {
  load()
  const hs = await request.get('/api/hour/summary/page', { params: { page: 1, size: 5, mine: true } })
  sum.value = (hs.list || [])[0] || {}
  const att = await request.get('/api/attendance/page', { params: { page: 1, size: 50, mine: true } })
  abnormal.value = (att.list || []).filter((a) => ['LATE', 'EARLY', 'ABSENT'].includes(a.status)).length
})
</script>
