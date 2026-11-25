<template>
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
