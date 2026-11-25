# -*- coding: utf-8 -*-
"""视图组 2：排班、考勤、工时、补贴发放。"""
F = {}


def add(rel, code):
    F[rel] = code.strip() + "\n"


add("src/views/ShiftManage.vue", """<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-select v-model="postId" placeholder="全部岗位" clearable style="width:220px" @change="reload">
            <el-option v-for="p in posts" :key="p.id" :label="p.postName" :value="p.id" />
          </el-select>
          <el-date-picker v-model="week" type="week" format="YYYY 第 ww 周" value-format="YYYY-MM-DD"
                          placeholder="选择周" :clearable="false" @change="reload" />
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button type="primary" plain style="margin-left:auto" @click="openAdd">新增班次</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h">
        <h2>本周排班</h2>
        <el-tag v-if="conflictCount" type="warning" effect="light" style="margin-left:10px">检测到 {{ conflictCount }} 处冲突</el-tag>
        <span class="muted" style="margin-left:auto">后端校验：同人同日重复班次 + 与登记可用时段冲突</span>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="studentName" label="学生" min-width="96" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column prop="shiftDate" label="日期" width="118" />
        <el-table-column label="时段" width="130"><template #default="{ row }"><span class="num">{{ row.startTime }}-{{ row.endTime }}</span></template></el-table-column>
        <el-table-column prop="workPlace" label="地点" min-width="150" />
        <el-table-column label="计划工时" width="96"><template #default="{ row }"><span class="num">{{ row.planHours }}</span></template></el-table-column>
        <el-table-column label="冲突校验" min-width="180">
          <template #default="{ row }">
            <el-tag v-if="row.conflictFlag" type="danger" effect="light">冲突</el-tag>
            <el-tag v-else type="success" effect="light">通过</el-tag>
            <span class="muted" style="margin-left:6px">{{ row.conflictReason || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.conflictFlag" link type="primary" @click="adjust(row)">调整</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="本周暂无排班，可新增班次" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="size" @current-change="load" />
      </div>
    </div>

    <el-dialog v-model="dlg" title="新增班次" width="520px">
      <el-form label-width="92px">
        <el-form-item label="岗位" required>
          <el-select v-model="form.postId" style="width:100%">
            <el-option v-for="p in posts" :key="p.id" :label="p.postName" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生" required>
          <el-select v-model="form.studentId" style="width:100%">
            <el-option v-for="s in students" :key="s.id" :label="s.realName + '（' + (s.orgName || '') + '）'" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.shiftDate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="时段">
          <el-input v-model="form.startTime" placeholder="18:00" style="width:100px" />
          <span style="margin:0 8px">至</span>
          <el-input v-model="form.endTime" placeholder="22:00" style="width:100px" />
        </el-form-item>
        <el-form-item label="地点"><el-input v-model="form.workPlace" /></el-form-item>
        <el-form-item label="计划工时"><el-input-number v-model="form.planHours" :min="0.5" :step="0.5" style="width:160px" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存并校验冲突</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(20)
const loading = ref(false); const dlg = ref(false); const conflictCount = ref(0)
const posts = ref([]); const students = ref([]); const postId = ref('')
const week = ref(startOfWeek(new Date()))
const form = reactive({})

function startOfWeek(d) {
  const x = new Date(d)
  const day = (x.getDay() + 6) % 7
  x.setDate(x.getDate() - day)
  return x.toISOString().slice(0, 10)
}

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/shift/page', { params: { page: page.value, size: size.value, postId: postId.value, weekStart: week.value } })
    rows.value = d.list || []; total.value = d.total || 0
    conflictCount.value = rows.value.filter((r) => r.conflictFlag).length
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, { postId: posts.value[0]?.id, startTime: '18:00', endTime: '22:00', planHours: 4, shiftDate: week.value })
  dlg.value = true
}
async function save() {
  try {
    const r = await request.post('/api/shift', form)
    ElMessage[r.conflictFlag ? 'warning' : 'success'](r.conflictFlag ? '已保存，但检测到冲突：' + r.conflictReason : '排班成功')
    dlg.value = false
    load()
  } catch (e) { /* 后端已提示 */ }
}
async function adjust(row) {
  const { value } = await ElMessageBox.prompt('调整后的时段（如 19:00）', '调整班次', { inputValue: row.startTime })
  await request.post('/api/shift/' + row.id + '/adjust', { startTime: value, endTime: row.endTime })
  ElMessage.success('已调整')
  load()
}
async function remove(row) {
  await ElMessageBox.confirm('确认删除该班次？', '删除确认', { type: 'warning' })
  await request.delete('/api/shift/' + row.id)
  ElMessage.success('已删除')
  load()
}
onMounted(async () => {
  const d = await request.get('/api/post/page', { params: { page: 1, size: 50 } })
  posts.value = d.list || []
  const u = await request.get('/api/user/page', { params: { page: 1, size: 50, roleId: 3 } })
  students.value = u.list || []
  load()
})
</script>
""")

