# -*- coding: utf-8 -*-
"""视图组 3：评价、标准、规则、留痕、报表、系统管理、个人中心、待办。"""
F = {}


def add(rel, code):
    F[rel] = code.strip() + "\n"


add("src/views/Evaluate.vue", """<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>学期评价</h2>
        <span class="muted" style="margin-left:auto">出勤 30 + 责任 30 + 技能 25 + 协作 15 = 100</span>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="studentName" label="学生" min-width="92" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column label="出勤" width="72"><template #default="{ row }"><span class="num">{{ row.attendanceScore }}</span></template></el-table-column>
        <el-table-column label="责任" width="72"><template #default="{ row }"><span class="num">{{ row.dutyScore }}</span></template></el-table-column>
        <el-table-column label="技能" width="72"><template #default="{ row }"><span class="num">{{ row.skillScore }}</span></template></el-table-column>
        <el-table-column label="协作" width="72"><template #default="{ row }"><span class="num">{{ row.teamScore }}</span></template></el-table-column>
        <el-table-column label="总分" width="88"><template #default="{ row }"><b class="num">{{ row.totalScore }}</b></template></el-table-column>
        <el-table-column prop="feedback" label="学生反馈" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="116"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openScore(row)">评分</el-button></template>
        </el-table-column>
        <template #empty><el-empty description="暂无评价记录" /></template>
      </el-table>
    </div>

    <div class="card">
      <div class="card-h"><h2>评分录入</h2></div>
      <div class="card-b">
        <el-form label-width="110px" style="max-width:620px">
          <el-form-item label="学生"><b>{{ form.studentName || '请从上方选择' }}</b></el-form-item>
          <el-form-item label="出勤（30）"><el-input-number v-model="form.attendanceScore" :min="0" :max="30" /></el-form-item>
          <el-form-item label="责任（30）"><el-input-number v-model="form.dutyScore" :min="0" :max="30" /></el-form-item>
          <el-form-item label="技能（25）"><el-input-number v-model="form.skillScore" :min="0" :max="25" /></el-form-item>
          <el-form-item label="协作（15）"><el-input-number v-model="form.teamScore" :min="0" :max="15" /></el-form-item>
          <el-form-item label="评语"><el-input v-model="form.comment" type="textarea" :rows="3" /></el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!form.id" @click="save">提交评价</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { statusText, statusType } from '@/utils/format'

const rows = ref([]); const loading = ref(false)
const form = reactive({ id: null, studentName: '', attendanceScore: 26, dutyScore: 26, skillScore: 22, teamScore: 13, comment: '' })

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/evaluation/page', { params: { page: 1, size: 50 } })
    rows.value = d.list || []
  } finally { loading.value = false }
}
function openScore(row) {
  Object.assign(form, {
    id: row.id, studentName: row.studentName,
    attendanceScore: row.attendanceScore, dutyScore: row.dutyScore,
    skillScore: row.skillScore, teamScore: row.teamScore, comment: row.comment
  })
}
async function save() {
  const total = form.attendanceScore + form.dutyScore + form.skillScore + form.teamScore
  await request.put('/api/evaluation/' + form.id, { ...form, totalScore: total, status: 'WAIT_STUDENT' })
  ElMessage.success('评价已提交，等待学生确认')
  load()
}
onMounted(load)
</script>
""")

