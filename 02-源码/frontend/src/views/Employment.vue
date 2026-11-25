<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-select v-model="postId" placeholder="选择岗位查看候选人" style="width:260px" @change="load">
            <el-option v-for="p in posts" :key="p.id" :label="p.postName + '（' + p.deptName + '）'" :value="p.id" />
          </el-select>
          <el-button @click="load">刷新</el-button>
          <span class="muted" style="margin-left:auto">录用人数由后端硬校验，超员直接拒绝</span>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>候选人对比</h2><span class="muted" style="margin-left:auto">共 {{ rows.length }} 人</span></div>
        <el-table :data="rows" v-loading="loading" border>
          <el-table-column prop="rank" label="#" width="52" />
          <el-table-column prop="studentName" label="学生" min-width="96" />
          <el-table-column prop="college" label="学院" min-width="130" />
          <el-table-column label="困难等级" width="110"><template #default="{ row }">{{ DIFFICULTY_TEXT[row.difficultyLevel] || '-' }}</template></el-table-column>
          <el-table-column label="匹配分" width="92"><template #default="{ row }"><span class="num">{{ row.matchScore ?? '-' }}</span></template></el-table-column>
          <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
          <el-table-column label="操作" width="190" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="evaluate(row)">计算</el-button>
              <el-button v-if="row.status !== 'EMPLOYED'" link type="primary" @click="employ(row)">录用</el-button>
              <el-button v-if="['SCREENING','INTERVIEW'].includes(row.status)" link type="danger" @click="reject(row)">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="card">
        <div class="card-h"><h2>公平匹配参考分</h2>
          <el-tag v-if="exp" :type="exp.score.grade === 'A' ? 'success' : exp.score.grade === 'B' ? 'primary' : 'warning'" effect="light" style="margin-left:auto">{{ exp.suggestion }}</el-tag>
        </div>
        <div class="card-b" v-if="exp">
          <div class="num" style="font-size:30px;font-weight:600;color:var(--primary)">
            {{ exp.score.totalScore }}<span class="muted" style="font-size:13px"> / 100 · {{ exp.score.grade }} 级</span>
          </div>
          <div class="muted" style="margin-bottom:14px">{{ exp.studentName }} · 规则 {{ exp.score.ruleVersion }}</div>
          <div class="score-row" v-for="i in exp.items" :key="i.name">
            <span class="nm">{{ i.name }}</span>
            <div class="bar2"><i :style="{ width: i.score + '%' }"></i></div>
            <span class="num" style="width:74px;text-align:right">{{ i.score }} × {{ i.weight }}%</span>
          </div>
          <div class="hint" style="margin-top:12px;line-height:1.9">
            <b>主要影响因素：</b>{{ exp.pros.join('；') }}<br />
            <b>未满足条件：</b>{{ exp.cons.join('；') }}<br />
            <b>可改进项：</b>{{ exp.improve.join('；') }}
          </div>
          <div style="margin-top:12px">
            <el-button size="small" @click="openAdjust(exp.score)">人工修正</el-button>
          </div>
        </div>
        <el-empty v-else description="选择候选人后点击「计算」查看依据" :image-size="70" />
      </div>
    </div>

    <el-dialog v-model="adjustDlg" title="人工修正结果" width="460px">
      <el-form label-width="92px">
        <el-form-item label="原始结果"><span class="num">{{ adjust.origin }} 分 · {{ adjust.originGrade }} 级</span></el-form-item>
        <el-form-item label="调整后等级">
          <el-select v-model="adjust.grade" style="width:160px">
            <el-option v-for="g in ['A','B','C','D']" :key="g" :label="g" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="修正原因" required><el-input v-model="adjust.reason" type="textarea" :rows="3" placeholder="不少于 5 个字，原始计算结果不会被覆盖" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDlg = false">取消</el-button>
        <el-button type="primary" @click="saveAdjust">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { statusText, statusType, DIFFICULTY_TEXT } from '@/utils/format'

const posts = ref([]); const postId = ref('')
const rows = ref([]); const loading = ref(false); const exp = ref(null)
const adjustDlg = ref(false)
const adjust = reactive({ id: null, origin: 0, originGrade: '', grade: 'B', reason: '' })

async function load() {
  if (!postId.value) return
  loading.value = true
  try {
    rows.value = await request.get('/api/application/compare', { params: { postId: postId.value } })
  } finally { loading.value = false }
}
async function evaluate(row) {
  exp.value = await request.post('/api/match/evaluate', { applicationId: String(row.id) })
  load()
}
function openAdjust(sc) {
  adjust.id = sc.id; adjust.origin = sc.totalScore; adjust.originGrade = sc.grade; adjust.grade = sc.grade; adjust.reason = ''
  adjustDlg.value = true
}
async function saveAdjust() {
  if (adjust.reason.trim().length < 5) { ElMessage.warning('修正原因不少于 5 个字'); return }
  await request.post('/api/match/score/' + adjust.id + '/adjust', { grade: adjust.grade, reason: adjust.reason })
  ElMessage.success('已保存人工修正')
  adjustDlg.value = false
}
async function employ(row) {
  const { value } = await ElMessageBox.prompt('录用原因（可留空）', '确认录用 ' + row.studentName, { inputPlaceholder: '如：面试通过，技能匹配' })
  await request.post('/api/application/' + row.id + '/employ', { remark: value })
  ElMessage.success('已录用')
  load()
}
async function reject(row) {
  const { value } = await ElMessageBox.prompt('请填写驳回原因（不少于 5 个字）', '驳回申请', { inputPlaceholder: '驳回原因' })
  await request.post('/api/application/' + row.id + '/reject', { reason: value })
  ElMessage.success('已驳回')
  load()
}
onMounted(async () => {
  const d = await request.get('/api/post/page', { params: { page: 1, size: 50 } })
  posts.value = (d.list || []).filter((p) => ['RECRUITING', 'FULL'].includes(p.status))
  if (posts.value.length) { postId.value = posts.value[0].id; load() }
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.25fr 1fr; gap: 16px; }
@media (max-width: 1280px) { .grid { grid-template-columns: 1fr; } }
</style>
