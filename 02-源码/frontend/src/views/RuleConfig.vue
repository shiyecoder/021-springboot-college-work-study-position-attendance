<template>
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
