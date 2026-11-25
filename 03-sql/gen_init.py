# -*- coding: utf-8 -*-
"""生成 NEW-021 高校勤工助学岗位与考勤管理系统的 init.sql（23 张表 + 真实分布测试数据）。"""
import random, pathlib, datetime as dt

random.seed(20261031)
OUT = pathlib.Path(__file__).parent / "init.sql"
PWD = "$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK"  # admin123

HEAD = """-- ============================================================
-- 高校勤工助学岗位与考勤管理系统 数据库初始化脚本
-- MySQL 8 / utf8mb4 ；库名 new_021
-- 说明：所有图片字段均指向项目内真实本地图片 /uploads/seed/<实体>/NN.jpg
-- ============================================================
DROP DATABASE IF EXISTS new_021;
CREATE DATABASE new_021 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE new_021;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
"""

DDL = """
-- 组织（学院 / 用工部门 / 管理中心）
CREATE TABLE sys_org (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  org_name VARCHAR(60) NOT NULL COMMENT '组织名称',
  org_type VARCHAR(20) NOT NULL COMMENT '类型：COLLEGE 学院 / DEPT 用工部门 / CENTER 管理中心',
  parent_id BIGINT DEFAULT 0 COMMENT '上级组织',
  sort INT DEFAULT 0 COMMENT '排序',
  status CHAR(1) DEFAULT '1' COMMENT '1 启用 0 停用',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='组织架构';

CREATE TABLE sys_role (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_code VARCHAR(30) NOT NULL UNIQUE COMMENT '角色编码',
  role_name VARCHAR(40) NOT NULL COMMENT '角色名称',
  data_scope VARCHAR(20) NOT NULL COMMENT '数据范围 SELF/DEPT/ALL',
  sort INT DEFAULT 0,
  status CHAR(1) DEFAULT '1',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='角色';

CREATE TABLE sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录账号',
  password VARCHAR(100) NOT NULL COMMENT 'BCrypt 密文，接口与日志均不返回',
  real_name VARCHAR(40) NOT NULL COMMENT '姓名',
  role_id BIGINT NOT NULL COMMENT '角色',
  org_id BIGINT COMMENT '所属组织',
  student_no VARCHAR(20) COMMENT '学号（学生）',
  phone VARCHAR(20),
  email VARCHAR(60),
  avatar VARCHAR(255) COMMENT '头像相对路径',
  gender CHAR(1) DEFAULT 'U' COMMENT 'M/F/U',
  status CHAR(1) DEFAULT '1' COMMENT '1 启用 0 停用',
  login_fail INT DEFAULT 0 COMMENT '连续登录失败次数',
  lock_until DATETIME NULL COMMENT '锁定截止时间',
  last_login DATETIME NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0,
  KEY idx_user_role (role_id),
  KEY idx_user_org (org_id)
) COMMENT='用户';

CREATE TABLE sys_menu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  parent_id BIGINT DEFAULT 0,
  menu_name VARCHAR(40) NOT NULL,
  menu_type CHAR(1) DEFAULT 'M' COMMENT 'M 菜单 B 按钮',
  path VARCHAR(100) COMMENT '前端路由',
  perms VARCHAR(80) COMMENT '权限标识',
  icon VARCHAR(40),
  sort INT DEFAULT 0,
  visible TINYINT DEFAULT 1 COMMENT '1 显示 0 隐藏（隐藏项不出现在侧边栏）',
  status CHAR(1) DEFAULT '1',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='菜单';

CREATE TABLE sys_role_menu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_id BIGINT NOT NULL,
  menu_id BIGINT NOT NULL,
  UNIQUE KEY uk_role_menu (role_id, menu_id)
) COMMENT='角色菜单';

CREATE TABLE sys_dict (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  dict_type VARCHAR(40) NOT NULL COMMENT '字典类型',
  dict_label VARCHAR(60) NOT NULL,
  dict_value VARCHAR(40) NOT NULL,
  sort INT DEFAULT 0,
  status CHAR(1) DEFAULT '1',
  KEY idx_dict_type (dict_type)
) COMMENT='数据字典';

CREATE TABLE sys_message (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  content VARCHAR(500),
  biz_type VARCHAR(30) COMMENT '业务类型',
  biz_no VARCHAR(40) COMMENT '业务编号，用于详情跳转',
  receiver_id BIGINT NOT NULL,
  read_flag TINYINT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_msg_receiver (receiver_id, read_flag)
) COMMENT='站内消息';

CREATE TABLE sys_attachment (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  biz_type VARCHAR(30) NOT NULL COMMENT '业务类型 STUDENT_PROOF/POST_DOC/ATTENDANCE',
  biz_no VARCHAR(40) COMMENT '业务编号',
  file_name VARCHAR(120) NOT NULL COMMENT '原始文件名',
  file_path VARCHAR(255) NOT NULL COMMENT '相对路径',
  file_size BIGINT DEFAULT 0,
  uploader_id BIGINT,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_att_biz (biz_type, biz_no)
) COMMENT='附件元数据';

CREATE TABLE sys_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT, user_name VARCHAR(40),
  module VARCHAR(40), action VARCHAR(60), method VARCHAR(200),
  params VARCHAR(1000), ip VARCHAR(40), cost_ms INT,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_log_time (create_time)
) COMMENT='操作日志';

CREATE TABLE semester (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  term_name VARCHAR(40) NOT NULL,
  start_date DATE NOT NULL, end_date DATE NOT NULL,
  month_hour_limit DECIMAL(6,1) DEFAULT 40.0 COMMENT '学生月度工时上限',
  status VARCHAR(20) DEFAULT 'RUNNING' COMMENT 'RUNNING/FINISHED',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='学期';

CREATE TABLE subsidy_standard (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  semester_id BIGINT NOT NULL,
  hour_rate DECIMAL(8,2) NOT NULL COMMENT '每小时标准（元）',
  month_hour_limit DECIMAL(6,1) NOT NULL,
  special_factor DECIMAL(4,2) DEFAULT 1.00 COMMENT '特殊岗位系数',
  effect_time DATETIME NOT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='补贴标准';

CREATE TABLE post_type_factor (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  post_type VARCHAR(30) NOT NULL COMMENT '岗位类型',
  factor DECIMAL(4,2) NOT NULL COMMENT '系数',
  remark VARCHAR(120),
  status CHAR(1) DEFAULT '1'
) COMMENT='特殊岗位系数';

CREATE TABLE student_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL UNIQUE,
  college VARCHAR(60) COMMENT '学院',
  major VARCHAR(60), grade VARCHAR(20),
  difficulty_level VARCHAR(20) COMMENT '困难认定等级 DIFFICULT_SPECIAL/DIFFICULT/NORMAL/NONE',
  skill_tags VARCHAR(200) COMMENT '技能标签，逗号分隔',
  available_time VARCHAR(200) COMMENT '可用时段',
  bank_card VARCHAR(40) COMMENT '银行卡后四位掩码',
  resume_path VARCHAR(255) COMMENT '简历附件路径',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='学生档案';

CREATE TABLE work_study_post (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  post_no VARCHAR(50) NOT NULL UNIQUE COMMENT '岗位编号，后端生成',
  post_name VARCHAR(80) NOT NULL,
  dept_id BIGINT NOT NULL COMMENT '用工部门',
  post_type VARCHAR(30) NOT NULL COMMENT '助管/助教/助研/志愿',
  work_place VARCHAR(100) NOT NULL,
  recruit_num INT NOT NULL DEFAULT 1 COMMENT '招聘人数',
  hired_num INT NOT NULL DEFAULT 0 COMMENT '已录用人数，后端重算',
  hour_rate DECIMAL(8,2) NOT NULL COMMENT '时薪标准',
  work_period VARCHAR(100) COMMENT '工作时段',
  ability_req VARCHAR(100) COMMENT '能力要求',
  post_desc VARCHAR(1000) COMMENT '岗位职责',
  budget DECIMAL(12,2) COMMENT '预算',
  teacher_id BIGINT COMMENT '指导老师',
  cover_image VARCHAR(255) COMMENT '岗位附图',
  status VARCHAR(20) DEFAULT 'DRAFT' COMMENT 'DRAFT/PENDING/RECRUITING/FULL/FINISHED/REJECTED',
  publish_time DATETIME NULL,
  version INT DEFAULT 0 COMMENT '乐观锁版本号',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0,
  KEY idx_post_dept (dept_id), KEY idx_post_status (status)
) COMMENT='勤工助学岗位';

CREATE TABLE post_application (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  apply_no VARCHAR(50) NOT NULL UNIQUE,
  post_id BIGINT NOT NULL,
  student_id BIGINT NOT NULL,
  apply_reason VARCHAR(500) COMMENT '申请理由',
  available_time VARCHAR(200) COMMENT '可用时段',
  resume_path VARCHAR(255) COMMENT '简历附件',
  interview_time DATETIME NULL,
  match_score DECIMAL(5,1) COMMENT '最近一次匹配分',
  status VARCHAR(20) DEFAULT 'SCREENING' COMMENT 'SCREENING/INTERVIEW/EMPLOYED/REJECTED/WITHDRAWN',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_app_post (post_id), KEY idx_app_student (student_id)
) COMMENT='岗位申请';

CREATE TABLE employment_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  post_id BIGINT NOT NULL, application_id BIGINT NOT NULL, student_id BIGINT NOT NULL,
  teacher_id BIGINT, employ_time DATETIME, status VARCHAR(20) DEFAULT 'EMPLOYED',
  remark VARCHAR(300) COMMENT '录用/驳回原因',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='录用记录';

CREATE TABLE work_shift (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  post_id BIGINT NOT NULL, student_id BIGINT NOT NULL,
  shift_date DATE NOT NULL, start_time VARCHAR(10) NOT NULL, end_time VARCHAR(10) NOT NULL,
  work_place VARCHAR(100),
  plan_hours DECIMAL(6,1) NOT NULL,
  conflict_flag TINYINT DEFAULT 0 COMMENT '1 存在课程/重复班次冲突',
  conflict_reason VARCHAR(200),
  status VARCHAR(20) DEFAULT 'CONFIRMED' COMMENT 'CONFIRMED/ADJUST/PENDING',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_shift_student (student_id, shift_date)
) COMMENT='排班';

CREATE TABLE attendance_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shift_id BIGINT, student_id BIGINT NOT NULL, post_id BIGINT NOT NULL,
  work_date DATE NOT NULL,
  check_in_time DATETIME NULL, check_out_time DATETIME NULL,
  actual_hours DECIMAL(6,1) DEFAULT 0, valid_hours DECIMAL(6,1) DEFAULT 0,
  status VARCHAR(20) DEFAULT 'NORMAL' COMMENT 'NORMAL/LATE/EARLY/ABSENT/LEAVE/MAKEUP/ING',
  abnormal_reason VARCHAR(200),
  evidence_image VARCHAR(255) COMMENT '异常证据图片',
  verify_status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/PASS/REJECT',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_att_student (student_id, work_date)
) COMMENT='考勤记录';

CREATE TABLE hour_summary (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  student_id BIGINT NOT NULL, post_id BIGINT NOT NULL,
  summary_month CHAR(7) NOT NULL COMMENT 'yyyy-MM',
  plan_hours DECIMAL(6,1) DEFAULT 0, actual_hours DECIMAL(6,1) DEFAULT 0,
  valid_hours DECIMAL(6,1) DEFAULT 0,
  limit_hours DECIMAL(6,1) DEFAULT 40.0,
  status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/CONFIRMED/OVER_LIMIT',
  confirm_time DATETIME NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_sum (student_id, post_id, summary_month)
) COMMENT='月度工时汇总';

CREATE TABLE hour_appeal (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  summary_id BIGINT NOT NULL, student_id BIGINT NOT NULL,
  appeal_hours DECIMAL(6,1) NOT NULL, reason VARCHAR(300) NOT NULL,
  status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/PASS/REJECT',
  handle_time DATETIME NULL, handle_remark VARCHAR(300),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='工时申诉';

CREATE TABLE subsidy_batch (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_no VARCHAR(50) NOT NULL UNIQUE,
  semester_id BIGINT NOT NULL, summary_month CHAR(7) NOT NULL,
  person_count INT DEFAULT 0, total_hours DECIMAL(10,1) DEFAULT 0,
  total_amount DECIMAL(12,2) DEFAULT 0,
  status VARCHAR(20) DEFAULT 'AUDITING' COMMENT 'AUDITING/APPROVED/PAID',
  audit_time DATETIME NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='补贴批次';

CREATE TABLE subsidy_item (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_id BIGINT NOT NULL, student_id BIGINT NOT NULL, post_id BIGINT NOT NULL,
  valid_hours DECIMAL(6,1) NOT NULL, hour_rate DECIMAL(8,2) NOT NULL,
  factor DECIMAL(4,2) DEFAULT 1.00,
  amount DECIMAL(10,2) NOT NULL COMMENT '后端计算：工时×时薪×系数',
  pay_status VARCHAR(20) DEFAULT 'WAIT' COMMENT 'WAIT/PAID/FAIL',
  pay_time DATETIME NULL, fail_reason VARCHAR(200),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_item_batch (batch_id)
) COMMENT='补贴明细';

CREATE TABLE term_evaluation (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  student_id BIGINT NOT NULL, post_id BIGINT NOT NULL, semester_id BIGINT NOT NULL,
  attendance_score INT DEFAULT 0 COMMENT '出勤 30',
  duty_score INT DEFAULT 0 COMMENT '责任 30',
  skill_score INT DEFAULT 0 COMMENT '技能 25',
  team_score INT DEFAULT 0 COMMENT '协作 15',
  total_score DECIMAL(5,1) DEFAULT 0,
  comment VARCHAR(300) COMMENT '老师评语',
  feedback VARCHAR(300) COMMENT '学生岗位反馈',
  status VARCHAR(20) DEFAULT 'WAIT_STUDENT' COMMENT 'DRAFT/WAIT_STUDENT/DONE',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='学期评价';

CREATE TABLE match_rule (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  version VARCHAR(10) NOT NULL,
  w_difficulty INT NOT NULL COMMENT '困难等级权重',
  w_conflict INT NOT NULL COMMENT '课表冲突权重',
  w_skill INT NOT NULL COMMENT '技能匹配权重',
  w_hours INT NOT NULL COMMENT '已获工时权重',
  w_absent INT NOT NULL COMMENT '历史缺勤权重',
  w_prefer INT NOT NULL COMMENT '岗位偏好权重',
  status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT 'ACTIVE/ARCHIVED',
  effect_time DATETIME NOT NULL,
  creator VARCHAR(40),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='公平匹配规则（权重合计必须 100）';

CREATE TABLE match_score (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  student_id BIGINT NOT NULL, post_id BIGINT NOT NULL, application_id BIGINT,
  rule_version VARCHAR(10) NOT NULL,
  score_difficulty INT, score_conflict INT, score_skill INT,
  score_hours INT, score_absent INT, score_prefer INT,
  total_score DECIMAL(5,1), grade VARCHAR(4) COMMENT 'A/B/C/D',
  snapshot_json TEXT COMMENT '输入快照，保证可复算',
  adjust_grade VARCHAR(4) COMMENT '人工调整后等级',
  adjust_reason VARCHAR(300) COMMENT '人工调整原因，不少于 5 字',
  adjust_by VARCHAR(40),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_score_app (application_id)
) COMMENT='匹配计算留痕';

CREATE TABLE work_study_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  biz_type VARCHAR(30) NOT NULL, biz_no VARCHAR(50) NOT NULL,
  from_status VARCHAR(20), to_status VARCHAR(20),
  action VARCHAR(60), reason VARCHAR(300),
  operator VARCHAR(40), create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_wsl_biz (biz_type, biz_no)
) COMMENT='业务流转时间轴';
"""


