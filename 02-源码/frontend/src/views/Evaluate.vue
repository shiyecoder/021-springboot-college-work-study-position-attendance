<template>
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
