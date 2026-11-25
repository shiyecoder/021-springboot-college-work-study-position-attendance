# -*- coding: utf-8 -*-
"""视图组 1：工作台、岗位广场/详情、我的申请、岗位管理、岗位审批、录用审核台。"""
import pathlib

F = {}


def add(rel, code):
    F[rel] = code.strip() + "\n"


add("src/views/Dashboard.vue", """<template>
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
""")

add("src/views/PostSquare.vue", """<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="kw" placeholder="岗位名称 / 编号" clearable @keyup.enter="reload" />
          <el-select v-model="deptId" placeholder="全部用工部门" clearable>
            <el-option v-for="o in depts" :key="o.id" :label="o.orgName" :value="o.id" />
          </el-select>
          <el-select v-model="postType" placeholder="全部岗位类型" clearable>
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <span class="muted" style="margin-left:auto">共 {{ total }} 个岗位在招</span>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="post" v-for="p in rows" :key="p.id">
        <div class="cover"><img :src="p.coverImage" alt="" /></div>
        <div class="body">
          <div class="ttl">
            <b>{{ p.postName }}</b>
            <span class="tag">{{ p.postType }}</span>
          </div>
          <div class="meta num">{{ p.postNo }} · {{ p.deptName }}</div>
          <div class="kv">
            <span>招聘 {{ p.recruitNum }} 人（已录 {{ p.hiredNum }}）</span>
            <span>{{ p.hourRate }} 元/时</span>
          </div>
          <div class="meta">{{ p.workPeriod }}</div>
          <div class="meta">要求：{{ p.abilityReq || '无特殊要求' }}</div>
          <div class="ops">
            <el-button link type="primary" @click="$router.push('/post/' + p.id)">查看详情</el-button>
            <el-button type="primary" size="small" @click="openApply(p)">申请岗位</el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="!rows.length" description="当前筛选条件下无岗位，清空筛选后再试" style="grid-column:1/-1" />
    </div>
    <div style="display:flex;justify-content:flex-end">
      <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                     v-model:current-page="page" v-model:page-size="size" :page-sizes="[10, 20, 50]"
                     @current-change="load" @size-change="reload" />
    </div>

    <el-drawer v-model="drawer" title="提交岗位申请" size="480px">
      <el-form label-width="96px" v-if="cur">
        <el-form-item label="目标岗位"><b>{{ cur.postName }}</b></el-form-item>
        <el-form-item label="用工部门">{{ cur.deptName }}</el-form-item>
        <el-form-item label="申请理由" required>
          <el-input v-model="form.applyReason" type="textarea" :rows="4" placeholder="不少于 10 个字，说明自身条件与可投入时间" />
        </el-form-item>
        <el-form-item label="可用时段" required>
          <el-input v-model="form.availableTime" placeholder="如：周一至周五 18:00 后，周六全天" />
        </el-form-item>
        <el-form-item label="个人简历">
          <el-upload :show-file-list="false" :http-request="uploadResume">
            <el-button size="small">上传简历/证明</el-button>
          </el-upload>
          <span v-if="form.resumePath" class="muted" style="margin-left:10px">{{ form.resumePath }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">提交申请</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const kw = ref(''); const deptId = ref(''); const postType = ref('')
const depts = ref([]); const types = ['助管', '助教', '助研', '志愿服务']
const drawer = ref(false); const cur = ref(null); const saving = ref(false)
const form = reactive({ applyReason: '', availableTime: '', resumePath: '' })

async function load() {
  const d = await request.get('/api/post/square', { params: { page: page.value, size: size.value, kw: kw.value, deptId: deptId.value, postType: postType.value } })
  rows.value = d.list || []
  total.value = d.total || 0
}
function reload() { page.value = 1; load() }
function reset() { kw.value = ''; deptId.value = ''; postType.value = ''; reload() }

function openApply(p) {
  cur.value = p
  form.applyReason = ''; form.availableTime = ''; form.resumePath = ''
  drawer.value = true
}
async function uploadResume(opt) {
  const fd = new FormData()
  fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.resumePath = d.path
  ElMessage.success('上传成功')
}
async function submit() {
  if (form.applyReason.trim().length < 10) { ElMessage.warning('申请理由不少于 10 个字'); return }
  if (!form.availableTime.trim()) { ElMessage.warning('请填写可用时段'); return }
  saving.value = true
  try {
    await request.post('/api/application', { postId: cur.value.id, ...form })
    ElMessage.success('申请已提交，等待用工部门筛选')
    drawer.value = false
    load()
  } finally { saving.value = false }
}
onMounted(async () => {
  const orgs = await request.get('/api/user/orgs')
  depts.value = (orgs || []).filter((o) => o.orgType === 'DEPT')
  load()
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.post { background: #fff; border: 1px solid var(--border); border-radius: 7px; overflow: hidden; display: flex; flex-direction: column; }
.cover { height: 132px; background: #E7EEF2; }
.cover img { width: 100%; height: 100%; object-fit: cover; }
.body { padding: 12px 14px 14px; }
.ttl { display: flex; align-items: center; gap: 8px; }
.ttl b { font-size: 14px; }
.tag { font-size: 11px; padding: 1px 7px; border-radius: 10px; color: #2F6B8A; background: #F1F7FA; }
.meta { font-size: 12px; color: var(--text3); margin-top: 4px; }
.kv { display: flex; justify-content: space-between; font-size: 13px; color: var(--text2); margin-top: 8px; }
.ops { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--border); }
@media (max-width: 1100px) { .grid { grid-template-columns: repeat(2, 1fr); } }
</style>
""")

