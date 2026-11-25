<template>
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
