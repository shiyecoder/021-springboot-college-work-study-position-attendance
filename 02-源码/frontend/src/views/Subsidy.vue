<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-date-picker v-model="month" type="month" value-format="YYYY-MM" placeholder="核算月份" style="width:180px" />
          <el-button type="primary" @click="generate">生成批次</el-button>
          <span class="muted" style="margin-left:auto">金额由后端按「有效工时 × 时薪 × 系数」计算，已发放不可改</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>补贴批次</h2></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="batchNo" label="批次号" min-width="150" />
        <el-table-column prop="summaryMonth" label="月份" width="100" />
        <el-table-column label="人数" width="80"><template #default="{ row }"><span class="num">{{ row.personCount }}</span></template></el-table-column>
        <el-table-column label="总工时" width="100"><template #default="{ row }"><span class="num">{{ row.totalHours }}</span></template></el-table-column>
        <el-table-column label="补贴总额" width="130"><template #default="{ row }"><span class="num">{{ money(row.totalAmount) }}</span></template></el-table-column>
        <el-table-column label="状态" width="112"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="审核时间" min-width="160"><template #default="{ row }">{{ formatTime(row.auditTime) }}</template></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'AUDITING'" link type="primary" @click="audit(row)">审核通过</el-button>
            <el-button link type="primary" @click="openItems(row)">查看明细</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无批次，选择月份后生成" /></template>
      </el-table>
    </div>

    <div class="card" v-if="curBatch">
      <div class="card-h"><h2>批次明细 · {{ curBatch.batchNo }}</h2>
        <span class="muted" style="margin-left:auto">审核通过后金额锁定，差错走调整单</span>
      </div>
      <el-table :data="items" border>
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="studentNo" label="学号" width="130" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column label="有效工时" width="96"><template #default="{ row }"><span class="num">{{ row.validHours }}</span></template></el-table-column>
        <el-table-column label="时薪" width="88"><template #default="{ row }"><span class="num">{{ row.hourRate }}</span></template></el-table-column>
        <el-table-column label="系数" width="80"><template #default="{ row }"><span class="num">{{ row.factor }}</span></template></el-table-column>
        <el-table-column label="应发金额" width="120"><template #default="{ row }"><span class="num">{{ money(row.amount) }}</span></template></el-table-column>
        <el-table-column label="发放状态" width="104"><template #default="{ row }"><el-tag :type="statusType(row.payStatus)" effect="light">{{ statusText(row.payStatus) }}</el-tag></template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, money, statusText, statusType } from '@/utils/format'

const rows = ref([]); const items = ref([]); const curBatch = ref(null)
const loading = ref(false); const month = ref('2026-10')

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/subsidy/batch/page', { params: { page: 1, size: 20 } })
    rows.value = d.list || []
  } finally { loading.value = false }
}
async function generate() {
  await ElMessageBox.confirm('将按本月已确认工时生成补贴批次，生成后不可重复生成，确认继续？', '生成批次', { type: 'warning' })
  await request.post('/api/subsidy/generate', { month: month.value })
  ElMessage.success('批次已生成')
  load()
}
async function audit(row) {
  await request.post('/api/subsidy/batch/' + row.id + '/audit')
  ElMessage.success('审核通过，金额已锁定')
  load()
}
async function openItems(row) {
  curBatch.value = row
  const d = await request.get('/api/subsidy/item/page', { params: { page: 1, size: 50, batchId: row.id } })
  items.value = d.list || []
}
onMounted(load)
</script>
