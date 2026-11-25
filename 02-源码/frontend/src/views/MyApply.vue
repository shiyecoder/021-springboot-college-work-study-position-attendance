<template>
  <div>
    <div class="card">
      <div class="card-h">
        <h2>我的岗位申请</h2>
        <el-radio-group v-model="status" size="small" style="margin-left:16px" @change="reload">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="SCREENING">待筛选</el-radio-button>
          <el-radio-button label="INTERVIEW">待面试</el-radio-button>
          <el-radio-button label="EMPLOYED">已录用</el-radio-button>
          <el-radio-button label="REJECTED">已驳回</el-radio-button>
        </el-radio-group>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="applyNo" label="申请编号" min-width="130" />
        <el-table-column prop="postName" label="岗位" min-width="200" />
        <el-table-column prop="deptName" label="用工部门" min-width="120" />
        <el-table-column label="匹配分" width="96"><template #default="{ row }"><span class="num">{{ row.matchScore ?? '-' }}</span></template></el-table-column>
        <el-table-column label="面试时间" min-width="160"><template #default="{ row }">{{ formatTime(row.interviewTime) }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="申请时间" min-width="160"><template #default="{ row }">{{ formatTime(row.createTime) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="['SCREENING','INTERVIEW'].includes(row.status)" link type="danger" @click="withdraw(row)">撤回</el-button>
            <el-button link type="primary" @click="$router.push('/post/' + row.postId)">详情</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，清空筛选或到岗位广场申请" /></template>
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
const status = ref(''); const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/application/page', { params: { page: page.value, size: size.value, status: status.value, mine: true } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
async function withdraw(row) {
  await ElMessageBox.confirm('撤回后如需再申请需重新提交，确认撤回？', '撤回确认', { type: 'warning' })
  await request.post('/api/application/' + row.id + '/withdraw')
  ElMessage.success('已撤回')
  load()
}
onMounted(load)
</script>
