<template>
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