def d(days_ago, h=9, m=0):
    t = dt.datetime(2026, 10, 31, 20, 0, 0) - dt.timedelta(days=days_ago)
    return t.replace(hour=h, minute=m, second=random.randint(0, 59)).strftime("%Y-%m-%d %H:%M:%S")


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def insert(table, cols, rows):
    body = ",\n".join("(" + ", ".join(q(x) for x in r) + ")" for r in rows)
    return f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n{body};\n"


sql = [HEAD, DDL]

# ---------- 组织 ----------
orgs = [(1, "学生资助管理中心", "CENTER", 0, 1), (2, "计划财务处", "CENTER", 0, 2),
        (3, "图书馆", "DEPT", 0, 3), (4, "实验中心", "DEPT", 0, 4),
        (5, "教务处", "DEPT", 0, 5), (6, "信息中心", "DEPT", 0, 6),
        (7, "后勤保障处", "DEPT", 0, 7), (8, "学工部", "DEPT", 0, 8),
        (9, "档案馆", "DEPT", 0, 9), (10, "体育部", "DEPT", 0, 10),
        (11, "计算机学院", "COLLEGE", 0, 11), (12, "电子信息学院", "COLLEGE", 0, 12),
        (13, "机械工程学院", "COLLEGE", 0, 13), (14, "经济管理学院", "COLLEGE", 0, 14)]