add("src/views/Standard.vue", """<template>
  <div class="grid2">
    <div class="card">
      <div class="card-h"><h2>学期配置</h2><el-button type="primary" size="small" style="margin-left:auto" @click="openSem">新增学期</el-button></div>
      <el-table :data="semesters" border>
        <el-table-column prop="termName" label="学期" min-width="110" />
        <el-table-column label="起止日期" min-width="220"><template #default="{ row }">{{ formatDate(row.startDate) }} ~ {{ formatDate(row.endDate) }}</template></el-table-column>
        <el-table-column label="月工时上限" width="110"><template #default="{ row }"><span class="num">{{ row.monthHourLimit }}</span></template></el-table-column>
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="row.status === 'RUNNING' ? 'success' : 'info'" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
      </el-table>
    </div>
    <div class="card">
      <div class="card-h"><h2>补贴标准</h2><el-button type="primary" size="small" style="margin-left:auto" @click="openStd">调整标准</el-button></div>
      <el-table :data="standards" border>
        <el-table-column label="适用学期" min-width="110"><template #default="{ row }">{{ semName(row.semesterId) }}</template></el-table-column>
        <el-table-column label="每小时标准" width="120"><template #default="{ row }"><span class="num">{{ money(row.hourRate) }}</span></template></el-table-column>
        <el-table-column label="月上限" width="92"><template #default="{ row }"><span class="num">{{ row.monthHourLimit }}</span></template></el-table-column>
        <el-table-column label="特殊系数" width="96"><template #default="{ row }"><span class="num">{{ row.specialFactor }}</span></template></el-table-column>
        <el-table-column label="生效时间" min-width="150"><template #default="{ row }">{{ formatTime(row.effectTime) }}</template></el-table-column>
      </el-table>
    </div>
    <div class="card" style="grid-column:1/-1">
      <div class="card-h"><h2>特殊岗位系数</h2><el-button size="small" style="margin-left:auto" @click="addFactor">新增系数</el-button></div>
      <el-table :data="factors" border>
        <el-table-column prop="postType" label="岗位类型" min-width="160" />
        <el-table-column label="系数" width="100"><template #default="{ row }"><span class="num">{{ row.factor }}</span></template></el-table-column>
        <el-table-column prop="remark" label="说明" min-width="220" />
        <el-table-column label="状态" width="92"><template #default="{ row }"><el-tag :type="row.status === '1' ? 'success' : 'info'" effect="light">{{ row.status === '1' ? '启用' : '停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="110"><template #default="{ row }"><el-button link type="primary" @click="editFactor(row)">编辑</el-button></template></el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="semDlg" title="新增学期" width="460px">
      <el-form label-width="110px">
        <el-form-item label="学期名称"><el-input v-model="sem.termName" /></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="sem.startDate" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="sem.endDate" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="月工时上限"><el-input-number v-model="sem.monthHourLimit" :min="1" :max="120" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="semDlg = false">取消</el-button><el-button type="primary" @click="saveSem">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="stdDlg" title="调整补贴标准" width="460px">
      <el-form label-width="120px">
        <el-form-item label="适用学期">
          <el-select v-model="std.semesterId" style="width:100%">
            <el-option v-for="s in semesters" :key="s.id" :label="s.termName" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="每小时标准"><el-input-number v-model="std.hourRate" :min="1" :precision="2" /></el-form-item>
        <el-form-item label="月工时上限"><el-input-number v-model="std.monthHourLimit" :min="1" :max="120" /></el-form-item>
        <el-form-item label="特殊岗位系数"><el-input-number v-model="std.specialFactor" :min="1" :max="3" :precision="2" :step="0.05" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="stdDlg = false">取消</el-button><el-button type="primary" @click="saveStd">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="facDlg" title="岗位系数" width="440px">
      <el-form label-width="92px">
        <el-form-item label="岗位类型"><el-input v-model="fac.postType" /></el-form-item>
        <el-form-item label="系数"><el-input-number v-model="fac.factor" :min="0.5" :max="3" :precision="2" :step="0.05" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="fac.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="facDlg = false">取消</el-button><el-button type="primary" @click="saveFac">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatDate, formatTime, money, statusText } from '@/utils/format'

const semesters = ref([]); const standards = ref([]); const factors = ref([])
const semDlg = ref(false); const stdDlg = ref(false); const facDlg = ref(false)
const sem = reactive({ termName: '', startDate: '', endDate: '', monthHourLimit: 40, status: 'RUNNING' })
const std = reactive({ semesterId: 1, hourRate: 22, monthHourLimit: 40, specialFactor: 1.1, effectTime: '' })
const fac = reactive({ id: null, postType: '', factor: 1.2, remark: '', status: '1' })

function semName(id) { return (semesters.value.find((s) => s.id === id) || {}).termName || '-' }

async function load() {
  semesters.value = await request.get('/api/semester/list')
  standards.value = await request.get('/api/standard/list')
  factors.value = await request.get('/api/factor/list')
}
function openSem() { semDlg.value = true }
async function saveSem() {
  await request.post('/api/semester', sem)
  ElMessage.success('已保存')
  semDlg.value = false; load()
}
function openStd() { stdDlg.value = true }
async function saveStd() {
  std.effectTime = new Date().toISOString().slice(0, 19).replace('T', ' ')
  await request.post('/api/standard', std)
  ElMessage.success('已保存新标准')
  stdDlg.value = false; load()
}
function addFactor() { Object.assign(fac, { id: null, postType: '', factor: 1.2, remark: '', status: '1' }); facDlg.value = true }
function editFactor(row) { Object.assign(fac, row); facDlg.value = true }
async function saveFac() {
  if (fac.id) await request.put('/api/factor/' + fac.id, fac)
  else await request.post('/api/factor', fac)
  ElMessage.success('已保存')
  facDlg.value = false; load()
}
onMounted(load)
</script>

<style scoped>
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 1200px) { .grid2 { grid-template-columns: 1fr; } }
</style>
""")

