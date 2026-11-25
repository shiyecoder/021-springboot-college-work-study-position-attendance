<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>计算结果留痕</h2>
        <span class="muted" style="margin-left:auto">相同输入 + 相同规则版本必然得到相同结果，可复算校验</span>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column prop="ruleVersion" label="规则版本" width="90" />
        <el-table-column label="总分" width="84"><template #default="{ row }"><b class="num">{{ row.totalScore }}</b></template></el-table-column>
        <el-table-column label="等级" width="76"><template #default="{ row }"><el-tag :type="row.grade === 'A' ? 'success' : row.grade === 'B' ? 'primary' : 'warning'" effect="light">{{ row.grade }}</el-tag></template></el-table-column>
        <el-table-column label="人工调整" width="110"><template #default="{ row }"><span class="muted">{{ row.adjustGrade ? row.adjustGrade + '（' + row.adjustBy + '）' : '无' }}</span></template></el-table-column>
        <el-table-column label="计算时间" min-width="160"><template #default="{ row }">{{ formatTime(row.createTime) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="open(row)">查看快照</el-button>
            <el-button link type="primary" @click="adjust(row)">修正</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无计算记录，可在录用审核台执行计算" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="size" @current-change="load" />
      </div>
    </div>

    <el-drawer v-model="dlg" title="计算快照" size="460px">
      <div v-if="cur">
        <div class="kv">
          <span>学生</span><b>{{ cur.studentName }}</b>
          <span>岗位</span><b>{{ cur.postName }}</b>
          <span>规则版本</span><b>{{ cur.ruleVersion }}</b>
          <span>总分 / 等级</span><b class="num">{{ cur.totalScore }} / {{ cur.grade }}</b>
          <span>计算时间</span><b>{{ formatTime(cur.createTime) }}</b>
        </div>
        <div class="hint" style="margin-top:14px;white-space:pre-wrap">{{ pretty }}</div>
        <div v-if="cur.adjustGrade" class="hint" style="margin-top:10px;background:#FDF7E9;border-color:#B26B00">
          人工修正为 {{ cur.adjustGrade }} 级，原因：{{ cur.adjustReason }}（原始结果未覆盖）
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const loading = ref(false); const dlg = ref(false); const cur = ref(null)
const pretty = computed(() => {
  if (!cur.value?.snapshotJson) return ''
  try { return JSON.stringify(JSON.parse(cur.value.snapshotJson), null, 2) } catch (e) { return cur.value.snapshotJson }
})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/match/score/page', { params: { page: page.value, size: size.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function open(row) { cur.value = row; dlg.value = true }
async function adjust(row) {
  const grade = await ElMessageBox.prompt('调整后的等级（A/B/C/D）', '人工修正', { inputValue: row.grade })
  const reason = await ElMessageBox.prompt('修正原因（不少于 5 个字）', '人工修正', { inputPlaceholder: '原因' })
  await request.post('/api/match/score/' + row.id + '/adjust', { grade: grade.value, reason: reason.value })
  ElMessage.success('已保存修正')
  load()
}
onMounted(load)
</script>

<style scoped>
.kv { display: grid; grid-template-columns: 92px 1fr; gap: 8px; font-size: 13px; }
.kv span { color: var(--text3); }
</style>