sql.append(insert("sys_org", ["id", "org_name", "org_type", "parent_id", "sort"], orgs))

# ---------- 角色 ----------
roles = [(1, "ADMIN", "资助中心管理员", "ALL", 1), (2, "DEPT", "用工部门老师", "DEPT", 2),
         (3, "STUDENT", "学生", "SELF", 3), (4, "FINANCE", "财务审核员", "ALL_READONLY", 4)]
sql.append(insert("sys_role", ["id", "role_code", "role_name", "data_scope", "sort"], roles))

# ---------- 菜单 ----------
MENUS = [
    (1, 0, "工作台", "/dashboard", "dashboard", 1),
    (2, 0, "我的待办", "/todo", "todo", 2),
    (3, 0, "岗位广场", "/post-square", "post", 3),
    (4, 0, "我的申请", "/my-apply", "apply", 4),
    (5, 0, "岗位管理", "/post-mgr", "post", 5),
    (6, 0, "岗位审批", "/post-audit", "audit", 6),
    (7, 0, "录用审核台", "/employment", "employ", 7),
    (8, 0, "排班管理", "/shift", "shift", 8),
    (9, 0, "我的排班", "/my-shift", "shift", 9),
    (10, 0, "考勤复核", "/attendance", "attend", 10),
    (11, 0, "签到签退", "/check", "attend", 11),
    (12, 0, "工时复核", "/hours", "hours", 12),
    (13, 0, "我的工时", "/my-hours", "hours", 13),
    (14, 0, "补贴核算", "/subsidy", "subsidy", 14),
    (15, 0, "发放登记", "/pay", "pay", 15),
    (16, 0, "学期评价", "/evaluate", "evaluate", 16),
    (17, 0, "学期与标准", "/standard", "standard", 17),
    (18, 0, "匹配规则", "/rule", "rule", 18),
    (19, 0, "计算留痕", "/score", "score", 19),
    (20, 0, "用工分析", "/report", "report", 20),
    (21, 0, "用户管理", "/user", "user", 21),
    (22, 0, "角色管理", "/role", "role", 22),
    (23, 0, "菜单管理", "/menu", "menu", 99),
]
menu_rows = [(i, p, n, "M", path, "sys:" + path.strip("/"), icon, s,
              0 if path == "/menu" else 1) for i, p, n, path, icon, s in MENUS]