add("src/views/RuleConfig.vue", """<template>
  <div>
    <div class="card">
      <div class="card-h">
        <h2>公平匹配权重配置</h2>
        <el-tag :type="sum === 100 ? 'success' : 'danger'" effect="light" style="margin-left:12px">权重合计 {{ sum }}%</el-tag>
        <span class="muted" style="margin-left:auto">当前生效版本 {{ active.version || '-' }}</span>
      </div>
      <div class="card-b">
        <div class="hint" style="margin-bottom:16px">
          创新点「兼顾困难度与能力的公平匹配」：权重合计必须等于 100%，保存后生成新版本并记录生效时间；
          已生成的留痕不受影响，只有新计算或主动重算才使用新权重。
        </div>
        <div class="score-row" v-for="w in weights" :key="w.key">
          <span class="nm">{{ w.label }}</span>
          <el-input-number v-model="form[w.key]" :min="0" :max="100" :step="5" size="small" style="width:110px" />
          <span class="muted">%　{{ w.tip }}</span>
        </div>
        <div style="margin-top:8px">
          <el-button type="primary" @click="save">保存为新版本</el-button>
          <el-button @click="reset">恢复默认</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>规则版本历史</h2></div>
      <el-table :data="history" border>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column label="权重摘要" min-width="200">
          <template #default="{ row }">{{ row.wDifficulty }}/{{ row.wConflict }}/{{ row.wSkill }}/{{ row.wHours }}/{{ row.wAbsent }}/{{ row.wPrefer }}</template>
        </el-table-column>
        <el-table-column label="生效时间" min-width="170"><template #default="{ row }">{{ formatTime(row.effectTime) }}</template></el-table-column>
        <el-table-column prop="creator" label="修改人" width="100" />
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText } from '@/utils/format'

const weights = [
  { key: 'wDifficulty', label: '困难等级', tip: '特别困难 100，困难 80，一般 60，不困难 40' },
  { key: 'wConflict', label: '课表冲突', tip: '无冲突 90，冲突 1 段 60' },
  { key: 'wSkill', label: '技能匹配度', tip: '按岗位能力标签命中比例' },
  { key: 'wHours', label: '已获工时', tip: '越接近月度上限得分越低' },
  { key: 'wAbsent', label: '历史缺勤次数', tip: '每次扣 30 分' },
  { key: 'wPrefer', label: '岗位偏好', tip: '时段匹配 100，否则 75' }
]
const form = reactive({ wDifficulty: 30, wConflict: 15, wSkill: 20, wHours: 15, wAbsent: 10, wPrefer: 10 })
const active = ref({}); const history = ref([])
const sum = computed(() => weights.reduce((s, w) => s + Number(form[w.key] || 0), 0))

async function load() {
  const d = await request.get('/api/match/rule')
  active.value = d.rule || {}
  history.value = d.history || []
  if (d.rule) {
    weights.forEach((w) => { form[w.key] = d.rule[w.key] })
  }
}
async function save() {
  if (sum.value !== 100) { ElMessage.warning('权重合计必须等于 100%，当前为 ' + sum.value + '%'); return }
  await request.post('/api/match/rule', { ...form })
  ElMessage.success('已保存为新版本')
  load()
}
function reset() {
  Object.assign(form, { wDifficulty: 30, wConflict: 15, wSkill: 20, wHours: 15, wAbsent: 10, wPrefer: 10 })
}
onMounted(load)
</script>
""")