add("src/views/MyShift.vue", """<template>
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
""")

add("src/views/CheckIn.vue", """<template>
  <div>
    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>今日班次</h2></div>
        <div class="card-b" v-if="shift">
          <div class="kv">
            <span>岗位</span><b>{{ shift.postName }}</b>
            <span>时段</span><b class="num">{{ shift.startTime }}-{{ shift.endTime }}</b>
            <span>地点</span><b>{{ shift.workPlace }}</b>
            <span>计划工时</span><b class="num">{{ shift.planHours }} 小时</b>
          </div>
          <div style="margin-top:16px">
            <el-button type="primary" @click="openCheck('IN')">签 到</el-button>
            <el-button @click="openCheck('OUT')">签 退</el-button>
            <el-button @click="makeupDlg = true">补卡申请</el-button>
          </div>
          <div class="hint" style="margin-top:14px">迟到超过 5 分钟自动记迟到并扣减 0.5 小时有效工时；未签到不可签退。</div>
        </div>
        <el-empty v-else description="今日没有排班" />
      </div>

      <div class="card">
        <div class="card-h"><h2>页面验证码</h2>
          <el-button link type="primary" style="margin-left:auto" @click="getCaptcha">刷新</el-button>
        </div>
        <div class="card-b">
          <div class="code num">{{ captcha || '----' }}</div>
          <el-input v-model="inputCode" placeholder="请输入验证码" maxlength="4" style="margin-top:12px" />
          <div class="muted" style="margin-top:8px">验证码 5 分钟内有效，连续 3 次错误需重新获取</div>
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h2>本月考勤</h2></div>
        <div class="card-b">
          <div class="kv">
            <span>出勤天数</span><b class="num">{{ stat.normal }}</b>
            <span>迟到</span><b class="num">{{ stat.late }}</b>
            <span>早退</span><b class="num">{{ stat.early }}</b>
            <span>缺勤</span><b class="num">{{ stat.absent }}</b>
            <span>有效工时</span><b class="num">{{ stat.hours }}</b>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>考勤明细</h2></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="workDate" label="日期" width="118" />
        <el-table-column prop="postName" label="岗位" min-width="180" />
        <el-table-column label="签到" min-width="160"><template #default="{ row }">{{ formatTime(row.checkInTime) }}</template></el-table-column>
        <el-table-column label="签退" min-width="160"><template #default="{ row }">{{ formatTime(row.checkOutTime) }}</template></el-table-column>
        <el-table-column label="有效工时" width="96"><template #default="{ row }"><span class="num">{{ row.validHours }}</span></template></el-table-column>
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="说明" min-width="180"><template #default="{ row }"><span class="muted">{{ row.abnormalReason || '-' }}</span></template></el-table-column>
        <template #empty><el-empty description="本月暂无考勤记录" /></template>
      </el-table>
    </div>

    <el-dialog v-model="dlg" :title="type === 'IN' ? '签到' : '签退'" width="400px">
      <div class="muted" style="margin-bottom:10px">请输入页面验证码完成{{ type === 'IN' ? '签到' : '签退' }}</div>
      <el-input v-model="inputCode" maxlength="4" placeholder="4 位验证码" />
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="doCheck">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="makeupDlg" title="补卡申请" width="460px">
      <el-form label-width="90px">
        <el-form-item label="日期"><el-date-picker v-model="makeup.workDate" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="补卡原因" required><el-input v-model="makeup.reason" type="textarea" :rows="3" placeholder="不少于 5 个字" /></el-form-item>
        <el-form-item label="证据图片" required>
          <el-upload :show-file-list="false" :http-request="uploadEvidence">
            <img v-if="makeup.evidence" :src="makeup.evidence" class="thumb" alt="" />
            <el-button v-else size="small">上传证据</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="makeupDlg = false">取消</el-button>
        <el-button type="primary" @click="submitMakeup">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const shift = ref(null); const captcha = ref(''); const inputCode = ref('')
const dlg = ref(false); const type = ref('IN'); const makeupDlg = ref(false)
const rows = ref([]); const loading = ref(false)
const stat = ref({ normal: 0, late: 0, early: 0, absent: 0, hours: 0 })
const makeup = reactive({ workDate: '', reason: '', evidence: '' })

async function getCaptcha() {
  const d = await request.get('/api/attendance/captcha')
  captcha.value = d.code
  inputCode.value = ''
}
function openCheck(t) {
  type.value = t
  getCaptcha()
  dlg.value = true
}
async function doCheck() {
  await request.post('/api/attendance/check', { type: type.value, shiftId: String(shift.value?.id || ''), captcha: inputCode.value })
  ElMessage.success(type.value === 'IN' ? '签到成功' : '签退成功')
  dlg.value = false
  load()
}
async function uploadEvidence(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  makeup.evidence = d.path
}
async function submitMakeup() {
  if (makeup.reason.trim().length < 5) { ElMessage.warning('补卡原因不少于 5 个字'); return }
  if (!makeup.evidence) { ElMessage.warning('请上传证据图片'); return }
  await request.post('/api/attendance/makeup', makeup)
  ElMessage.success('补卡申请已提交')
  makeupDlg.value = false
  load()
}
async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/attendance/page', { params: { page: 1, size: 30, mine: true } })
    rows.value = d.list || []
    const today = new Date().toISOString().slice(0, 10)
    stat.value.normal = rows.value.filter((r) => r.status === 'NORMAL').length
    stat.value.late = rows.value.filter((r) => r.status === 'LATE').length
    stat.value.early = rows.value.filter((r) => r.status === 'EARLY').length
    stat.value.absent = rows.value.filter((r) => r.status === 'ABSENT').length
    stat.value.hours = rows.value.reduce((s, r) => s + Number(r.validHours || 0), 0).toFixed(1)
    const sh = await request.get('/api/shift/page', { params: { page: 1, size: 50, mine: true, weekStart: startOfWeek(new Date()) } })
    shift.value = (sh.list || []).find((x) => x.shiftDate === today) || (sh.list || [])[0] || null
  } finally { loading.value = false }
}
function startOfWeek(d) {
  const x = new Date(d); const day = (x.getDay() + 6) % 7
  x.setDate(x.getDate() - day)
  return x.toISOString().slice(0, 10)
}
onMounted(load)
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 16px; }
.kv { display: grid; grid-template-columns: 88px 1fr; gap: 8px; font-size: 13px; }
.kv span { color: var(--text3); }
.code { font-size: 26px; letter-spacing: 10px; font-weight: 600; color: var(--primary); background: #F1F7FA;
  border: 1px dashed var(--border); border-radius: 6px; text-align: center; padding: 16px 0; }
@media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
</style>
""")

add("src/views/AttendanceReview.vue", """<template>
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
""")

add("src/views/HourReview.vue", """<template>
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
""")

add("src/views/MyHours.vue", """<template>
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
""")

add("src/views/Subsidy.vue", """<template>
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
""")

add("src/views/PayList.vue", """<template>
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
""")

print("views2", len(F))