sql.append(insert("sys_menu", ["id", "parent_id", "menu_name", "menu_type", "path", "perms",
                               "icon", "sort", "visible"], menu_rows))

ROLE_MENUS = {
    1: [1, 2, 5, 6, 7, 8, 10, 12, 14, 16, 17, 18, 19, 20, 21, 22, 23],
    2: [1, 2, 5, 7, 8, 10, 12, 16, 19],
    3: [1, 3, 4, 9, 11, 13],
    4: [1, 2, 14, 15, 20],
}
rm = []
k = 1
for rid, mids in ROLE_MENUS.items():
    for m in mids:
        rm.append((k, rid, m))
        k += 1
sql.append(insert("sys_role_menu", ["id", "role_id", "menu_id"], rm))

# ---------- 字典 ----------
dicts = [("post_type", "助管", "ASSIST_ADMIN"), ("post_type", "助教", "ASSIST_TEACH"),
         ("post_type", "助研", "ASSIST_RESEARCH"), ("post_type", "志愿服务", "VOLUNTEER"),
         ("post_status", "草稿", "DRAFT"), ("post_status", "待审核", "PENDING"),
         ("post_status", "招聘中", "RECRUITING"), ("post_status", "已满额", "FULL"),
         ("post_status", "已结束", "FINISHED"), ("post_status", "已驳回", "REJECTED"),
         ("difficulty", "特别困难", "DIFFICULT_SPECIAL"), ("difficulty", "困难", "DIFFICULT"),
         ("difficulty", "一般", "NORMAL"), ("difficulty", "不困难", "NONE"),
         ("attend_status", "正常", "NORMAL"), ("attend_status", "迟到", "LATE"),
         ("attend_status", "早退", "EARLY"), ("attend_status", "缺勤", "ABSENT"),
         ("attend_status", "请假", "LEAVE"), ("attend_status", "补卡", "MAKEUP"),
         ("weekday", "周一", "1"), ("weekday", "周二", "2"), ("weekday", "周三", "3"),
         ("weekday", "周四", "4"), ("weekday", "周五", "5"), ("weekday", "周六", "6"),
         ("weekday", "周日", "7")]
sql.append(insert("sys_dict", ["id", "dict_type", "dict_label", "dict_value", "sort"],
                  [(i + 1, t, l, v, i) for i, (t, l, v) in enumerate(dicts)]))

# ---------- 用户 ----------
DEPTS = {3: "图书馆", 4: "实验中心", 5: "教务处", 6: "信息中心", 7: "后勤保障处",
         8: "学工部", 9: "档案馆", 10: "体育部"}
TEACHERS = [(101, "t_zhou", "周岚", 3), (102, "t_li", "李强", 4), (103, "t_chen", "陈立", 5),
            (104, "t_sun", "孙浩", 6), (105, "t_zhao", "赵敏", 8), (106, "t_qian", "钱伟", 9),
            (107, "t_wu", "吴磊", 10), (108, "t_hu", "胡静", 7), (109, "t_gao", "高峰", 5),
            (110, "t_lin", "林芳", 4)]
STUDENTS = [
    (201, "s_2023010214", "张一凡", "2023010214", 11, "计算机学院", "计算机科学与技术", "2023级", "DIFFICULT_SPECIAL",
     "计算机维护,网络调试,办公软件", "周一至周五 18:00 后，周六全天"),
    (202, "s_2023020377", "陈思远", "2023020377", 12, "电子信息学院", "电子信息工程", "2023级", "DIFFICULT",
     "电子电路,焊接,仪器操作", "周二、周四 18:00 后，周日全天"),
    (203, "s_2023040552", "李梦瑶", "2023040552", 13, "机械工程学院", "机械设计制造", "2024级", "NORMAL",
     "文档整理,制图,Photoshop", "周一至周五 14:00 后"),
    (204, "s_2023030119", "王浩然", "2023030119", 11, "计算机学院", "软件工程", "2023级", "DIFFICULT_SPECIAL",
     "编程,数据库,服务器运维", "周三全天，周五 18:00 后"),
    (205, "s_2023050803", "刘雨桐", "2023050803", 14, "经济管理学院", "会计学", "2024级", "DIFFICULT",
     "Excel,数据整理,公文写作", "周一至周五 18:00 后"),
    (206, "s_2023020411", "赵天成", "2023020411", 12, "电子信息学院", "通信工程", "2022级", "NORMAL",
     "网络维护,硬件维修", "周二、周四全天"),
    (207, "s_2023060233", "孙悦", "2023060233", 13, "机械工程学院", "工业设计", "2024级", "DIFFICULT_SPECIAL",
     "设计,摄影,排版", "周末全天"),
    (208, "s_2023010388", "周子涵", "2023010388", 11, "计算机学院", "人工智能", "2022级", "NONE",
     "Python,数据分析", "周一、周三 18:00 后"),
]
users = [(1, "admin", "王敏", 1, 1, None, "13800002201", "wangmin@univ.edu.cn", "/uploads/seed/avatar/01.jpg", "F", 1, d(3, 8, 22)),
         (2, "fin_liu", "刘颖", 4, 2, None, "13600009033", "liuying@univ.edu.cn", "/uploads/seed/avatar/02.jpg", "F", 1, d(1, 9, 15))]