add("src/views/PostDetail.vue", """<template>
  <div v-if="p">
    <div class="card">
      <div class="card-h">
        <h2>{{ p.postName }}</h2>
        <el-tag :type="statusType(p.status)" effect="light">{{ statusText(p.status) }}</el-tag>
        <div style="margin-left:auto" class="muted">编号 {{ p.postNo }} · 责任人 {{ p.teacherName }} · 更新 {{ formatTime(p.updateTime) }}</div>
      </div>
      <div class="card-b">
        <div class="top-info">
          <img :src="p.coverImage" class="cover" alt="" />
          <div class="fields">
            <div><label>用工部门</label><span>{{ p.deptName }}</span></div>
            <div><label>岗位类型</label><span>{{ p.postType }}</span></div>
            <div><label>工作地点</label><span>{{ p.workPlace }}</span></div>
            <div><label>招聘人数</label><span class="num">{{ p.recruitNum }} 人（已录 {{ p.hiredNum }}）</span></div>
            <div><label>时薪标准</label><span class="num">{{ p.hourRate }} 元/时</span></div>
            <div><label>工作时段</label><span>{{ p.workPeriod }}</span></div>
            <div><label>能力要求</label><span>{{ p.abilityReq || '-' }}</span></div>
            <div><label>预算</label><span class="num">{{ money(p.budget) }}</span></div>
          </div>
        </div>
        <div class="hint" style="margin-top:16px">{{ p.postDesc }}</div>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>业务时间轴</h2></div>
      <div class="card-b">
        <div class="timeline">
          <div class="tl" v-for="t in p.timeline" :key="t.id">
            <div class="dot"></div>
            <div class="txt"><b>{{ t.action }}{{ t.toStatus ? ' → ' + statusText(t.toStatus) : '' }}</b>
              <span>{{ formatTime(t.createTime) }} · {{ t.operator }}{{ t.reason ? ' · ' + t.reason : '' }}</span></div>
          </div>
          <el-empty v-if="!p.timeline || !p.timeline.length" description="暂无流转记录" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import { formatTime, money, statusText, statusType } from '@/utils/format'

const route = useRoute()
const p = ref(null)
onMounted(async () => { p.value = await request.get('/api/post/' + route.params.id) })
</script>

<style scoped>
.top-info { display: flex; gap: 22px; }
.cover { width: 260px; height: 176px; border-radius: 7px; object-fit: cover; background: #E7EEF2; }
.fields { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px 24px; flex: 1; font-size: 13px; }
.fields label { color: var(--text3); display: inline-block; width: 76px; }
</style>
""")