add("src/views/ScoreList.vue", """<template>
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
""")

add("src/views/Report.vue", """<template>
  <div>
    <div class="kpi-grid">
      <div class="kpi" v-for="k in kpis" :key="k.k"><div class="k">{{ k.k }}</div><div class="v num">{{ k.v }}</div><div class="d">{{ k.d }}</div></div>
    </div>
    <div class="chart-grid" style="margin-bottom:12px">
      <div class="chart-box"><h3>申请 / 录用转化</h3><div ref="c1" class="chart"></div></div>
      <div class="chart-box"><h3>岗位类型分布</h3><div ref="c2" class="chart"></div></div>
      <div class="chart-box"><h3>满意度分布</h3><div ref="c3" class="chart"></div></div>
    </div>
    <div class="card">
      <div class="card-h"><h2>推荐采纳率与人工调整率</h2>
        <span class="tag" style="margin-left:auto">人工调整率 {{ adjustRate }}</span>
      </div>
      <el-table :data="rows" border>
        <el-table-column prop="postName" label="岗位" min-width="220" />
        <el-table-column label="计算次数" width="110"><template #default="{ row }"><span class="num">{{ row.cnt }}</span></template></el-table-column>
        <el-table-column label="人工调整" width="110"><template #default="{ row }"><span class="num">{{ row.adjust }}</span></template></el-table-column>
        <el-table-column label="采纳率" width="110"><template #default="{ row }"><span class="num">{{ row.rate }}</span></template></el-table-column>
        <el-table-column label="说明" min-width="220"><template #default="{ row }"><span class="muted">{{ row.tip }}</span></template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { money } from '@/utils/format'

const c1 = ref(); const c2 = ref(); const c3 = ref()
const kpis = ref([]); const rows = ref([]); const adjustRate = ref('0%')
const C = ['#173B57', '#287271', '#2F6B8A', '#8A99A5', '#7FB2C9']

onMounted(async () => {
  const s = await request.get('/api/dashboard/stats')
  kpis.value = [
    { k: '在办岗位', v: s.postCount, d: '不含已结束' },
    { k: '申请人数', v: s.applyCount, d: '累计' },
    { k: '录用率', v: s.employRate, d: '录用 / 申请' },
    { k: '完成工时', v: s.finishHours, d: '本月有效工时' },
    { k: '缺勤率', v: s.absentRate, d: '缺勤 / 考勤' },
    { k: '补贴金额', v: money(s.subsidyAmount), d: '批次合计' }
  ]
  const c = await request.get('/api/dashboard/charts')
  adjustRate.value = c.adjustRate
  await nextTick()
  echarts.init(c1.value).setOption({
    grid: { left: 36, right: 14, top: 18, bottom: 26 }, tooltip: {},
    xAxis: { type: 'category', data: ['申请', '录用'], axisLabel: { color: '#8A99A5' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F5' } }, axisLabel: { color: '#8A99A5' } },
    series: [{ type: 'bar', barWidth: 34, data: [s.applyCount, s.employedCount], itemStyle: { color: C[0], borderRadius: [4, 4, 0, 0] } }]
  })
  const typeMap = { '助管': 0, '助教': 0, '助研': 0, '志愿服务': 0 }
  const posts = await request.get('/api/post/page', { params: { page: 1, size: 100 } })
  ;(posts.list || []).forEach((p) => { typeMap[p.postType] = (typeMap[p.postType] || 0) + 1 })
  echarts.init(c2.value).setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 11 } },
    series: [{ type: 'pie', radius: ['44%', '66%'], center: ['50%', '44%'], label: { show: false },
      data: Object.entries(typeMap).map(([k, v], i) => ({ name: k, value: v, itemStyle: { color: C[i % 5] } })) }]
  })
  echarts.init(c3.value).setOption({
    grid: { left: 34, right: 12, top: 18, bottom: 24 }, tooltip: {},
    xAxis: { type: 'category', data: c.satisfaction.map((x) => x.name), axisLabel: { color: '#8A99A5', fontSize: 10, interval: 0 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F5' } }, axisLabel: { color: '#8A99A5' } },
    series: [{ type: 'bar', barWidth: 20, data: c.satisfaction.map((x) => x.value), itemStyle: { color: C[1], borderRadius: [4, 4, 0, 0] } }]
  })

  const scores = await request.get('/api/match/score/page', { params: { page: 1, size: 200 } })
  const byPost = {}
  ;(scores.list || []).forEach((x) => {
    byPost[x.postName] = byPost[x.postName] || { cnt: 0, adjust: 0 }
    byPost[x.postName].cnt++
    if (x.adjustGrade) byPost[x.postName].adjust++
  })
  rows.value = Object.entries(byPost).map(([postName, v]) => ({
    postName, cnt: v.cnt, adjust: v.adjust,
    rate: ((v.cnt - v.adjust) / v.cnt * 100).toFixed(1) + '%',
    tip: v.adjust ? '人工调整 ' + v.adjust + ' 次，需关注匹配规则是否符合实际' : '全部采纳系统推荐'
  }))
})
</script>

<style scoped>
.tag { font-size: 12px; padding: 2px 10px; border-radius: 11px; color: #2F6B8A; background: #F1F7FA; }
</style>
""")

