<template>
  <div>
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="kpi"><div class="k">待审核</div><div class="v num">{{ stat.pending }}</div><div class="d">含超 3 天 1 个</div></div>
      <div class="kpi"><div class="k">在招岗位</div><div class="v num">{{ stat.recruiting }}</div><div class="d">覆盖多个部门</div></div>
      <div class="kpi"><div class="k">已满额</div><div class="v num">{{ stat.full }}</div><div class="d">可结束或扩招</div></div>
      <div class="kpi"><div class="k">草稿</div><div class="v num">{{ stat.draft }}</div><div class="d">部门未提交</div></div>
    </div>
    <div class="card">
      <div class="card-h">
        <h2>待审核岗位</h2>
        <el-select v-model="deptId" placeholder="全部部门" clearable size="small" style="width:180px;margin-left:12px" @change="reload">
          <el-option v-for="o in depts" :key="o.id" :label="o.orgName" :value="o.id" />
        </el-select>
        <span class="muted" style="margin-left:auto">审批需核对必要性、预算、安全风险与人数</span>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="postNo" label="岗位编号" min-width="130" />
        <el-table-column prop="postName" label="岗位名称" min-width="190" />
        <el-table-column prop="deptName" label="用工部门" min-width="110" />
        <el-table-column label="人数" width="80"><template #default="{ row }"><span class="num">{{ row.recruitNum }}</span></template></el-table-column>
        <el-table-column label="预算" width="120"><template #default="{ row }"><span class="num">{{ money(row.budget) }}</span></template></el-table-column>
        <el-table-column prop="teacherName" label="指导老师" width="100" />
        <el-table-column label="提交时间" min-width="160"><template #default="{ row }">{{ formatTime(row.updateTime) }}</template></el-table-column>
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openAudit(row)">审批</el-button></template>
        </el-table-column>
        <template #empty><el-empty description="当前没有待审核岗位" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="size" @current-change="load" />
      </div>
    </div>

    <el-drawer v-model="drawer" title="岗位审批" size="480px">
      <div v-if="cur">
        <div class="sum">
          <div><b>{{ cur.postName }}</b> <span class="muted">{{ cur.postNo }}</span></div>
          <div class="muted">{{ cur.deptName }} · {{ cur.teacherName }} · {{ cur.workPeriod }}</div>
          <div class="num" style="margin-top:6px">招聘 {{ cur.recruitNum }} 人 · 时薪 {{ cur.hourRate }} 元 · 预算 {{ money(cur.budget) }}</div>
        </div>
        <el-form label-width="92px" style="margin-top:16px">
          <el-form-item label="必要性">
            <div class="hint">{{ cur.postDesc }}</div>
          </el-form-item>
          <el-form-item label="审批意见">
            <el-input v-model="reason" type="textarea" :rows="3" placeholder="驳回时必须填写不少于 5 个字的原因" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="danger" plain @click="act('REJECTED')">驳回</el-button>
        <el-button type="primary" @click="act('RECRUITING')">通过并发布</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, money, statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const loading = ref(false); const drawer = ref(false); const cur = ref(null); const reason = ref('')
const deptId = ref(''); const depts = ref([])
const stat = ref({ pending: 0, recruiting: 0, full: 0, draft: 0 })

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/post/page', { params: { page: page.value, size: size.value, status: 'PENDING', deptId: deptId.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function openAudit(row) { cur.value = row; reason.value = ''; drawer.value = true }
async function act(to) {
  if (to === 'REJECTED' && reason.value.trim().length < 5) { ElMessage.warning('驳回必须填写不少于 5 个字的原因'); return }
  await request.post('/api/post/' + cur.value.id + '/transition', { toStatus: to, reason: reason.value || '审核通过，同意发布' })
  ElMessage.success('操作成功')
  drawer.value = false
  load(); loadStat()
}
async function loadStat() {
  for (const s of ['PENDING', 'RECRUITING', 'FULL', 'DRAFT']) {
    const d = await request.get('/api/post/page', { params: { page: 1, size: 1, status: s } })
    stat.value[({ PENDING: 'pending', RECRUITING: 'recruiting', FULL: 'full', DRAFT: 'draft' })[s]] = d.total
  }
}
onMounted(async () => {
  depts.value = (await request.get('/api/user/orgs') || []).filter((o) => o.orgType === 'DEPT')
  load(); loadStat()
})
</script>

<style scoped>
.sum { background: #F6F9FA; border-radius: 6px; padding: 12px 14px; font-size: 13px; line-height: 1.9; }
</style>
