<template>
  <div>
    <div class="kpi-grid">
      <div class="kpi" v-for="k in kpis" :key="k.k">
        <div class="k">{{ k.k }}</div>
        <div class="v num">{{ k.v }}</div>
        <div class="d">{{ k.d }}</div>
      </div>
    </div>
    <div class="chart-grid" style="margin-bottom:12px">
      <div class="chart-box"><h3>近 6 个月申请趋势</h3><div ref="c1" class="chart"></div></div>
      <div class="chart-box"><h3>岗位状态分布</h3><div ref="c2" class="chart"></div></div>
      <div class="chart-box"><h3>推荐结果分布</h3><div ref="c3" class="chart"></div></div>
    </div>
    <div class="chart-grid">
      <div class="chart-box"><h3>用工部门工时排行（本月）</h3><div ref="c4" class="chart"></div></div>
      <div class="chart-box"><h3>考勤异常构成</h3><div ref="c5" class="chart"></div></div>
      <div class="chart-box" style="padding:12px 16px">
        <h3>待我处理</h3>
        <div v-for="t in todos" :key="t.no" class="todo" @click="go(t)">
          <span class="tag" :class="t.cls">{{ t.type }}</span>
          <b>{{ t.title }}</b>
          <span class="muted">{{ t.time }}</span>
        </div>
        <el-empty v-if="!todos.length" description="暂无待办" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { statusText, money, formatTime } from '@/utils/format'

const router = useRouter()
const c1 = ref(); const c2 = ref(); const c3 = ref(); const c4 = ref(); const c5 = ref()
const kpis = ref([])
const todos = ref([])
const C = ['#173B57', '#287271', '#2F6B8A', '#8A99A5', '#7FB2C9']

function chart(el, opt) {
  const inst = echarts.init(el)
  inst.setOption(opt)
  return inst
}

async function load() {
  const s = await request.get('/api/dashboard/stats')
  kpis.value = [
    { k: '在办岗位', v: s.postCount, d: '含招聘中与已满额' },
    { k: '累计申请', v: s.applyCount, d: '全部学期' },
    { k: '录用率', v: s.employRate, d: '录用 / 申请' },
    { k: '本月完成工时', v: s.finishHours, d: '有效工时合计' },
    { k: '缺勤率', v: s.absentRate, d: '缺勤 / 全部考勤' },
    { k: '补贴总额', v: money(s.subsidyAmount), d: '已生成批次合计' }
  ]
  const c = await request.get('/api/dashboard/charts')

  await nextTick()
  chart(c1.value, {
    grid: { left: 34, right: 12, top: 18, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: c.months.map((m) => m.slice(5) + '月'), axisLine: { lineStyle: { color: '#DFE7EC' } }, axisLabel: { color: '#8A99A5', fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F5' } }, axisLabel: { color: '#8A99A5', fontSize: 11 } },
    series: [{ type: 'line', smooth: true, data: c.trend, symbolSize: 6, itemStyle: { color: C[2] }, areaStyle: { color: 'rgba(47,107,138,.10)' } }]
  })
  chart(c2.value, {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 11, color: '#5A6B77' } },
    series: [{
      type: 'pie', radius: ['46%', '68%'], center: ['50%', '44%'],
      data: c.statusDist.map((d, i) => ({ name: statusText(d.name), value: d.value, itemStyle: { color: C[i % 5] } })),
      label: { show: false }
    }]
  })
  chart(c3.value, {
    grid: { left: 30, right: 12, top: 18, bottom: 24 },
    tooltip: {},
    xAxis: { type: 'category', data: c.gradeDist.map((d) => d.name + ' 级'), axisLabel: { color: '#8A99A5', fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F5' } }, axisLabel: { color: '#8A99A5', fontSize: 11 } },
    series: [{ type: 'bar', barWidth: 22, data: c.gradeDist.map((d) => d.value), itemStyle: { color: C[1], borderRadius: [4, 4, 0, 0] } }]
  })
  chart(c4.value, {
    grid: { left: 78, right: 20, top: 14, bottom: 20 },
    tooltip: {},
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#EDF2F5' } }, axisLabel: { color: '#8A99A5', fontSize: 11 } },
    yAxis: { type: 'category', data: c.deptRank.map((d) => d.name).reverse(), axisLabel: { color: '#5A6B77', fontSize: 11 } },
    series: [{ type: 'bar', barWidth: 14, data: c.deptRank.map((d) => d.value).reverse(), itemStyle: { color: C[2], borderRadius: [0, 3, 3, 0] } }]
  })
  chart(c5.value, {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 11, color: '#5A6B77' } },
    series: [{
      type: 'pie', radius: ['46%', '68%'], center: ['50%', '44%'],
      data: c.attDist.map((d, i) => ({ name: statusText(d.name), value: d.value, itemStyle: { color: C[(i + 2) % 5] } })),
      label: { show: false }
    }]
  })

  // 待办：待审岗位 + 待处理申请
  const audit = await request.get('/api/post/page', { params: { page: 1, size: 3, status: 'PENDING' } })
  const list = []
  ;(audit.list || []).forEach((p) => list.push({ type: '岗位审批', cls: 't-wa', title: p.postName, no: p.postNo, time: formatTime(p.updateTime), to: '/post-audit' }))
  const apps = await request.get('/api/application/page', { params: { page: 1, size: 3, status: 'SCREENING' } })
  ;(apps.list || []).forEach((a) => list.push({ type: '申请待筛选', cls: 't-pr', title: a.studentName + ' · ' + a.postName, no: a.applyNo, time: formatTime(a.createTime), to: '/employment' }))
  todos.value = list.slice(0, 4)
}
function go(t) { router.push(t.to) }
onMounted(load)
</script>

<style scoped>
.todo { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px dashed var(--border); font-size: 13px; cursor: pointer; }
.todo:last-child { border-bottom: none; }
.todo b { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.todo .muted { margin-left: auto; }
.tag { font-size: 11px; padding: 1px 7px; border-radius: 10px; flex: none; }
.t-wa { color: #8A5A00; background: #FDF7E9; }
.t-pr { color: #2F6B8A; background: #F1F7FA; }
</style>