add("src/views/UserList.vue", """<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="kw" placeholder="姓名 / 账号 / 学号" clearable @keyup.enter="reload" />
          <el-select v-model="roleId" placeholder="全部角色" clearable style="width:180px" @change="reload">
            <el-option v-for="r in roles" :key="r.id" :label="r.roleName" :value="r.id" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button type="primary" plain style="margin-left:auto" @click="openAdd">新建用户</el-button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>用户列表</h2><span class="muted" style="margin-left:auto">共 {{ total }} 条</span></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column label="头像" width="72"><template #default="{ row }"><img class="avatar" :src="row.avatar" alt="" /></template></el-table-column>
        <el-table-column prop="username" label="账号" min-width="130" />
        <el-table-column prop="realName" label="姓名" min-width="92" />
        <el-table-column prop="roleName" label="角色" min-width="130" />
        <el-table-column prop="orgName" label="所属部门/学院" min-width="150" />
        <el-table-column prop="studentNo" label="学号" width="130" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column label="状态" width="90"><template #default="{ row }"><el-tag :type="row.status === '1' ? 'success' : 'info'" effect="light">{{ row.status === '1' ? '启用' : '停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="resetPwd(row)">重置密码</el-button>
            <el-button link :type="row.status === '1' ? 'danger' : 'success'" @click="toggle(row)">{{ row.status === '1' ? '停用' : '启用' }}</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无用户" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10,20,50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-dialog v-model="dlg" :title="form.id ? '编辑用户' : '新建用户'" width="520px">
      <el-form label-width="96px">
        <el-form-item label="账号" required><el-input v-model="form.username" :disabled="!!form.id" /></el-form-item>
        <el-form-item label="姓名" required><el-input v-model="form.realName" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.roleId" style="width:100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.roleName" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门/学院">
          <el-select v-model="form.orgId" style="width:100%">
            <el-option v-for="o in orgs" :key="o.id" :label="o.orgName" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学号"><el-input v-model="form.studentNo" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item v-if="!form.id" label="初始密码"><el-input v-model="form.password" placeholder="留空默认 123456" /></el-form-item>
        <el-form-item label="头像">
          <el-upload :show-file-list="false" :http-request="uploadAvatar">
            <img v-if="form.avatar" class="avatar" :src="form.avatar" alt="" />
            <el-button v-else size="small">上传头像</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const rows = ref([]); const roles = ref([]); const orgs = ref([])
const total = ref(0); const page = ref(1); const size = ref(10)
const kw = ref(''); const roleId = ref(''); const loading = ref(false); const dlg = ref(false)
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/user/page', { params: { page: page.value, size: size.value, kw: kw.value, roleId: roleId.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function openAdd() { Object.keys(form).forEach((k) => delete form[k]); form.roleId = 3; dlg.value = true }
function openEdit(row) { Object.keys(form).forEach((k) => delete form[k]); Object.assign(form, JSON.parse(JSON.stringify(row))); dlg.value = true }
async function uploadAvatar(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.avatar = d.path
}
async function save() {
  if (form.id) await request.put('/api/user/' + form.id, form)
  else await request.post('/api/user', form)
  ElMessage.success('已保存')
  dlg.value = false; load()
}
async function resetPwd(row) {
  await ElMessageBox.confirm('将重置为初始密码 123456，确认？', '重置密码', { type: 'warning' })
  await request.post('/api/user/' + row.id + '/reset')
  ElMessage.success('已重置')
}
async function toggle(row) {
  await request.put('/api/user/' + row.id, { status: row.status === '1' ? '0' : '1', realName: row.realName, phone: row.phone, email: row.email })
  ElMessage.success('已更新')
  load()
}
onMounted(async () => {
  roles.value = await request.get('/api/role/list')
  orgs.value = await request.get('/api/user/orgs')
  load()
})
</script>

<style scoped>
.avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); }
</style>
""")