for i, (uid, un, rn, org) in enumerate(TEACHERS, start=3):
    users.append((uid, un, rn, 2, org, None, "139%08d" % random.randint(0, 99999999),
                  un + "@univ.edu.cn", "/uploads/seed/avatar/%02d.jpg" % (i % 6 + 1), "M" if i % 2 else "F", 1, d(i * 3, 8, 30)))
for i, s in enumerate(STUDENTS):
    uid, un, rn, sno, org, col, maj, grade, lvl, skills, avail = s
    users.append((uid, un, rn, 3, org, sno, "137%08d" % random.randint(0, 99999999),
                  un + "@stu.univ.edu.cn", "/uploads/seed/avatar/%02d.jpg" % (i % 6 + 1),
                  "M" if i % 2 == 0 else "F", 1, d(i * 2 + 1, 20, 10)))
urows = [(u[0], u[1], PWD, u[2], u[3], u[4], u[5], u[6], u[7], u[8], u[9], u[10], 0, None, u[11], d(190 - u[0] * 4, 9, 10), d(2, 18, 0), 0) for u in users]
sql.append(insert("sys_user", ["id", "username", "password", "real_name", "role_id", "org_id", "student_no",
                               "phone", "email", "avatar", "gender", "status", "login_fail", "lock_until",
                               "last_login", "create_time", "update_time", "deleted"], urows))

# ---------- 学生档案 ----------
profs = []
for i, s in enumerate(STUDENTS):
    uid, un, rn, sno, org, col, maj, grade, lvl, skills, avail = s
    profs.append((i + 1, uid, col, maj, grade, lvl, skills, avail, "****" + str(random.randint(1000, 9999)),
                  "/uploads/seed/evidence/%02d.jpg" % (i % 3 + 1), d(150 - i * 5, 10, 0), d(6, 16, 0)))
sql.append(insert("student_profile", ["id", "user_id", "college", "major", "grade", "difficulty_level",
                                     "skill_tags", "available_time", "bank_card", "resume_path",
                                     "create_time", "update_time"], profs))

# ---------- 学期 / 标准 ----------
sql.append(insert("semester", ["id", "term_name", "start_date", "end_date", "month_hour_limit", "status", "create_time"],
                  [(1, "2026 秋季", "2026-09-01", "2027-01-15", 40.0, "RUNNING", d(180, 9, 0)),
                   (2, "2026 春季", "2026-02-24", "2026-07-10", 40.0, "FINISHED", d(300, 9, 0))]))
sql.append(insert("subsidy_standard", ["id", "semester_id", "hour_rate", "month_hour_limit", "special_factor", "effect_time", "create_time"],
                  [(1, 1, 22.00, 40.0, 1.10, "2026-09-01 00:00:00", d(180, 9, 10)),
                   (2, 2, 21.00, 40.0, 1.05, "2026-02-24 00:00:00", d(300, 9, 10))]))
sql.append(insert("post_type_factor", ["id", "post_type", "factor", "remark", "status"],
                  [(1, "实验设备维护", 1.20, "含设备操作风险", "1"),
                   (2, "夜间值守", 1.15, "22:00 后时段", "1"),
                   (3, "普通助管", 1.00, "默认系数", "1"),
                   (4, "助教", 1.05, "需课程成绩前 30%", "1")]))

# ---------- 岗位 ----------
POSTS = [
    ("图书馆阅览室值班", 3, "助管", "图书馆 3F 阅览室", 2, 22.00, "工作日 18:00-22:00", "普通话标准,责任心强", "阅览室晚间开放值守，负责借还登记、秩序维护与设备关闭。", 12800, 101, "RECRUITING"),
    ("实验中心设备维护助理", 4, "助研", "实验楼 A 座 403", 3, 25.00, "周一至周五 14:00-18:00", "电子电路,仪器操作", "协助实验室设备日常巡检、耗材登记及简单故障排查。", 24000, 102, "RECRUITING"),
    ("教务处资料整理", 5, "助管", "行政楼 208", 1, 20.00, "工作日 14:00-17:00", "办公软件,公文写作", "教学档案归档、数据录入与文件流转。", 8400, 103, "RECRUITING"),
    ("机房值守助理", 6, "助管", "信息楼 B201 机房", 4, 24.00, "工作日 18:00-22:00", "网络维护,服务器运维", "机房日常值守、上机秩序维护与网络故障初判。", 31200, 104, "RECRUITING"),
    ("迎新志愿服务岗", 8, "志愿服务", "校园各迎新点", 8, 18.00, "9 月 1 日-9 月 7 日全天", "沟通能力,体力", "迎新期间引导新生报到、搬运行李与咨询答疑。", 18600, 105, "FULL"),
    ("档案室数字化助理", 9, "助管", "档案馆 105", 2, 22.00, "工作日 09:00-12:00", "文档整理,扫描设备", "纸质档案扫描、命名与目录校对。", 13600, 106, "RECRUITING"),
    ("体育场馆管理员", 10, "助管", "体育馆 1 号馆", 2, 20.00, "周末 09:00-17:00", "责任心强,安全意识", "场馆开放管理、器材借还登记与安全检查。", 11200, 107, "FULL"),
    ("食堂文明督导", 7, "志愿服务", "第一食堂", 6, 18.00, "工作日 11:30-13:00", "沟通能力", "就餐秩序引导、光盘行动宣传与意见收集。", 9600, 108, "FINISHED"),
    ("课程助教（数据结构）", 11, "助教", "计算机学院 A305", 2, 26.00, "周二、周四 19:00-21:00", "数据结构,表达能力", "协助批改作业、答疑与实验课辅导。", 20800, 109, "RECRUITING"),
    ("实验室耗材管理", 4, "助管", "实验楼 A 座 201", 1, 22.00, "工作日 09:00-12:00", "Excel,细致耐心", "耗材出入库登记、库存盘点与采购申请整理。", 8800, 102, "RECRUITING"),
    ("校史馆讲解助理", 9, "志愿服务", "校史馆", 3, 20.00, "周末 10:00-16:00", "普通话标准,表达能力", "校史馆参观接待与讲解。", 14400, 106, "FINISHED"),
    ("网络运维助理", 6, "助研", "信息楼 B105", 2, 25.00, "工作日 15:00-18:00", "网络调试,Linux", "校园网终端故障处理与交换机日常巡检。", 15600, 104, "DRAFT"),
    ("图书馆书架整理", 3, "助管", "图书馆 2F", 3, 20.00, "工作日 08:00-11:00", "体力,细致", "书架倒架、图书排序与破损图书登记。", 13200, 101, "PENDING"),
    ("就业中心信息录入", 8, "助管", "就业指导中心", 1, 21.00, "工作日 14:00-17:00", "Excel,数据录入", "招聘信息审核录入与企业联系台账维护。", 7560, 105, "PENDING"),
    ("宿舍安全检查助理", 7, "助管", "学生公寓 1-6 栋", 4, 19.00, "每周二、周四 20:00-22:00", "责任心强", "宿舍安全隐患排查与记录上报。", 9120, 108, "RECRUITING"),
    ("科研数据标注", 4, "助研", "实验楼 C 座 502", 2, 28.00, "时间灵活", "Python,细致", "科研项目图像数据标注与质量抽检。", 22400, 110, "RECRUITING"),
]
post_rows = []
for i, (name, dept, ptype, place, num, rate, period, ability, desc, budget, teacher, status) in enumerate(POSTS, start=1):
    no = "WS-2026-%04d" % (70 + i)
    hired = num if status == "FULL" else (0 if status in ("DRAFT", "PENDING") else random.randint(0, num - 1))
    pub = d(160 - i * 6, 10, 0) if status not in ("DRAFT", "PENDING") else None
    post_rows.append((i, no, name, dept, ptype, place, num, hired, rate, period, ability, desc, budget,
                      teacher, "/uploads/seed/post/%02d.jpg" % (i % 6 + 1), status, pub,
                      d(170 - i * 6, 9, 20), d(3 + i, 15, 0), 1))
