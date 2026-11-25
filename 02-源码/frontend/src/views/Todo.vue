<template>
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