add("src/views/RoleList.vue", """<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>角色与数据范围</h2><el-button type="primary" size="small" style="margin-left:auto" @click="openAdd">新增角色</el-button></div>
      <el-table :data="rows" border>
        <el-table-column prop="roleCode" label="角色编码" min-width="120" />
        <el-table-column prop="roleName" label="角色名称" min-width="150" />
        <el-table-column prop="dataScope" label="数据范围" min-width="130" />
        <el-table-column label="状态" width="92"><template #default="{ row }"><el-tag :type="row.status === '1' ? 'success' : 'info'" effect="light">{{ row.status === '1' ? '启用' : '停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openAssign(row)">分配菜单</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dlg" :title="form.id ? '编辑角色' : '新增角色'" width="480px">
      <el-form label-width="96px">
        <el-form-item label="角色编码"><el-input v-model="form.roleCode" /></el-form-item>
        <el-form-item label="角色名称"><el-input v-model="form.roleName" /></el-form-item>
        <el-form-item label="数据范围">
          <el-select v-model="form.dataScope" style="width:100%">
            <el-option label="本人 SELF" value="SELF" />
            <el-option label="本部门 DEPT" value="DEPT" />
            <el-option label="全部 ALL" value="ALL" />
            <el-option label="只读全部 ALL_READONLY" value="ALL_READONLY" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="assignDlg" :title="'为「' + (cur.roleName || '') + '」分配菜单'" width="520px">
      <el-tree ref="tree" :data="menuTree" show-checkbox node-key="id" :props="{ label: 'menuName', children: 'children' }"
               default-expand-all :default-checked-keys="checked" />
      <template #footer>
        <el-button @click="assignDlg = false">取消</el-button>
        <el-button type="primary" @click="saveAssign">保存授权</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const rows = ref([]); const menus = ref([]); const menuTree = ref([])
const dlg = ref(false); const assignDlg = ref(false); const tree = ref(); const cur = ref({})
const checked = ref([])
const form = reactive({})

async function load() {
  const d = await request.get('/api/role/page', { params: { page: 1, size: 20 } })
  rows.value = d.list || []
}
async function loadMenus() {
  menus.value = await request.get('/api/menu/tree')
}
function openAdd() { Object.keys(form).forEach((k) => delete form[k]); form.dataScope = 'SELF'; dlg.value = true }
function openEdit(row) { Object.keys(form).forEach((k) => delete form[k]); Object.assign(form, row); dlg.value = true }
async function save() {
  if (form.id) await request.put('/api/role/' + form.id, form)
  else await request.post('/api/role', form)
  ElMessage.success('已保存'); dlg.value = false; load()
}
async function openAssign(row) {
  cur.value = row
  const ids = await request.get('/api/role/' + row.id + '/menus')
  checked.value = ids || []
  assignDlg.value = true
  setTimeout(() => tree.value && tree.value.setCheckedKeys(checked.value), 60)
}
async function saveAssign() {
  const ids = tree.value.getCheckedKeys().concat(tree.value.getHalfCheckedKeys())
  await request.put('/api/role/' + cur.value.id + '/menus', ids)
  ElMessage.success('授权已保存，重新登录后生效')
  assignDlg.value = false
}
onMounted(async () => {
  await Promise.all([load(), loadMenus()])
  const roots = []
  const map = {}
  menus.value.forEach((m) => { map[m.id] = { ...m, children: [] } })
  menus.value.forEach((m) => {
    if (m.parentId && map[m.parentId]) map[m.parentId].children.push(map[m.id])
    else roots.push(map[m.id])
  })
  menuTree.value = roots
})
</script>
""")

