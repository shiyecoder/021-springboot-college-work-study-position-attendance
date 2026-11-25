<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-select v-model="batchId" placeholder="选择批次" style="width:220px" @change="load">
            <el-option v-for="b in batches" :key="b.id" :label="b.batchNo + '（' + b.summaryMonth + '）'" :value="b.id" />
          </el-select>
          <el-select v-model="payStatus" placeholder="全部状态" clearable style="width:180px" @change="load">
            <el-option label="待发放" value="WAIT" />
            <el-option label="已发放" value="PAID" />
            <el-option label="发放失败" value="FAIL" />
          </el-select>
          <el-button type="primary" @click="load">查询</el-button>
          <span class="muted" style="margin-left:auto">财务只登记线下发放状态，系统不直接转账</span>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>发放明细</h2>
        <el-tag v-if="curBatch" type="info" effect="light" style="margin-left:auto">{{ statusText(curBatch.status) }} · 金额已锁定</el-tag>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="studentNo" label="学号" width="130" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column label="金额" width="120"><template #default="{ row }"><span class="num">{{ money(row.amount) }}</span></template></el-table-column>
        <el-table-column label="发放状态" width="110"><template #default="{ row }"><el-tag :type="statusType(row.payStatus)" effect="light">{{ statusText(row.payStatus) }}</el-tag></template></el-table-column>
        <el-table-column label="发放时间" min-width="160"><template #default="{ row }">{{ formatTime(row.payTime) }}</template></el-table-column>
        <el-table-column label="失败原因" min-width="180"><template #default="{ row }"><span class="muted">{{ row.failReason || '-' }}</span></template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.payStatus !== 'PAID'" link type="primary" @click="pay(row, 'PAID')">登记已发放</el-button>
            <el-button v-if="row.payStatus === 'WAIT'" link type="danger" @click="pay(row, 'FAIL')">登记失败</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="该批次暂无明显" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="size" @current-change="load" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, money, statusText, statusType } from '@/utils/format'

const rows = ref([]); const batches = ref([]); const batchId = ref(''); const curBatch = ref(null)
const payStatus = ref(''); const total = ref(0); const page = ref(1); const size = ref(20)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/subsidy/item/page', { params: { page: page.value, size: size.value, batchId: batchId.value, payStatus: payStatus.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
async function pay(row, status) {
  let reason = ''
  if (status === 'FAIL') {
    const r = await ElMessageBox.prompt('请填写发放失败原因（不少于 5 个字）', '登记失败', { inputPlaceholder: '如：银行卡信息有误' })
    reason = r.value
  }
  await request.post('/api/subsidy/item/' + row.id + '/pay', { status, reason })
  ElMessage.success('已登记')
  load()
}
onMounted(async () => {
  const d = await request.get('/api/subsidy/batch/page', { params: { page: 1, size: 20 } })
  batches.value = d.list || []
  const target = batches.value.find((b) => b.status !== 'AUDITING') || batches.value[0]
  if (target) { batchId.value = target.id; curBatch.value = target }
  load()
})
</script>
