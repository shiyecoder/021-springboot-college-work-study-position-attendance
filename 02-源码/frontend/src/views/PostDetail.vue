<template>
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