add("src/views/MenuList.vue", """<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>菜单管理</h2>
        <span class="muted" style="margin-left:auto">visible=0 的菜单不在侧边栏显示，但可被权限引用</span>
      </div>
      <el-table :data="rows" border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="menuName" label="菜单名称" min-width="130" />
        <el-table-column prop="menuType" label="类型" width="80" />
        <el-table-column prop="path" label="路由" min-width="150" />
        <el-table-column prop="perms" label="权限标识" min-width="160" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="显示" width="90"><template #default="{ row }"><el-tag :type="row.visible === 1 ? 'success' : 'info'" effect="light">{{ row.visible === 1 ? '显示' : '隐藏' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="toggle(row)">{{ row.visible === 1 ? '隐藏' : '显示' }}</el-button></template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const rows = ref([])
async function load() { rows.value = await request.get('/api/menu/tree') }
async function toggle(row) {
  await request.put('/api/menu/' + row.id, { visible: row.visible === 1 ? 0 : 1 })
  ElMessage.success('已更新')
  load()
}
onMounted(load)
</script>
""")

add("src/views/Profile.vue", """<template>
  <div class="grid">
    <div class="card">
      <div class="card-h"><h2>个人资料</h2></div>
      <div class="card-b">
        <div class="avatar-row">
          <el-upload :show-file-list="false" :http-request="uploadAvatar">
            <img class="big-avatar" :src="form.avatar || ''" alt="" />
          </el-upload>
          <div>
            <div><b>{{ form.realName }}</b> <span class="muted">{{ form.roleName }}</span></div>
            <div class="muted">{{ form.orgName }} · {{ form.studentNo || form.username }}</div>
            <el-button size="small" style="margin-top:8px" @click="$refs.up?.click()">更换头像</el-button>
          </div>
        </div>
        <el-form label-width="88px" style="margin-top:18px">
          <el-form-item label="姓名"><el-input v-model="form.realName" /></el-form-item>
          <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
          <el-form-item><el-button type="primary" @click="saveProfile">保存资料</el-button></el-form-item>
        </el-form>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>修改密码</h2></div>
      <div class="card-b">
        <el-form label-width="88px">
          <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" show-password /></el-form-item>
          <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" show-password placeholder="至少 6 位" /></el-form-item>
          <el-form-item label="确认密码"><el-input v-model="pwd.confirm" type="password" show-password /></el-form-item>
          <el-form-item><el-button type="primary" @click="savePwd">修改密码</el-button></el-form-item>
        </el-form>
        <div class="hint">密码使用 BCrypt 保存，任何接口与日志都不会返回密码字段。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'

const form = reactive({})
const pwd = reactive({ oldPassword: '', newPassword: '', confirm: '' })

async function load() {
  const me = await request.get('/api/auth/me')
  Object.assign(form, me)
  store.setUser(me)
}
async function uploadAvatar(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.avatar = d.path
  await request.put('/api/auth/profile', { realName: form.realName, phone: form.phone, email: form.email, avatar: form.avatar })
  ElMessage.success('头像已更新，右上角同步显示')
  load()
}
async function saveProfile() {
  await request.put('/api/auth/profile', { realName: form.realName, phone: form.phone, email: form.email, avatar: form.avatar })
  ElMessage.success('资料已保存')
  load()
}
async function savePwd() {
  if (pwd.newPassword !== pwd.confirm) { ElMessage.warning('两次输入的新密码不一致'); return }
  if (pwd.newPassword.length < 6) { ElMessage.warning('新密码至少 6 位'); return }
  await request.post('/api/auth/password', { oldPassword: pwd.oldPassword, newPassword: pwd.newPassword })
  ElMessage.success('密码已修改')
  pwd.oldPassword = ''; pwd.newPassword = ''; pwd.confirm = ''
}
onMounted(load)
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.avatar-row { display: flex; gap: 16px; align-items: center; }
.big-avatar { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); background: #E7EEF2; cursor: pointer; }
@media (max-width: 1000px) { .grid { grid-template-columns: 1fr; } }
</style>
""")

