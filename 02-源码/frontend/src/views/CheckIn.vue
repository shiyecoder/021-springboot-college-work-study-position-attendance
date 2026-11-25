<template>
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