add("src/views/MyApply.vue", """<template>
  <div>
    <div class="card">
      <div class="card-h">
        <h2>我的岗位申请</h2>
        <el-radio-group v-model="status" size="small" style="margin-left:16px" @change="reload">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="SCREENING">待筛选</el-radio-button>
          <el-radio-button label="INTERVIEW">待面试</el-radio-button>
          <el-radio-button label="EMPLOYED">已录用</el-radio-button>
          <el-radio-button label="REJECTED">已驳回</el-radio-button>
        </el-radio-group>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="applyNo" label="申请编号" min-width="130" />
        <el-table-column prop="postName" label="岗位" min-width="200" />
        <el-table-column prop="deptName" label="用工部门" min-width="120" />
        <el-table-column label="匹配分" width="96"><template #default="{ row }"><span class="num">{{ row.matchScore ?? '-' }}</span></template></el-table-column>
        <el-table-column label="面试时间" min-width="160"><template #default="{ row }">{{ formatTime(row.interviewTime) }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="申请时间" min-width="160"><template #default="{ row }">{{ formatTime(row.createTime) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="['SCREENING','INTERVIEW'].includes(row.status)" link type="danger" @click="withdraw(row)">撤回</el-button>
            <el-button link type="primary" @click="$router.push('/post/' + row.postId)">详情</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，清空筛选或到岗位广场申请" /></template>
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
const status = ref(''); const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/application/page', { params: { page: page.value, size: size.value, status: status.value, mine: true } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
async function withdraw(row) {
  await ElMessageBox.confirm('撤回后如需再申请需重新提交，确认撤回？', '撤回确认', { type: 'warning' })
  await request.post('/api/application/' + row.id + '/withdraw')
  ElMessage.success('已撤回')
  load()
}
onMounted(load)
</script>
""")

