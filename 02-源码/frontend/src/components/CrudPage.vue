<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="kw" :placeholder="'搜索' + cfg.title" clearable @keyup.enter="reload" />
          <el-select v-if="cfg.statusOptions" v-model="status" placeholder="全部状态" clearable>
            <el-option v-for="o in cfg.statusOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button v-if="!cfg.readonly" type="primary" plain style="margin-left:auto" @click="openAdd">
            <el-icon><Plus /></el-icon>新建
          </el-button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h">
        <h2>{{ cfg.title }}</h2>
        <div style="margin-left:auto" class="muted">共 {{ total }} 条</div>
      </div>
      <el-table :data="rows" v-loading="loading" border style="width:100%">
        <el-table-column v-for="c in cfg.columns" :key="c.prop" :prop="c.prop" :label="c.label"
                         :min-width="c.minWidth || 110" :align="c.align || 'left'" show-overflow-tooltip>
          <template #default="{ row }">
            <img v-if="c.type === 'image'" class="thumb" :src="row[c.prop]" alt="" />
            <el-tag v-else-if="c.type === 'status'" :type="statusType(row[c.prop])" effect="light">
              {{ statusText(row[c.prop]) }}
            </el-tag>
            <span v-else-if="c.type === 'time'" class="num">{{ formatTime(row[c.prop]) }}</span>
            <span v-else-if="c.type === 'date'" class="num">{{ formatDate(row[c.prop]) }}</span>
            <span v-else-if="c.type === 'num'" class="num">{{ row[c.prop] ?? '-' }}</span>
            <span v-else>{{ row[c.prop] ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="!cfg.readonly" label="操作" :width="cfg.rowWidth || 150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
            <!-- 页面自定义的行内操作（如角色分配菜单） -->
            <slot name="row-actions" :row="row" />
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，可清空筛选或新建" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size"
                       :page-sizes="[10, 20, 50]" @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-dialog v-model="visible" :title="(form.id ? '编辑' : '新建') + cfg.title" width="640px">
      <el-form :model="form" label-width="110px">
        <el-form-item v-for="f in cfg.fields" :key="f.prop" :label="f.label" :required="f.required">
          <el-select v-if="f.type === 'select'" v-model="form[f.prop]" style="width:220px">
            <el-option v-for="o in f.options" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
          <el-input v-else-if="f.type === 'textarea'" v-model="form[f.prop]" type="textarea" :rows="3" />
          <el-date-picker v-else-if="f.type === 'date'" v-model="form[f.prop]" type="date"
                          value-format="YYYY-MM-DD" style="width:200px" />
          <el-input-number v-else-if="f.type === 'number'" v-model="form[f.prop]" :precision="f.precision || 0"
                           style="width:200px" />
          <el-upload v-else-if="f.type === 'image'" :show-file-list="false" :http-request="(o) => doUpload(o, f.prop)">
            <img v-if="form[f.prop]" class="thumb" style="width:96px;height:72px" :src="form[f.prop]" alt="" />
            <el-button v-else size="small">上传图片</el-button>
          </el-upload>
          <el-input v-else v-model="form[f.prop]" style="width:320px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, formatDate, statusText, statusType } from '@/utils/format'

const props = defineProps({ cfg: { type: Object, required: true } })
const cfg = props.cfg
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const kw = ref('')
const status = ref('')
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get(cfg.url + '/page', {
      params: { page: page.value, size: size.value, kw: kw.value, status: status.value }
    })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { kw.value = ''; status.value = ''; reload() }

function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  cfg.fields.forEach((f) => { form[f.prop] = f.default ?? null })
  visible.value = true
}
function openEdit(row) {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, JSON.parse(JSON.stringify(row)))
  visible.value = true
}
async function save() {
  saving.value = true
  try {
    if (form.id) await request.put(cfg.url + '/' + form.id, form)
    else await request.post(cfg.url, form)
    ElMessage.success('保存成功')
    visible.value = false
    load()
  } finally { saving.value = false }
}
async function remove(row) {
  await ElMessageBox.confirm('删除后不可恢复，确认删除该记录？', '删除确认', { type: 'warning' })
  await request.delete(cfg.url + '/' + row.id)
  ElMessage.success('已删除')
  load()
}
async function doUpload(opt, prop) {
  const fd = new FormData()
  fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form[prop] = d.path
  ElMessage.success('上传成功')
}
onMounted(load)
defineExpose({ reload })
</script>
