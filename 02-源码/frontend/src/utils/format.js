/**
 * 全局时间格式化：全系统统一调用，禁止各页面自行拼接
 * @param {string|Date} v 时间值
 * @param {boolean} dateOnly 是否只显示日期
 */
export function formatTime(v, dateOnly = false) {
  if (!v) return '-'
  const s = String(v).replace('T', ' ')
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ ]?(\d{2}):(\d{2}):(\d{2})/)
  if (m) {
    return dateOnly ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}`
  }
  return s
}

export function formatDate(v) {
  return formatTime(v, true)
}

/** 金额：两位小数 + 千分位 */
export function money(v) {
  if (v === null || v === undefined || v === '') return '-'
  return '¥ ' + Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/** 状态字典 → 中文标签 */
export const STATUS_TEXT = {
  // 岗位
  DRAFT: '草稿', PENDING: '待审核', RECRUITING: '招聘中', FULL: '已满额', FINISHED: '已结束', REJECTED: '已驳回',
  // 申请
  SCREENING: '待筛选', INTERVIEW: '待面试', EMPLOYED: '已录用', WITHDRAWN: '已撤回',
  // 考勤
  NORMAL: '正常', LATE: '迟到', EARLY: '早退', ABSENT: '缺勤', LEAVE: '请假', MAKEUP: '补卡', ING: '进行中',
  // 复核
  PASS: '已通过', REJECT: '已驳回', WAIT: '待发放',
  // 工时
  CONFIRMED: '已确认', OVER_LIMIT: '超上限',
  // 补贴
  AUDITING: '待审核', APPROVED: '已审核', PAID: '已发放', FAIL: '发放失败',
  // 排班
  ADJUST: '待调整',
  // 通用
  RUNNING: '进行中', ACCOUNT: '正常', ON: '启用', OFF: '停用', ACTIVE: '生效中', ARCHIVED: '已归档',
  // 评价
  WAIT_STUDENT: '待学生确认', DONE: '已完成',
  // 困难等级
  DIFFICULT_SPECIAL: '特别困难', DIFFICULT: '困难', NONE: '不困难'
}

export function statusText(s) {
  return STATUS_TEXT[s] || s || '-'
}

export function statusType(s) {
  if (['RECRUITING', 'NORMAL', 'PASS', 'CONFIRMED', 'PAID', 'DONE', 'ON', 'ACTIVE', 'EMPLOYED'].includes(s)) return 'success'
  if (['INTERVIEW', 'ING', 'APPROVED', 'RUNNING', 'SCREENING'].includes(s)) return 'primary'
  if (['PENDING', 'AUDITING', 'WAIT', 'WAIT_STUDENT', 'ADJUST', 'OVER_LIMIT', 'MAKEUP', 'LATE'].includes(s)) return 'warning'
  if (['REJECTED', 'ABSENT', 'FAIL', 'EARLY', 'REJECT'].includes(s)) return 'danger'
  return 'info'
}

export const DIFFICULTY_TEXT = {
  DIFFICULT_SPECIAL: '特别困难', DIFFICULT: '困难', NORMAL: '一般', NONE: '不困难'
}