sql.append(insert("work_study_post", ["id", "post_no", "post_name", "dept_id", "post_type", "work_place",
                                      "recruit_num", "hired_num", "hour_rate", "work_period", "ability_req",
                                      "post_desc", "budget", "teacher_id", "cover_image", "status",
                                      "publish_time", "create_time", "update_time", "version"], post_rows))

# ---------- 申请 ----------
APP_STATUS = ["SCREENING", "SCREENING", "INTERVIEW", "INTERVIEW", "EMPLOYED", "EMPLOYED", "EMPLOYED", "REJECTED"]
apps = []
aid = 380
for i in range(34):
    aid += 1
    post = (i % 16) + 1
    stu = 201 + ((i * 3 + i // 16) % 8)
    st = APP_STATUS[i % len(APP_STATUS)]
    t = d(175 - i * 5, 9 + (i % 8), (i * 7) % 59)
    apps.append((i + 1, "AP-2026-%04d" % aid, post, stu,
                 random.choice(["希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。",
                                "本人具备岗位所需技能，时间安排稳定，愿意长期承担。",
                                "对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。"]),
                 random.choice(["周一至周五 18:00 后", "周末全天", "周二、周四 14:00 后"]),
                 "/uploads/seed/evidence/%02d.jpg" % (i % 3 + 1),
                 d(110 - i * 3, 14, 0) if st == "INTERVIEW" else None,
                 round(random.uniform(62, 92), 1) if st in ("INTERVIEW", "EMPLOYED", "REJECTED") else None,
                 st, t, d(100 - i * 3, 16, 0)))
sql.append(insert("post_application", ["id", "apply_no", "post_id", "student_id", "apply_reason",
                                       "available_time", "resume_path", "interview_time", "match_score",
                                       "status", "create_time", "update_time"], apps))

# ---------- 录用 ----------
emps = []
eid = 0
for a in apps:
    if a[9] == "EMPLOYED":
        eid += 1
        emps.append((eid, a[2], a[0], a[3], 101, a[11], "EMPLOYED", "面试通过，技能与岗位匹配"))
    elif a[9] == "REJECTED":
        eid += 1
        emps.append((eid, a[2], a[0], a[3], 101, a[11], "REJECTED", "同期候选人匹配度更高，岗位名额已满"))
sql.append(insert("employment_record", ["id", "post_id", "application_id", "student_id", "teacher_id",
                                        "employ_time", "status", "remark"], emps))

# ---------- 排班 ----------
shifts = []
sid = 0
base = dt.date(2026, 10, 31)
for i in range(46):
    sid += 1
    stu = 201 + (i % 8)
    post = (i % 16) + 1
    day = base - dt.timedelta(days=(i * 2) % 58)
    conflict = 1 if i % 11 == 0 else 0
    shifts.append((sid, post, stu, day.strftime("%Y-%m-%d"), "18:00", "22:00",
                   random.choice(["图书馆 3F 阅览室", "实验楼 A 座 403", "信息楼 B201 机房", "档案馆 105"]),
                   4.0, conflict,
                   random.choice(["与《编译原理》晚课冲突", "当日已有其他班次"]) if conflict else None,
                   "ADJUST" if conflict else "CONFIRMED",
                   d(150 - i * 2, 10, 0)))
sql.append(insert("work_shift", ["id", "post_id", "student_id", "shift_date", "start_time", "end_time",
                                 "work_place", "plan_hours", "conflict_flag", "conflict_reason",
                                 "status", "create_time"], shifts))

# ---------- 考勤 ----------
ATT = ["NORMAL", "NORMAL", "NORMAL", "NORMAL", "LATE", "EARLY", "ABSENT", "LEAVE"]
atts = []
for i, sh in enumerate(shifts):
    st = ATT[i % len(ATT)]
    wd = sh[3]
    # 签到签退时间带随机分钟/秒，避免所有记录时间完全一致
    ci = wd + " 17:%02d:%02d" % (random.randint(48, 59), random.randint(0, 59)) if st != "LATE" \
        else wd + " 18:%02d:%02d" % (random.randint(6, 25), random.randint(0, 59))
    co = wd + " 21:%02d:%02d" % (random.randint(40, 59), random.randint(0, 59)) if st != "EARLY" \
        else wd + " 21:%02d:%02d" % (random.randint(10, 40), random.randint(0, 59))
    actual = 4.0 if st in ("NORMAL", "LATE") else (3.8 if st == "EARLY" else 0)
    valid = max(0.0, round(actual - (0.5 if st == "LATE" else 0.2 if st == "EARLY" else 0), 1))
    atts.append((i + 1, sh[0], sh[2], sh[1], wd,
                 None if st in ("ABSENT", "LEAVE") else ci,
                 None if st in ("ABSENT", "LEAVE") else co,
                 actual, valid, st,
                 {"LATE": "迟到 9 分钟", "EARLY": "早退 12 分钟", "ABSENT": "未签到且未请假",
                  "LEAVE": "已提交请假单"}.get(st),
                 "/uploads/seed/evidence/%02d.jpg" % (i % 3 + 1) if st in ("ABSENT", "LATE") else None,
                 random.choice(["PASS", "PASS", "PENDING"]) if st != "NORMAL" else "PASS",
                 d(150 - i * 2, 22, 10)))
sql.append(insert("attendance_record", ["id", "shift_id", "student_id", "post_id", "work_date",
                                       "check_in_time", "check_out_time", "actual_hours", "valid_hours",
                                       "status", "abnormal_reason", "evidence_image", "verify_status",
                                       "create_time"], atts))

# ---------- 工时汇总 ----------
sums = []
k = 0
for month in ["2026-05", "2026-06", "2026-09", "2026-10"]:
    for stu in range(201, 209):
        k += 1
        plan = random.choice([24.0, 28.0, 32.0, 36.0, 40.0, 44.0])
        actual = round(plan + random.choice([-0.5, 0, 0, 0.4, 0.8]), 1)
        valid = min(actual, 40.0) if plan > 40 else actual
        over = plan > 40
        st = "OVER_LIMIT" if over else ("CONFIRMED" if month != "2026-10" else "PENDING")
        sums.append((k, stu, (stu - 201) % 16 + 1, month, plan, actual, valid, 40.0, st,
                     d(30, 10, 0) if st == "CONFIRMED" else None, d(60, 9, 0)))
sql.append(insert("hour_summary", ["id", "student_id", "post_id", "summary_month", "plan_hours",
                                   "actual_hours", "valid_hours", "limit_hours", "status",
                                   "confirm_time", "create_time"], sums))

# ---------- 申诉 ----------
appeals = [(1, 17, 202, 2.0, "10 月 22 日临时顶班未计入排班，实际到岗 4 小时", "PENDING", None, None, d(4, 11, 8)),
           (2, 9, 201, 0.5, "当日系统故障导致签到失败，有老师证明", "PASS", d(3, 15, 0), "经核实予以补录 0.5 小时", d(6, 9, 12)),
           (3, 4, 207, 1.5, "周末班次调换后未同步系统，实际出勤 5.5 小时", "REJECT", d(10, 10, 0), "调换未走审批流程，不予认定", d(20, 14, 30))]
sql.append(insert("hour_appeal", ["id", "summary_id", "student_id", "appeal_hours", "reason", "status",
                                  "handle_time", "handle_remark", "create_time"], appeals))

# ---------- 补贴批次 / 明细 ----------
sql.append(insert("subsidy_batch", ["id", "batch_no", "semester_id", "summary_month", "person_count",
                                    "total_hours", "total_amount", "status", "audit_time", "create_time"],
                  [(1, "SB-2026-09-A", 1, "2026-09", 8, 271.2, 5836.80, "PAID", d(40, 10, 0), d(45, 9, 0)),
                   (2, "SB-2026-10-A", 1, "2026-10", 8, 289.3, 6248.40, "AUDITING", None, d(5, 9, 0))]))
items = []
for i in range(16):
    batch = 1 if i < 8 else 2
    stu = 201 + (i % 8)
    h = round(random.uniform(20, 40), 1)
    rate = random.choice([22.0, 25.0, 20.0, 24.0])
    factor = random.choice([1.0, 1.2, 1.15])
    amt = round(h * rate * factor, 2)
    pay = "PAID" if batch == 1 else ("FAIL" if i == 12 else "WAIT")
    items.append((i + 1, batch, stu, (i % 16) + 1, h, rate, factor, amt, pay,
                  d(38, 14, 0) if pay == "PAID" else None,
                  "银行卡信息有误，退回重发" if pay == "FAIL" else None, d(9, 9, 30)))
sql.append(insert("subsidy_item", ["id", "batch_id", "student_id", "post_id", "valid_hours", "hour_rate",
                                   "factor", "amount", "pay_status", "pay_time", "fail_reason", "create_time"], items))

# ---------- 学期评价 ----------
evals = []
for i in range(10):
    a, b, c, e = random.randint(22, 30), random.randint(21, 30), random.randint(16, 25), random.randint(9, 15)
    evals.append((i + 1, 201 + (i % 8), (i % 16) + 1, 1, a, b, c, e, round(a + b + c + e, 1),
                  random.choice(["值守认真，借还登记准确，建议下学期继续留用。", "工作主动，能与同学配合完成临时任务。",
                                 "技能掌握较快，建议加强时间观念。"]),
                  random.choice(["岗位与专业相关，希望增加培训", "工作强度适中，收获较大", "排班较为集中，建议分散"]),
                  random.choice(["DONE", "WAIT_STUDENT", "WAIT_STUDENT"]), d(20 - i, 16, 0)))
sql.append(insert("term_evaluation", ["id", "student_id", "post_id", "semester_id", "attendance_score",
                                      "duty_score", "skill_score", "team_score", "total_score", "comment",
                                      "feedback", "status", "create_time"], evals))

# ---------- 匹配规则 ----------
sql.append(insert("match_rule", ["id", "version", "w_difficulty", "w_conflict", "w_skill", "w_hours",
                                  "w_absent", "w_prefer", "status", "effect_time", "creator", "create_time"],
                  [(1, "v2", 25, 20, 20, 15, 10, 10, "ARCHIVED", "2026-03-01 00:00:00", "王敏", d(240, 9, 0)),
                   (2, "v3", 30, 15, 20, 15, 10, 10, "ACTIVE", "2026-09-01 00:00:00", "王敏", d(180, 9, 0))]))

# ---------- 匹配计算留痕 ----------
scores = []
for i in range(20):
    stu = 201 + (i % 8)
    post = (i % 16) + 1
    sd = random.choice([40, 60, 80, 100])
    sc = random.choice([30, 60, 90])
    sk = random.choice([50, 70, 88, 96])
    sh = random.choice([50, 70, 85])
    sa = random.choice([0, 60, 90, 100])
    sp = random.choice([50, 75, 100])
    tot = round(sd * .3 + sc * .15 + sk * .2 + sh * .15 + sa * .1 + sp * .1, 1)
    grade = "A" if tot >= 80 else "B" if tot >= 70 else "C" if tot >= 60 else "D"
    adj = "B" if i == 3 else None
    scores.append((i + 1, stu, post, (i % 34) + 1, "v3", sd, sc, sk, sh, sa, sp, tot, grade,
                   '{"difficulty":%d,"conflict":%d,"skill":%d,"hours":%d,"absent":%d,"prefer":%d}' % (sd, sc, sk, sh, sa, sp),
                   adj, "面试沟通表达不足，暂列候补" if adj else None, "李强" if adj else None,
                   d(50 - i, 16, 20)))
sql.append(insert("match_score", ["id", "student_id", "post_id", "application_id", "rule_version",
                                  "score_difficulty", "score_conflict", "score_skill", "score_hours",
                                  "score_absent", "score_prefer", "total_score", "grade", "snapshot_json",
                                  "adjust_grade", "adjust_reason", "adjust_by", "create_time"], scores))

# ---------- 流转时间轴 ----------
logs = []
k = 0
for i in range(24):
    k += 1
    logs.append((k, "POST" if i % 3 else "APPLICATION",
                 "WS-2026-%04d" % (71 + i % 16) if i % 3 else "AP-2026-%04d" % (381 + i % 34),
                 random.choice(["DRAFT", "PENDING", "SCREENING"]),
                 random.choice(["PENDING", "RECRUITING", "INTERVIEW", "EMPLOYED"]),
                 random.choice(["提交", "审核通过", "驳回", "录用", "退回修改", "发布"]),
                 random.choice(["材料齐备，予以通过", "预算超限，退回调整", "岗位必要性强，同意发布", None]),
                 random.choice(["王敏", "李强", "周岚", "刘颖"]), d(120 - i * 4, 10, 5)))
sql.append(insert("work_study_log", ["id", "biz_type", "biz_no", "from_status", "to_status",
                                     "action", "reason", "operator", "create_time"], logs))

# ---------- 消息 ----------
msgs = [(1, "岗位待审批", "图书馆提交的「图书馆阅览室值班」等待审核，请及时处理。", "POST", "WS-2026-0071", 1, 0, d(1, 9, 12)),
        (2, "工时申诉待处理", "陈思远提交 10 月工时申诉 2.0 小时，请在期限内复核。", "APPEAL", "APL-0001", 1, 0, d(4, 11, 10)),
        (3, "补贴批次待审核", "10 月补贴批次 SB-2026-10-A 已生成，共 8 人。", "SUBSIDY", "SB-2026-10-A", 2, 0, d(5, 9, 5)),
        (4, "面试通知", "您申请的「实验中心设备维护助理」面试时间为 11 月 2 日 14:00。", "APPLICATION", "AP-2026-0412", 201, 1, d(2, 15, 0)),
        (5, "工时待确认", "10 月工时已汇总，请在 11 月 5 日前确认。", "HOURS", "2026-10", 101, 0, d(3, 8, 40))]
sql.append(insert("sys_message", ["id", "title", "content", "biz_type", "biz_no", "receiver_id",
                                  "read_flag", "create_time"], msgs))

# ---------- 附件 ----------
atts2 = []
for i in range(12):
    atts2.append((i + 1, "STUDENT_PROOF" if i % 2 else "POST_DOC",
                  "AP-2026-%04d" % (381 + i) if i % 2 else "WS-2026-%04d" % (71 + i),
                  random.choice(["困难认定证明.jpg", "学生证扫描件.jpg", "岗位申请书.jpg"]),
                  "/uploads/seed/evidence/%02d.jpg" % (i % 3 + 1),
                  random.randint(120000, 380000), 201 + (i % 8), d(80 - i * 4, 10, 0)))
sql.append(insert("sys_attachment", ["id", "biz_type", "biz_no", "file_name", "file_path", "file_size",
                                     "uploader_id", "create_time"], atts2))

# ---------- 日志 ----------
logrows = []
for i in range(40):
    logrows.append((i + 1, random.choice([1, 2, 101, 102, 201]), random.choice(["王敏", "刘颖", "周岚", "李强", "张一凡"]),
                    random.choice(["岗位管理", "录用管理", "考勤管理", "补贴核算", "系统管理"]),
                    random.choice(["新增", "修改", "删除", "审批", "导出"]),
                    random.choice(["/api/post", "/api/application/employ", "/api/attendance/verify", "/api/subsidy/generate"]),
                    "{}", "127.0.0.1", random.randint(12, 480), d(30 - i % 30, 9 + i % 10, i % 60)))
sql.append(insert("sys_log", ["id", "user_id", "user_name", "module", "action", "method", "params",
                              "ip", "cost_ms", "create_time"], logrows))

# ---------- 回填：申请单上的匹配分取最近一次计算留痕（保证列表页有值） ----------
sql.append("""UPDATE post_application a JOIN match_score s ON s.application_id = a.id
SET a.match_score = s.total_score WHERE a.match_score IS NULL;
""")

sql.append("SET FOREIGN_KEY_CHECKS = 1;\n")
OUT.write_text("\n".join(sql), encoding="utf-8")
print("written", OUT, len(OUT.read_text(encoding='utf-8')), "bytes")