add("src/views/PostList.vue", """<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="q.kw" placeholder="岗位名称 / 编号" clearable @keyup.enter="reload" />
          <el-select v-model="q.postType" placeholder="岗位类型" clearable>
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
          <el-select v-model="q.status" placeholder="招聘状态" clearable>
            <el-option v-for="s in statusList" :key="s" :label="statusText(s)" :value="s" />
          </el-select>
          <el-input v-model="q.workPeriod" placeholder="工作时段" clearable />
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" plain style="margin-left:auto" @click="openAdd">新建岗位</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>岗位列表</h2><span class="muted" style="margin-left:auto">共 {{ total }} 条</span></div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column label="封面" width="86"><template #default="{ row }"><img class="thumb" :src="row.coverImage" alt="" /></template></el-table-column>
        <el-table-column prop="postNo" label="岗位编号" min-width="130" />
        <el-table-column prop="postName" label="岗位名称" min-width="190" />
        <el-table-column prop="deptName" label="用工部门" min-width="110" />
        <el-table-column prop="postType" label="类型" width="90" />
        <el-table-column label="人数" width="96"><template #default="{ row }"><span class="num">{{ row.hiredNum }}/{{ row.recruitNum }}</span></template></el-table-column>
        <el-table-column label="时薪" width="88"><template #default="{ row }"><span class="num">{{ row.hourRate }}</span></template></el-table-column>
        <el-table-column prop="workPeriod" label="工作时段" min-width="150" />
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="更新时间" min-width="160"><template #default="{ row }">{{ formatTime(row.updateTime) }}</template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'DRAFT' || row.status === 'REJECTED'" link type="primary" @click="trans(row, 'PENDING', '提交审核')">提交</el-button>
            <el-button v-if="row.status === 'RECRUITING'" link type="primary" @click="trans(row, 'FINISHED', '结束岗位')">结束</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，清空筛选或新建岗位" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10,20,50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="form.id ? '编辑岗位' : '新建岗位'" size="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="岗位名称" required><el-input v-model="form.postName" /></el-form-item>
        <el-form-item label="岗位类型" required>
          <el-select v-model="form.postType" style="width:220px">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作地点" required><el-input v-model="form.workPlace" /></el-form-item>
        <el-form-item label="招聘人数" required><el-input-number v-model="form.recruitNum" :min="1" :max="99" style="width:180px" /></el-form-item>
        <el-form-item label="时薪标准" required><el-input-number v-model="form.hourRate" :min="1" :precision="2" style="width:180px" /></el-form-item>
        <el-form-item label="工作时段"><el-input v-model="form.workPeriod" maxlength="100" show-word-limit placeholder="如：工作日 18:00-22:00" /></el-form-item>
        <el-form-item label="能力要求"><el-input v-model="form.abilityReq" maxlength="100" show-word-limit /></el-form-item>
        <el-form-item label="预算"><el-input-number v-model="form.budget" :min="0" :precision="2" style="width:200px" /></el-form-item>
        <el-form-item label="岗位职责"><el-input v-model="form.postDesc" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="岗位附图">
          <el-upload :show-file-list="false" :http-request="uploadCover">
            <img v-if="form.coverImage" :src="form.coverImage" class="thumb" alt="" />
            <el-button v-else size="small">上传图片</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const loading = ref(false); const saving = ref(false); const drawer = ref(false)
const types = ['助管', '助教', '助研', '志愿服务']
const statusList = ['DRAFT', 'PENDING', 'RECRUITING', 'FULL', 'FINISHED', 'REJECTED']
const q = reactive({ kw: '', postType: '', status: '', workPeriod: '' })
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/post/page', { params: { page: page.value, size: size.value, ...q } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { q.kw = ''; q.postType = ''; q.status = ''; q.workPeriod = ''; reload() }

function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, { recruitNum: 1, hourRate: 22, postType: '助管', postDesc: '' })
  drawer.value = true
}
function openEdit(row) {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, JSON.parse(JSON.stringify(row)))
  drawer.value = true
}
async function uploadCover(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.coverImage = d.path
}
async function save() {
  saving.value = true
  try {
    if (form.id) await request.put('/api/post/' + form.id, form)
    else await request.post('/api/post', form)
    ElMessage.success('保存成功')
    drawer.value = false
    load()
  } finally { saving.value = false }
}
async function trans(row, to, title) {
  const { value } = await ElMessageBox.prompt('请填写原因（不少于 5 个字）', title, { inputPlaceholder: '变更原因' })
  await request.post('/api/post/' + row.id + '/transition', { toStatus: to, reason: value })
  ElMessage.success('操作成功')
  load()
}
async function remove(row) {
  await ElMessageBox.confirm('删除后不可恢复，确认删除该岗位？', '删除确认', { type: 'warning' })
  await request.delete('/api/post/' + row.id)
  ElMessage.success('已删除')
  load()
}
onMounted(load)
</script>
""")