add("src/views/Todo.vue", """<template>
  <div>
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="kpi"><div class="k">待处理</div><div class="v num">{{ posts.length + apps.length }}</div><div class="d">待审岗位 + 待筛申请</div></div>
      <div class="kpi"><div class="k">待面试</div><div class="v num">{{ interview }}</div><div class="d">已安排面试</div></div>
      <div class="kpi"><div class="k">工时待确认</div><div class="v num">{{ pendingHours }}</div><div class="d">本月汇总</div></div>
      <div class="kpi"><div class="k">申诉待处理</div><div class="v num">{{ appeals }}</div><div class="d">工时申诉</div></div>
    </div>
    <div class="card">
      <div class="card-h"><h2>待我处理</h2><span class="muted" style="margin-left:auto">按待办优先、更新时间倒序</span></div>
      <el-table :data="list" border>
        <el-table-column prop="type" label="类型" width="110" />
        <el-table-column prop="no" label="业务编号" min-width="140" />
        <el-table-column prop="title" label="摘要" min-width="240" />
        <el-table-column label="更新时间" min-width="160"><template #default="{ row }">{{ formatTime(row.time) }}</template></el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="$router.push(row.to)">处理</el-button></template>
        </el-table-column>
        <template #empty><el-empty description="当前没有待办，可到岗位广场或岗位管理继续操作" /></template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'
import { store } from '@/store/user'

const list = ref([]); const posts = ref([]); const apps = ref([])
const interview = ref(0); const pendingHours = ref(0); const appeals = ref(0)

onMounted(async () => {
  const role = store.user?.roleCode
  if (role !== 'STUDENT') {
    const p = await request.get('/api/post/page', { params: { page: 1, size: 20, status: 'PENDING' } })
    posts.value = p.list || []
    posts.value.forEach((x) => list.value.push({ type: '岗位审批', no: x.postNo, title: x.postName + ' · ' + x.deptName, time: x.updateTime, to: '/post-audit' }))
    const a = await request.get('/api/application/page', { params: { page: 1, size: 20, status: 'SCREENING' } })
    apps.value = a.list || []
    apps.value.forEach((x) => list.value.push({ type: '申请待筛选', no: x.applyNo, title: x.studentName + ' · ' + x.postName, time: x.createTime, to: '/employment' }))
    const i = await request.get('/api/application/page', { params: { page: 1, size: 1, status: 'INTERVIEW' } })
    interview.value = i.total || 0
    const h = await request.get('/api/hour/summary/page', { params: { page: 1, size: 1, status: 'PENDING' } })
    pendingHours.value = h.total || 0
    const ap = await request.get('/api/hour/appeal/page', { params: { page: 1, size: 1, status: 'PENDING' } })
    appeals.value = ap.total || 0
    ;(ap.list || []).forEach((x) => list.value.push({ type: '工时申诉', no: 'APL-' + x.id, title: x.studentName + ' 申诉 ' + x.appealHours + ' 小时', time: x.createTime, to: '/hours' }))
  } else {
    const a = await request.get('/api/application/page', { params: { page: 1, size: 20, mine: true, status: 'INTERVIEW' } })
    ;(a.list || []).forEach((x) => list.value.push({ type: '面试通知', no: x.applyNo, title: x.postName + ' · ' + (x.interviewTime || ''), time: x.updateTime, to: '/my-apply' }))
    const h = await request.get('/api/hour/summary/page', { params: { page: 1, size: 1, mine: true, status: 'PENDING' } })
    pendingHours.value = h.total || 0
  }
})
</script>
""")

print("views3", len(F))