add("src/views/PostAudit.vue", """<template>
  <div>
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="kpi"><div class="k">待审核</div><div class="v num">{{ stat.pending }}</div><div class="d">含超 3 天 1 个</div></div>
      <div class="kpi"><div class="k">在招岗位</div><div class="v num">{{ stat.recruiting }}</div><div class="d">覆盖多个部门</div></div>
      <div class="kpi"><div class="k">已满额</div><div class="v num">{{ stat.full }}</div><div class="d">可结束或扩招</div></div>
      <div class="kpi"><div class="k">草稿</div><div class="v num">{{ stat.draft }}</div><div class="d">部门未提交</div></div>
    </div>
    <div class="card">
      <div class="card-h">
        <h2>待审核岗位</h2>
        <el-select v-model="deptId" placeholder="全部部门" clearable size="small" style="width:180px;margin-left:12px" @change="reload">
          <el-option v-for="o in depts" :key="o.id" :label="o.orgName" :value="o.id" />
        </el-select>
        <span class="muted" style="margin-left:auto">审批需核对必要性、预算、安全风险与人数</span>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="postNo" label="岗位编号" min-width="130" />
        <el-table-column prop="postName" label="岗位名称" min-width="190" />
        <el-table-column prop="deptName" label="用工部门" min-width="110" />
        <el-table-column label="人数" width="80"><template #default="{ row }"><span class="num">{{ row.recruitNum }}</span></template></el-table-column>
        <el-table-column label="预算" width="120"><template #default="{ row }"><span class="num">{{ money(row.budget) }}</span></template></el-table-column>
        <el-table-column prop="teacherName" label="指导老师" width="100" />
        <el-table-column label="提交时间" min-width="160"><template #default="{ row }">{{ formatTime(row.updateTime) }}</template></el-table-column>
        <el-table-column label="状态" width="96"><template #default="{ row }"><el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="openAudit(row)">审批</el-button></template>
        </el-table-column>
        <template #empty><el-empty description="当前没有待审核岗位" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:12px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="size" @current-change="load" />
      </div>
    </div>

    <el-drawer v-model="drawer" title="岗位审批" size="480px">
      <div v-if="cur">
        <div class="sum">
          <div><b>{{ cur.postName }}</b> <span class="muted">{{ cur.postNo }}</span></div>
          <div class="muted">{{ cur.deptName }} · {{ cur.teacherName }} · {{ cur.workPeriod }}</div>
          <div class="num" style="margin-top:6px">招聘 {{ cur.recruitNum }} 人 · 时薪 {{ cur.hourRate }} 元 · 预算 {{ money(cur.budget) }}</div>
        </div>
        <el-form label-width="92px" style="margin-top:16px">
          <el-form-item label="必要性">
            <div class="hint">{{ cur.postDesc }}</div>
          </el-form-item>
          <el-form-item label="审批意见">
            <el-input v-model="reason" type="textarea" :rows="3" placeholder="驳回时必须填写不少于 5 个字的原因" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="danger" plain @click="act('REJECTED')">驳回</el-button>
        <el-button type="primary" @click="act('RECRUITING')">通过并发布</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, money, statusText, statusType } from '@/utils/format'

const rows = ref([]); const total = ref(0); const page = ref(1); const size = ref(10)
const loading = ref(false); const drawer = ref(false); const cur = ref(null); const reason = ref('')
const deptId = ref(''); const depts = ref([])
const stat = ref({ pending: 0, recruiting: 0, full: 0, draft: 0 })

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/post/page', { params: { page: page.value, size: size.value, status: 'PENDING', deptId: deptId.value } })
    rows.value = d.list || []; total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function openAudit(row) { cur.value = row; reason.value = ''; drawer.value = true }
async function act(to) {
  if (to === 'REJECTED' && reason.value.trim().length < 5) { ElMessage.warning('驳回必须填写不少于 5 个字的原因'); return }
  await request.post('/api/post/' + cur.value.id + '/transition', { toStatus: to, reason: reason.value || '审核通过，同意发布' })
  ElMessage.success('操作成功')
  drawer.value = false
  load(); loadStat()
}
async function loadStat() {
  for (const s of ['PENDING', 'RECRUITING', 'FULL', 'DRAFT']) {
    const d = await request.get('/api/post/page', { params: { page: 1, size: 1, status: s } })
    stat.value[({ PENDING: 'pending', RECRUITING: 'recruiting', FULL: 'full', DRAFT: 'draft' })[s]] = d.total
  }
}
onMounted(async () => {
  depts.value = (await request.get('/api/user/orgs') || []).filter((o) => o.orgType === 'DEPT')
  load(); loadStat()
})
</script>

<style scoped>
.sum { background: #F6F9FA; border-radius: 6px; padding: 12px 14px; font-size: 13px; line-height: 1.9; }
</style>
""")

add("src/views/Employment.vue", """<template>
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
""")

print("views1", len(F))
