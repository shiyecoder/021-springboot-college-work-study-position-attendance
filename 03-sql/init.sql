-- ============================================================
-- 高校勤工助学岗位与考勤管理系统 数据库初始化脚本
-- MySQL 8 / utf8mb4 ；库名 new_021
-- 说明：所有图片字段均指向项目内真实本地图片 /uploads/seed/<实体>/NN.jpg
-- ============================================================
DROP DATABASE IF EXISTS new_021;
CREATE DATABASE new_021 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE new_021;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;


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

INSERT INTO sys_org (id, org_name, org_type, parent_id, sort) VALUES
(1, '学生资助管理中心', 'CENTER', 0, 1),
(2, '计划财务处', 'CENTER', 0, 2),
(3, '图书馆', 'DEPT', 0, 3),
(4, '实验中心', 'DEPT', 0, 4),
(5, '教务处', 'DEPT', 0, 5),
(6, '信息中心', 'DEPT', 0, 6),
(7, '后勤保障处', 'DEPT', 0, 7),
(8, '学工部', 'DEPT', 0, 8),
(9, '档案馆', 'DEPT', 0, 9),
(10, '体育部', 'DEPT', 0, 10),
(11, '计算机学院', 'COLLEGE', 0, 11),
(12, '电子信息学院', 'COLLEGE', 0, 12),
(13, '机械工程学院', 'COLLEGE', 0, 13),
(14, '经济管理学院', 'COLLEGE', 0, 14);

INSERT INTO sys_role (id, role_code, role_name, data_scope, sort) VALUES
(1, 'ADMIN', '资助中心管理员', 'ALL', 1),
(2, 'DEPT', '用工部门老师', 'DEPT', 2),
(3, 'STUDENT', '学生', 'SELF', 3),
(4, 'FINANCE', '财务审核员', 'ALL_READONLY', 4);

INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, perms, icon, sort, visible) VALUES
(1, 0, '工作台', 'M', '/dashboard', 'sys:dashboard', 'dashboard', 1, 1),
(2, 0, '我的待办', 'M', '/todo', 'sys:todo', 'todo', 2, 1),
(3, 0, '岗位广场', 'M', '/post-square', 'sys:post-square', 'post', 3, 1),
(4, 0, '我的申请', 'M', '/my-apply', 'sys:my-apply', 'apply', 4, 1),
(5, 0, '岗位管理', 'M', '/post-mgr', 'sys:post-mgr', 'post', 5, 1),
(6, 0, '岗位审批', 'M', '/post-audit', 'sys:post-audit', 'audit', 6, 1),
(7, 0, '录用审核台', 'M', '/employment', 'sys:employment', 'employ', 7, 1),
(8, 0, '排班管理', 'M', '/shift', 'sys:shift', 'shift', 8, 1),
(9, 0, '我的排班', 'M', '/my-shift', 'sys:my-shift', 'shift', 9, 1),
(10, 0, '考勤复核', 'M', '/attendance', 'sys:attendance', 'attend', 10, 1),
(11, 0, '签到签退', 'M', '/check', 'sys:check', 'attend', 11, 1),
(12, 0, '工时复核', 'M', '/hours', 'sys:hours', 'hours', 12, 1),
(13, 0, '我的工时', 'M', '/my-hours', 'sys:my-hours', 'hours', 13, 1),
(14, 0, '补贴核算', 'M', '/subsidy', 'sys:subsidy', 'subsidy', 14, 1),
(15, 0, '发放登记', 'M', '/pay', 'sys:pay', 'pay', 15, 1),
(16, 0, '学期评价', 'M', '/evaluate', 'sys:evaluate', 'evaluate', 16, 1),
(17, 0, '学期与标准', 'M', '/standard', 'sys:standard', 'standard', 17, 1),
(18, 0, '匹配规则', 'M', '/rule', 'sys:rule', 'rule', 18, 1),
(19, 0, '计算留痕', 'M', '/score', 'sys:score', 'score', 19, 1),
(20, 0, '用工分析', 'M', '/report', 'sys:report', 'report', 20, 1),
(21, 0, '用户管理', 'M', '/user', 'sys:user', 'user', 21, 1),
(22, 0, '角色管理', 'M', '/role', 'sys:role', 'role', 22, 1),
(23, 0, '菜单管理', 'M', '/menu', 'sys:menu', 'menu', 99, 0);

INSERT INTO sys_role_menu (id, role_id, menu_id) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 1, 5),
(4, 1, 6),
(5, 1, 7),
(6, 1, 8),
(7, 1, 10),
(8, 1, 12),
(9, 1, 14),
(10, 1, 16),
(11, 1, 17),
(12, 1, 18),
(13, 1, 19),
(14, 1, 20),
(15, 1, 21),
(16, 1, 22),
(17, 1, 23),
(18, 2, 1),
(19, 2, 2),
(20, 2, 5),
(21, 2, 7),
(22, 2, 8),
(23, 2, 10),
(24, 2, 12),
(25, 2, 16),
(26, 2, 19),
(27, 3, 1),
(28, 3, 3),
(29, 3, 4),
(30, 3, 9),
(31, 3, 11),
(32, 3, 13),
(33, 4, 1),
(34, 4, 2),
(35, 4, 14),
(36, 4, 15),
(37, 4, 20);

INSERT INTO sys_dict (id, dict_type, dict_label, dict_value, sort) VALUES
(1, 'post_type', '助管', 'ASSIST_ADMIN', 0),
(2, 'post_type', '助教', 'ASSIST_TEACH', 1),
(3, 'post_type', '助研', 'ASSIST_RESEARCH', 2),
(4, 'post_type', '志愿服务', 'VOLUNTEER', 3),
(5, 'post_status', '草稿', 'DRAFT', 4),
(6, 'post_status', '待审核', 'PENDING', 5),
(7, 'post_status', '招聘中', 'RECRUITING', 6),
(8, 'post_status', '已满额', 'FULL', 7),
(9, 'post_status', '已结束', 'FINISHED', 8),
(10, 'post_status', '已驳回', 'REJECTED', 9),
(11, 'difficulty', '特别困难', 'DIFFICULT_SPECIAL', 10),
(12, 'difficulty', '困难', 'DIFFICULT', 11),
(13, 'difficulty', '一般', 'NORMAL', 12),
(14, 'difficulty', '不困难', 'NONE', 13),
(15, 'attend_status', '正常', 'NORMAL', 14),
(16, 'attend_status', '迟到', 'LATE', 15),
(17, 'attend_status', '早退', 'EARLY', 16),
(18, 'attend_status', '缺勤', 'ABSENT', 17),
(19, 'attend_status', '请假', 'LEAVE', 18),
(20, 'attend_status', '补卡', 'MAKEUP', 19),
(21, 'weekday', '周一', '1', 20),
(22, 'weekday', '周二', '2', 21),
(23, 'weekday', '周三', '3', 22),
(24, 'weekday', '周四', '4', 23),
(25, 'weekday', '周五', '5', 24),
(26, 'weekday', '周六', '6', 25),
(27, 'weekday', '周日', '7', 26);

INSERT INTO sys_user (id, username, password, real_name, role_id, org_id, student_no, phone, email, avatar, gender, status, login_fail, lock_until, last_login, create_time, update_time, deleted) VALUES
(1, 'admin', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '王敏', 1, 1, NULL, '13800002201', 'wangmin@univ.edu.cn', '/uploads/seed/avatar/01.jpg', 'F', 1, 0, NULL, '2026-10-28 08:22:19', '2026-04-28 09:10:31', '2026-10-29 18:00:34', 0),
(2, 'fin_liu', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '刘颖', 4, 2, NULL, '13600009033', 'liuying@univ.edu.cn', '/uploads/seed/avatar/02.jpg', 'F', 1, 0, NULL, '2026-10-30 09:15:15', '2026-05-02 09:10:21', '2026-10-29 18:00:29', 0),
(101, 't_zhou', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '周岚', 2, 3, NULL, '13998493391', 't_zhou@univ.edu.cn', '/uploads/seed/avatar/04.jpg', 'M', 1, 0, NULL, '2026-10-22 08:30:24', '2027-06-02 09:10:23', '2026-10-29 18:00:24', 0),
(102, 't_li', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '李强', 2, 4, NULL, '13909770149', 't_li@univ.edu.cn', '/uploads/seed/avatar/05.jpg', 'F', 1, 0, NULL, '2026-10-19 08:30:32', '2027-06-06 09:10:23', '2026-10-29 18:00:41', 0),
(103, 't_chen', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '陈立', 2, 5, NULL, '13905485252', 't_chen@univ.edu.cn', '/uploads/seed/avatar/06.jpg', 'M', 1, 0, NULL, '2026-10-16 08:30:13', '2027-06-10 09:10:25', '2026-10-29 18:00:23', 0),
(104, 't_sun', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '孙浩', 2, 6, NULL, '13933166368', 't_sun@univ.edu.cn', '/uploads/seed/avatar/01.jpg', 'F', 1, 0, NULL, '2026-10-13 08:30:30', '2027-06-14 09:10:07', '2026-10-29 18:00:35', 0),
(105, 't_zhao', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '赵敏', 2, 8, NULL, '13929685625', 't_zhao@univ.edu.cn', '/uploads/seed/avatar/02.jpg', 'M', 1, 0, NULL, '2026-10-10 08:30:40', '2027-06-18 09:10:41', '2026-10-29 18:00:16', 0),
(106, 't_qian', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '钱伟', 2, 9, NULL, '13921277910', 't_qian@univ.edu.cn', '/uploads/seed/avatar/03.jpg', 'F', 1, 0, NULL, '2026-10-07 08:30:06', '2027-06-22 09:10:11', '2026-10-29 18:00:02', 0),
(107, 't_wu', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '吴磊', 2, 10, NULL, '13976941062', 't_wu@univ.edu.cn', '/uploads/seed/avatar/04.jpg', 'M', 1, 0, NULL, '2026-10-04 08:30:55', '2027-06-26 09:10:27', '2026-10-29 18:00:04', 0),
(108, 't_hu', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '胡静', 2, 7, NULL, '13978761273', 't_hu@univ.edu.cn', '/uploads/seed/avatar/05.jpg', 'F', 1, 0, NULL, '2026-10-01 08:30:02', '2027-06-30 09:10:18', '2026-10-29 18:00:24', 0),
(109, 't_gao', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '高峰', 2, 5, NULL, '13936310750', 't_gao@univ.edu.cn', '/uploads/seed/avatar/06.jpg', 'M', 1, 0, NULL, '2026-09-28 08:30:14', '2027-07-04 09:10:50', '2026-10-29 18:00:07', 0),
(110, 't_lin', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '林芳', 2, 4, NULL, '13910615102', 't_lin@univ.edu.cn', '/uploads/seed/avatar/01.jpg', 'F', 1, 0, NULL, '2026-09-25 08:30:14', '2027-07-08 09:10:39', '2026-10-29 18:00:15', 0),
(201, 's_2023010214', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '张一凡', 3, 11, '2023010214', '13775599833', 's_2023010214@stu.univ.edu.cn', '/uploads/seed/avatar/01.jpg', 'M', 1, 0, NULL, '2026-10-30 20:10:30', '2028-07-06 09:10:58', '2026-10-29 18:00:42', 0),
(202, 's_2023020377', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '陈思远', 3, 12, '2023020377', '13724516093', 's_2023020377@stu.univ.edu.cn', '/uploads/seed/avatar/02.jpg', 'F', 1, 0, NULL, '2026-10-28 20:10:49', '2028-07-10 09:10:50', '2026-10-29 18:00:57', 0),
(203, 's_2023040552', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '李梦瑶', 3, 13, '2023040552', '13750734756', 's_2023040552@stu.univ.edu.cn', '/uploads/seed/avatar/03.jpg', 'M', 1, 0, NULL, '2026-10-26 20:10:55', '2028-07-14 09:10:12', '2026-10-29 18:00:08', 0),
(204, 's_2023030119', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '王浩然', 3, 11, '2023030119', '13790105062', 's_2023030119@stu.univ.edu.cn', '/uploads/seed/avatar/04.jpg', 'F', 1, 0, NULL, '2026-10-24 20:10:23', '2028-07-18 09:10:07', '2026-10-29 18:00:35', 0),
(205, 's_2023050803', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '刘雨桐', 3, 14, '2023050803', '13782377666', 's_2023050803@stu.univ.edu.cn', '/uploads/seed/avatar/05.jpg', 'M', 1, 0, NULL, '2026-10-22 20:10:15', '2028-07-22 09:10:57', '2026-10-29 18:00:12', 0),
(206, 's_2023020411', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '赵天成', 3, 12, '2023020411', '13714234125', 's_2023020411@stu.univ.edu.cn', '/uploads/seed/avatar/06.jpg', 'F', 1, 0, NULL, '2026-10-20 20:10:02', '2028-07-26 09:10:05', '2026-10-29 18:00:10', 0),
(207, 's_2023060233', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '孙悦', 3, 13, '2023060233', '13756835798', 's_2023060233@stu.univ.edu.cn', '/uploads/seed/avatar/01.jpg', 'M', 1, 0, NULL, '2026-10-18 20:10:10', '2028-07-30 09:10:32', '2026-10-29 18:00:54', 0),
(208, 's_2023010388', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '周子涵', 3, 11, '2023010388', '13784925633', 's_2023010388@stu.univ.edu.cn', '/uploads/seed/avatar/02.jpg', 'F', 1, 0, NULL, '2026-10-16 20:10:26', '2028-08-03 09:10:15', '2026-10-29 18:00:55', 0);

INSERT INTO student_profile (id, user_id, college, major, grade, difficulty_level, skill_tags, available_time, bank_card, resume_path, create_time, update_time) VALUES
(1, 201, '计算机学院', '计算机科学与技术', '2023级', 'DIFFICULT_SPECIAL', '计算机维护,网络调试,办公软件', '周一至周五 18:00 后，周六全天', '****2465', '/uploads/seed/evidence/01.jpg', '2026-06-03 10:00:47', '2026-10-25 16:00:01'),
(2, 202, '电子信息学院', '电子信息工程', '2023级', 'DIFFICULT', '电子电路,焊接,仪器操作', '周二、周四 18:00 后，周日全天', '****5074', '/uploads/seed/evidence/02.jpg', '2026-06-08 10:00:54', '2026-10-25 16:00:40'),
(3, 203, '机械工程学院', '机械设计制造', '2024级', 'NORMAL', '文档整理,制图,Photoshop', '周一至周五 14:00 后', '****7078', '/uploads/seed/evidence/03.jpg', '2026-06-13 10:00:25', '2026-10-25 16:00:33'),
(4, 204, '计算机学院', '软件工程', '2023级', 'DIFFICULT_SPECIAL', '编程,数据库,服务器运维', '周三全天，周五 18:00 后', '****4655', '/uploads/seed/evidence/01.jpg', '2026-06-18 10:00:05', '2026-10-25 16:00:21'),
(5, 205, '经济管理学院', '会计学', '2024级', 'DIFFICULT', 'Excel,数据整理,公文写作', '周一至周五 18:00 后', '****9843', '/uploads/seed/evidence/02.jpg', '2026-06-23 10:00:12', '2026-10-25 16:00:13'),
(6, 206, '电子信息学院', '通信工程', '2022级', 'NORMAL', '网络维护,硬件维修', '周二、周四全天', '****8498', '/uploads/seed/evidence/03.jpg', '2026-06-28 10:00:28', '2026-10-25 16:00:40'),
(7, 207, '机械工程学院', '工业设计', '2024级', 'DIFFICULT_SPECIAL', '设计,摄影,排版', '周末全天', '****3171', '/uploads/seed/evidence/01.jpg', '2026-07-03 10:00:32', '2026-10-25 16:00:51'),
(8, 208, '计算机学院', '人工智能', '2022级', 'NONE', 'Python,数据分析', '周一、周三 18:00 后', '****1890', '/uploads/seed/evidence/02.jpg', '2026-07-08 10:00:55', '2026-10-25 16:00:26');

INSERT INTO semester (id, term_name, start_date, end_date, month_hour_limit, status, create_time) VALUES
(1, '2026 秋季', '2026-09-01', '2027-01-15', 40.0, 'RUNNING', '2026-05-04 09:00:44'),
(2, '2026 春季', '2026-02-24', '2026-07-10', 40.0, 'FINISHED', '2026-01-04 09:00:09');

INSERT INTO subsidy_standard (id, semester_id, hour_rate, month_hour_limit, special_factor, effect_time, create_time) VALUES
(1, 1, 22.0, 40.0, 1.1, '2026-09-01 00:00:00', '2026-05-04 09:10:03'),
(2, 2, 21.0, 40.0, 1.05, '2026-02-24 00:00:00', '2026-01-04 09:10:16');

INSERT INTO post_type_factor (id, post_type, factor, remark, status) VALUES
(1, '实验设备维护', 1.2, '含设备操作风险', '1'),
(2, '夜间值守', 1.15, '22:00 后时段', '1'),
(3, '普通助管', 1.0, '默认系数', '1'),
(4, '助教', 1.05, '需课程成绩前 30%', '1');

INSERT INTO work_study_post (id, post_no, post_name, dept_id, post_type, work_place, recruit_num, hired_num, hour_rate, work_period, ability_req, post_desc, budget, teacher_id, cover_image, status, publish_time, create_time, update_time, version) VALUES
(1, 'WS-2026-0071', '图书馆阅览室值班', 3, '助管', '图书馆 3F 阅览室', 2, 0, 22.0, '工作日 18:00-22:00', '普通话标准,责任心强', '阅览室晚间开放值守，负责借还登记、秩序维护与设备关闭。', 12800, 101, '/uploads/seed/post/02.jpg', 'RECRUITING', '2026-05-30 10:00:58', '2026-05-20 09:20:03', '2026-10-27 15:00:45', 1),
(2, 'WS-2026-0072', '实验中心设备维护助理', 4, '助研', '实验楼 A 座 403', 3, 0, 25.0, '周一至周五 14:00-18:00', '电子电路,仪器操作', '协助实验室设备日常巡检、耗材登记及简单故障排查。', 24000, 102, '/uploads/seed/post/03.jpg', 'RECRUITING', '2026-06-05 10:00:00', '2026-05-26 09:20:46', '2026-10-26 15:00:42', 1),
(3, 'WS-2026-0073', '教务处资料整理', 5, '助管', '行政楼 208', 1, 0, 20.0, '工作日 14:00-17:00', '办公软件,公文写作', '教学档案归档、数据录入与文件流转。', 8400, 103, '/uploads/seed/post/04.jpg', 'RECRUITING', '2026-06-11 10:00:18', '2026-06-01 09:20:54', '2026-10-25 15:00:12', 1),
(4, 'WS-2026-0074', '机房值守助理', 6, '助管', '信息楼 B201 机房', 4, 2, 24.0, '工作日 18:00-22:00', '网络维护,服务器运维', '机房日常值守、上机秩序维护与网络故障初判。', 31200, 104, '/uploads/seed/post/05.jpg', 'RECRUITING', '2026-06-17 10:00:15', '2026-06-07 09:20:56', '2026-10-24 15:00:46', 1),
(5, 'WS-2026-0075', '迎新志愿服务岗', 8, '志愿服务', '校园各迎新点', 8, 8, 18.0, '9 月 1 日-9 月 7 日全天', '沟通能力,体力', '迎新期间引导新生报到、搬运行李与咨询答疑。', 18600, 105, '/uploads/seed/post/06.jpg', 'FULL', '2026-06-23 10:00:52', '2026-06-13 09:20:33', '2026-10-23 15:00:22', 1),
(6, 'WS-2026-0076', '档案室数字化助理', 9, '助管', '档案馆 105', 2, 1, 22.0, '工作日 09:00-12:00', '文档整理,扫描设备', '纸质档案扫描、命名与目录校对。', 13600, 106, '/uploads/seed/post/01.jpg', 'RECRUITING', '2026-06-29 10:00:12', '2026-06-19 09:20:19', '2026-10-22 15:00:14', 1),
(7, 'WS-2026-0077', '体育场馆管理员', 10, '助管', '体育馆 1 号馆', 2, 2, 20.0, '周末 09:00-17:00', '责任心强,安全意识', '场馆开放管理、器材借还登记与安全检查。', 11200, 107, '/uploads/seed/post/02.jpg', 'FULL', '2026-07-05 10:00:41', '2026-06-25 09:20:35', '2026-10-21 15:00:21', 1),
(8, 'WS-2026-0078', '食堂文明督导', 7, '志愿服务', '第一食堂', 6, 4, 18.0, '工作日 11:30-13:00', '沟通能力', '就餐秩序引导、光盘行动宣传与意见收集。', 9600, 108, '/uploads/seed/post/03.jpg', 'FINISHED', '2026-07-11 10:00:20', '2026-07-01 09:20:52', '2026-10-20 15:00:11', 1),
(9, 'WS-2026-0079', '课程助教（数据结构）', 11, '助教', '计算机学院 A305', 2, 1, 26.0, '周二、周四 19:00-21:00', '数据结构,表达能力', '协助批改作业、答疑与实验课辅导。', 20800, 109, '/uploads/seed/post/04.jpg', 'RECRUITING', '2026-07-17 10:00:44', '2026-07-07 09:20:29', '2026-10-19 15:00:33', 1),
(10, 'WS-2026-0080', '实验室耗材管理', 4, '助管', '实验楼 A 座 201', 1, 0, 22.0, '工作日 09:00-12:00', 'Excel,细致耐心', '耗材出入库登记、库存盘点与采购申请整理。', 8800, 102, '/uploads/seed/post/05.jpg', 'RECRUITING', '2026-07-23 10:00:03', '2026-07-13 09:20:00', '2026-10-18 15:00:18', 1),
(11, 'WS-2026-0081', '校史馆讲解助理', 9, '志愿服务', '校史馆', 3, 2, 20.0, '周末 10:00-16:00', '普通话标准,表达能力', '校史馆参观接待与讲解。', 14400, 106, '/uploads/seed/post/06.jpg', 'FINISHED', '2026-07-29 10:00:48', '2026-07-19 09:20:31', '2026-10-17 15:00:49', 1),
(12, 'WS-2026-0082', '网络运维助理', 6, '助研', '信息楼 B105', 2, 0, 25.0, '工作日 15:00-18:00', '网络调试,Linux', '校园网终端故障处理与交换机日常巡检。', 15600, 104, '/uploads/seed/post/01.jpg', 'DRAFT', NULL, '2026-07-25 09:20:35', '2026-10-16 15:00:36', 1),
(13, 'WS-2026-0083', '图书馆书架整理', 3, '助管', '图书馆 2F', 3, 0, 20.0, '工作日 08:00-11:00', '体力,细致', '书架倒架、图书排序与破损图书登记。', 13200, 101, '/uploads/seed/post/02.jpg', 'PENDING', NULL, '2026-07-31 09:20:17', '2026-10-15 15:00:04', 1),
(14, 'WS-2026-0084', '就业中心信息录入', 8, '助管', '就业指导中心', 1, 0, 21.0, '工作日 14:00-17:00', 'Excel,数据录入', '招聘信息审核录入与企业联系台账维护。', 7560, 105, '/uploads/seed/post/03.jpg', 'PENDING', NULL, '2026-08-06 09:20:09', '2026-10-14 15:00:55', 1),
(15, 'WS-2026-0085', '宿舍安全检查助理', 7, '助管', '学生公寓 1-6 栋', 4, 1, 19.0, '每周二、周四 20:00-22:00', '责任心强', '宿舍安全隐患排查与记录上报。', 9120, 108, '/uploads/seed/post/04.jpg', 'RECRUITING', '2026-08-22 10:00:35', '2026-08-12 09:20:38', '2026-10-13 15:00:59', 1),
(16, 'WS-2026-0086', '科研数据标注', 4, '助研', '实验楼 C 座 502', 2, 1, 28.0, '时间灵活', 'Python,细致', '科研项目图像数据标注与质量抽检。', 22400, 110, '/uploads/seed/post/05.jpg', 'RECRUITING', '2026-08-28 10:00:05', '2026-08-18 09:20:48', '2026-10-12 15:00:35', 1);

INSERT INTO post_application (id, apply_no, post_id, student_id, apply_reason, available_time, resume_path, interview_time, match_score, status, create_time, update_time) VALUES
(1, 'AP-2026-0381', 1, 201, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周末全天', '/uploads/seed/evidence/01.jpg', NULL, NULL, 'SCREENING', '2026-05-09 09:00:16', '2026-07-23 16:00:29'),
(2, 'AP-2026-0382', 2, 204, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/02.jpg', NULL, NULL, 'SCREENING', '2026-05-14 10:07:13', '2026-07-26 16:00:39'),
(3, 'AP-2026-0383', 3, 207, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/03.jpg', '2026-07-19 14:00:13', 74.0, 'INTERVIEW', '2026-05-19 11:14:16', '2026-07-29 16:00:48'),
(4, 'AP-2026-0384', 4, 202, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', '2026-07-22 14:00:39', 86.2, 'INTERVIEW', '2026-05-24 12:21:10', '2026-08-01 16:00:41'),
(5, 'AP-2026-0385', 5, 205, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周末全天', '/uploads/seed/evidence/02.jpg', NULL, 77.1, 'EMPLOYED', '2026-05-29 13:28:48', '2026-08-04 16:00:05'),
(6, 'AP-2026-0386', 6, 208, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周二、周四 14:00 后', '/uploads/seed/evidence/03.jpg', NULL, 83.4, 'EMPLOYED', '2026-06-03 14:35:53', '2026-08-07 16:00:49'),
(7, 'AP-2026-0387', 7, 203, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周末全天', '/uploads/seed/evidence/01.jpg', NULL, 83.8, 'EMPLOYED', '2026-06-08 15:42:20', '2026-08-10 16:00:03'),
(8, 'AP-2026-0388', 8, 206, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/02.jpg', NULL, 65.7, 'REJECTED', '2026-06-13 16:49:02', '2026-08-13 16:00:15'),
(9, 'AP-2026-0389', 9, 201, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周一至周五 18:00 后', '/uploads/seed/evidence/03.jpg', NULL, NULL, 'SCREENING', '2026-06-18 09:56:21', '2026-08-16 16:00:16'),
(10, 'AP-2026-0390', 10, 204, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周一至周五 18:00 后', '/uploads/seed/evidence/01.jpg', NULL, NULL, 'SCREENING', '2026-06-23 10:04:38', '2026-08-19 16:00:23'),
(11, 'AP-2026-0391', 11, 207, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/02.jpg', '2026-08-12 14:00:52', 71.5, 'INTERVIEW', '2026-06-28 11:11:32', '2026-08-22 16:00:38'),
(12, 'AP-2026-0392', 12, 202, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周二、周四 14:00 后', '/uploads/seed/evidence/03.jpg', '2026-08-15 14:00:05', 88.4, 'INTERVIEW', '2026-07-03 12:18:15', '2026-08-25 16:00:52'),
(13, 'AP-2026-0393', 13, 205, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', NULL, 69.4, 'EMPLOYED', '2026-07-08 13:25:09', '2026-08-28 16:00:51'),
(14, 'AP-2026-0394', 14, 208, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/02.jpg', NULL, 88.7, 'EMPLOYED', '2026-07-13 14:32:12', '2026-08-31 16:00:41'),
(15, 'AP-2026-0395', 15, 203, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周一至周五 18:00 后', '/uploads/seed/evidence/03.jpg', NULL, 84.4, 'EMPLOYED', '2026-07-18 15:39:26', '2026-09-03 16:00:16'),
(16, 'AP-2026-0396', 16, 206, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周一至周五 18:00 后', '/uploads/seed/evidence/01.jpg', NULL, 78.0, 'REJECTED', '2026-07-23 16:46:18', '2026-09-06 16:00:13'),
(17, 'AP-2026-0397', 1, 202, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周末全天', '/uploads/seed/evidence/02.jpg', NULL, NULL, 'SCREENING', '2026-07-28 09:53:32', '2026-09-09 16:00:22'),
(18, 'AP-2026-0398', 2, 205, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周末全天', '/uploads/seed/evidence/03.jpg', NULL, NULL, 'SCREENING', '2026-08-02 10:01:53', '2026-09-12 16:00:26'),
(19, 'AP-2026-0399', 3, 208, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周一至周五 18:00 后', '/uploads/seed/evidence/01.jpg', '2026-09-05 14:00:17', 75.8, 'INTERVIEW', '2026-08-07 11:08:54', '2026-09-15 16:00:14'),
(20, 'AP-2026-0400', 4, 203, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周二、周四 14:00 后', '/uploads/seed/evidence/02.jpg', '2026-09-08 14:00:51', 70.7, 'INTERVIEW', '2026-08-12 12:15:24', '2026-09-18 16:00:35'),
(21, 'AP-2026-0401', 5, 206, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周末全天', '/uploads/seed/evidence/03.jpg', NULL, 80.3, 'EMPLOYED', '2026-08-17 13:22:08', '2026-09-21 16:00:15'),
(22, 'AP-2026-0402', 6, 201, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', NULL, 70.8, 'EMPLOYED', '2026-08-22 14:29:21', '2026-09-24 16:00:58'),
(23, 'AP-2026-0403', 7, 204, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周一至周五 18:00 后', '/uploads/seed/evidence/02.jpg', NULL, 87.3, 'EMPLOYED', '2026-08-27 15:36:40', '2026-09-27 16:00:28'),
(24, 'AP-2026-0404', 8, 207, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周一至周五 18:00 后', '/uploads/seed/evidence/03.jpg', NULL, 75.0, 'REJECTED', '2026-09-01 16:43:37', '2026-09-30 16:00:01'),
(25, 'AP-2026-0405', 9, 202, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', NULL, NULL, 'SCREENING', '2026-09-06 09:50:44', '2026-10-03 16:00:09'),
(26, 'AP-2026-0406', 10, 205, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/02.jpg', NULL, NULL, 'SCREENING', '2026-09-11 10:57:22', '2026-10-06 16:00:02'),
(27, 'AP-2026-0407', 11, 208, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周末全天', '/uploads/seed/evidence/03.jpg', '2026-09-29 14:00:50', 83.6, 'INTERVIEW', '2026-09-16 11:05:09', '2026-10-09 16:00:42'),
(28, 'AP-2026-0408', 12, 203, '本人具备岗位所需技能，时间安排稳定，愿意长期承担。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', '2026-10-02 14:00:20', 72.6, 'INTERVIEW', '2026-09-21 12:12:52', '2026-10-12 16:00:40'),
(29, 'AP-2026-0409', 13, 206, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周末全天', '/uploads/seed/evidence/02.jpg', NULL, 86.9, 'EMPLOYED', '2026-09-26 13:19:44', '2026-10-15 16:00:39'),
(30, 'AP-2026-0410', 14, 201, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周末全天', '/uploads/seed/evidence/03.jpg', NULL, 87.7, 'EMPLOYED', '2026-10-01 14:26:23', '2026-10-18 16:00:27'),
(31, 'AP-2026-0411', 15, 204, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', NULL, 70.8, 'EMPLOYED', '2026-10-06 15:33:00', '2026-10-21 16:00:44'),
(32, 'AP-2026-0412', 16, 207, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周一至周五 18:00 后', '/uploads/seed/evidence/02.jpg', NULL, 77.0, 'REJECTED', '2026-10-11 16:40:44', '2026-10-24 16:00:46'),
(33, 'AP-2026-0413', 1, 203, '对该岗位工作内容感兴趣，希望通过勤工助学提升综合能力。', '周一至周五 18:00 后', '/uploads/seed/evidence/03.jpg', NULL, NULL, 'SCREENING', '2026-10-16 09:47:49', '2026-10-27 16:00:15'),
(34, 'AP-2026-0414', 2, 206, '希望利用课余时间参与学校工作，减轻家庭负担并锻炼实践能力。', '周二、周四 14:00 后', '/uploads/seed/evidence/01.jpg', NULL, NULL, 'SCREENING', '2026-10-21 10:54:56', '2026-10-30 16:00:49');

INSERT INTO employment_record (id, post_id, application_id, student_id, teacher_id, employ_time, status, remark) VALUES
(1, 5, 5, 205, 101, '2026-08-04 16:00:05', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(2, 6, 6, 208, 101, '2026-08-07 16:00:49', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(3, 7, 7, 203, 101, '2026-08-10 16:00:03', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(4, 8, 8, 206, 101, '2026-08-13 16:00:15', 'REJECTED', '同期候选人匹配度更高，岗位名额已满'),
(5, 13, 13, 205, 101, '2026-08-28 16:00:51', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(6, 14, 14, 208, 101, '2026-08-31 16:00:41', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(7, 15, 15, 203, 101, '2026-09-03 16:00:16', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(8, 16, 16, 206, 101, '2026-09-06 16:00:13', 'REJECTED', '同期候选人匹配度更高，岗位名额已满'),
(9, 5, 21, 206, 101, '2026-09-21 16:00:15', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(10, 6, 22, 201, 101, '2026-09-24 16:00:58', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(11, 7, 23, 204, 101, '2026-09-27 16:00:28', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(12, 8, 24, 207, 101, '2026-09-30 16:00:01', 'REJECTED', '同期候选人匹配度更高，岗位名额已满'),
(13, 13, 29, 206, 101, '2026-10-15 16:00:39', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(14, 14, 30, 201, 101, '2026-10-18 16:00:27', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(15, 15, 31, 204, 101, '2026-10-21 16:00:44', 'EMPLOYED', '面试通过，技能与岗位匹配'),
(16, 16, 32, 207, 101, '2026-10-24 16:00:46', 'REJECTED', '同期候选人匹配度更高，岗位名额已满');

INSERT INTO work_shift (id, post_id, student_id, shift_date, start_time, end_time, work_place, plan_hours, conflict_flag, conflict_reason, status, create_time) VALUES
(1, 1, 201, '2026-10-31', '18:00', '22:00', '档案馆 105', 4.0, 1, '与《编译原理》晚课冲突', 'ADJUST', '2026-06-03 10:00:38'),
(2, 2, 202, '2026-10-29', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-06-05 10:00:39'),
(3, 3, 203, '2026-10-27', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-06-07 10:00:17'),
(4, 4, 204, '2026-10-25', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-06-09 10:00:00'),
(5, 5, 205, '2026-10-23', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-06-11 10:00:18'),
(6, 6, 206, '2026-10-21', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-06-13 10:00:03'),
(7, 7, 207, '2026-10-19', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-06-15 10:00:21'),
(8, 8, 208, '2026-10-17', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-06-17 10:00:08'),
(9, 9, 201, '2026-10-15', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-06-19 10:00:53'),
(10, 10, 202, '2026-10-13', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-06-21 10:00:09'),
(11, 11, 203, '2026-10-11', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-06-23 10:00:07'),
(12, 12, 204, '2026-10-09', '18:00', '22:00', '信息楼 B201 机房', 4.0, 1, '当日已有其他班次', 'ADJUST', '2026-06-25 10:00:07'),
(13, 13, 205, '2026-10-07', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-06-27 10:00:28'),
(14, 14, 206, '2026-10-05', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-06-29 10:00:05'),
(15, 15, 207, '2026-10-03', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-07-01 10:00:37'),
(16, 16, 208, '2026-10-01', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-07-03 10:00:38'),
(17, 1, 201, '2026-09-29', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-07-05 10:00:14'),
(18, 2, 202, '2026-09-27', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-07-07 10:00:14'),
(19, 3, 203, '2026-09-25', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-07-09 10:00:59'),
(20, 4, 204, '2026-09-23', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-07-11 10:00:22'),
(21, 5, 205, '2026-09-21', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-07-13 10:00:52'),
(22, 6, 206, '2026-09-19', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-07-15 10:00:13'),
(23, 7, 207, '2026-09-17', '18:00', '22:00', '实验楼 A 座 403', 4.0, 1, '与《编译原理》晚课冲突', 'ADJUST', '2026-07-17 10:00:58'),
(24, 8, 208, '2026-09-15', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-07-19 10:00:42'),
(25, 9, 201, '2026-09-13', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-07-21 10:00:18'),
(26, 10, 202, '2026-09-11', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-07-23 10:00:55'),
(27, 11, 203, '2026-09-09', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-07-25 10:00:50'),
(28, 12, 204, '2026-09-07', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-07-27 10:00:47'),
(29, 13, 205, '2026-09-05', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-07-29 10:00:45'),
(30, 14, 206, '2026-10-31', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-07-31 10:00:25'),
(31, 15, 207, '2026-10-29', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-08-02 10:00:47'),
(32, 16, 208, '2026-10-27', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-08-04 10:00:24'),
(33, 1, 201, '2026-10-25', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-08-06 10:00:56'),
(34, 2, 202, '2026-10-23', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 1, '当日已有其他班次', 'ADJUST', '2026-08-08 10:00:24'),
(35, 3, 203, '2026-10-21', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-08-10 10:00:01'),
(36, 4, 204, '2026-10-19', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-08-12 10:00:56'),
(37, 5, 205, '2026-10-17', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-08-14 10:00:05'),
(38, 6, 206, '2026-10-15', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-08-16 10:00:42'),
(39, 7, 207, '2026-10-13', '18:00', '22:00', '信息楼 B201 机房', 4.0, 0, NULL, 'CONFIRMED', '2026-08-18 10:00:03'),
(40, 8, 208, '2026-10-11', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-08-20 10:00:01'),
(41, 9, 201, '2026-10-09', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-08-22 10:00:00'),
(42, 10, 202, '2026-10-07', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 0, NULL, 'CONFIRMED', '2026-08-24 10:00:12'),
(43, 11, 203, '2026-10-05', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-08-26 10:00:09'),
(44, 12, 204, '2026-10-03', '18:00', '22:00', '实验楼 A 座 403', 4.0, 0, NULL, 'CONFIRMED', '2026-08-28 10:00:27'),
(45, 13, 205, '2026-10-01', '18:00', '22:00', '图书馆 3F 阅览室', 4.0, 1, '与《编译原理》晚课冲突', 'ADJUST', '2026-08-30 10:00:28'),
(46, 14, 206, '2026-09-29', '18:00', '22:00', '档案馆 105', 4.0, 0, NULL, 'CONFIRMED', '2026-09-01 10:00:56');

INSERT INTO attendance_record (id, shift_id, student_id, post_id, work_date, check_in_time, check_out_time, actual_hours, valid_hours, status, abnormal_reason, evidence_image, verify_status, create_time) VALUES
(1, 1, 201, 1, '2026-10-31', '2026-10-31 17:57:16', '2026-10-31 21:41:06', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-03 22:10:37'),
(2, 2, 202, 2, '2026-10-29', '2026-10-29 17:57:54', '2026-10-29 21:41:34', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-05 22:10:11'),
(3, 3, 203, 3, '2026-10-27', '2026-10-27 17:48:49', '2026-10-27 21:56:38', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-07 22:10:01'),
(4, 4, 204, 4, '2026-10-25', '2026-10-25 17:59:51', '2026-10-25 21:49:59', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-09 22:10:58'),
(5, 5, 205, 5, '2026-10-23', '2026-10-23 18:19:37', '2026-10-23 21:51:16', 4.0, 3.5, 'LATE', '迟到 9 分钟', '/uploads/seed/evidence/02.jpg', 'PASS', '2026-06-11 22:10:26'),
(6, 6, 206, 6, '2026-10-21', '2026-10-21 17:59:57', '2026-10-21 21:10:38', 3.8, 3.6, 'EARLY', '早退 12 分钟', NULL, 'PASS', '2026-06-13 22:10:50'),
(7, 7, 207, 7, '2026-10-19', NULL, NULL, 0, 0.0, 'ABSENT', '未签到且未请假', '/uploads/seed/evidence/01.jpg', 'PASS', '2026-06-15 22:10:29'),
(8, 8, 208, 8, '2026-10-17', NULL, NULL, 0, 0.0, 'LEAVE', '已提交请假单', NULL, 'PENDING', '2026-06-17 22:10:02'),
(9, 9, 201, 9, '2026-10-15', '2026-10-15 17:58:33', '2026-10-15 21:41:21', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-19 22:10:14'),
(10, 10, 202, 10, '2026-10-13', '2026-10-13 17:48:50', '2026-10-13 21:55:19', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-21 22:10:48'),
(11, 11, 203, 11, '2026-10-11', '2026-10-11 17:58:16', '2026-10-11 21:43:08', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-23 22:10:15'),
(12, 12, 204, 12, '2026-10-09', '2026-10-09 17:49:18', '2026-10-09 21:44:13', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-06-25 22:10:56'),
(13, 13, 205, 13, '2026-10-07', '2026-10-07 18:24:03', '2026-10-07 21:57:42', 4.0, 3.5, 'LATE', '迟到 9 分钟', '/uploads/seed/evidence/01.jpg', 'PASS', '2026-06-27 22:10:00'),
(14, 14, 206, 14, '2026-10-05', '2026-10-05 17:56:29', '2026-10-05 21:30:13', 3.8, 3.6, 'EARLY', '早退 12 分钟', NULL, 'PASS', '2026-06-29 22:10:44'),
(15, 15, 207, 15, '2026-10-03', NULL, NULL, 0, 0.0, 'ABSENT', '未签到且未请假', '/uploads/seed/evidence/03.jpg', 'PASS', '2026-07-01 22:10:01'),
(16, 16, 208, 16, '2026-10-01', NULL, NULL, 0, 0.0, 'LEAVE', '已提交请假单', NULL, 'PENDING', '2026-07-03 22:10:28'),
(17, 17, 201, 1, '2026-09-29', '2026-09-29 17:49:55', '2026-09-29 21:55:24', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-05 22:10:42'),
(18, 18, 202, 2, '2026-09-27', '2026-09-27 17:54:23', '2026-09-27 21:52:17', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-07 22:10:26'),
(19, 19, 203, 3, '2026-09-25', '2026-09-25 17:49:36', '2026-09-25 21:56:02', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-09 22:10:35'),
(20, 20, 204, 4, '2026-09-23', '2026-09-23 17:59:37', '2026-09-23 21:40:28', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-11 22:10:19'),
(21, 21, 205, 5, '2026-09-21', '2026-09-21 18:14:53', '2026-09-21 21:52:57', 4.0, 3.5, 'LATE', '迟到 9 分钟', '/uploads/seed/evidence/03.jpg', 'PENDING', '2026-07-13 22:10:52'),
(22, 22, 206, 6, '2026-09-19', '2026-09-19 17:55:55', '2026-09-19 21:24:18', 3.8, 3.6, 'EARLY', '早退 12 分钟', NULL, 'PASS', '2026-07-15 22:10:13'),
(23, 23, 207, 7, '2026-09-17', NULL, NULL, 0, 0.0, 'ABSENT', '未签到且未请假', '/uploads/seed/evidence/02.jpg', 'PASS', '2026-07-17 22:10:41'),
(24, 24, 208, 8, '2026-09-15', NULL, NULL, 0, 0.0, 'LEAVE', '已提交请假单', NULL, 'PASS', '2026-07-19 22:10:15'),
(25, 25, 201, 9, '2026-09-13', '2026-09-13 17:57:34', '2026-09-13 21:47:41', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-21 22:10:17'),
(26, 26, 202, 10, '2026-09-11', '2026-09-11 17:57:38', '2026-09-11 21:46:20', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-23 22:10:07'),
(27, 27, 203, 11, '2026-09-09', '2026-09-09 17:49:50', '2026-09-09 21:43:34', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-25 22:10:52'),
(28, 28, 204, 12, '2026-09-07', '2026-09-07 17:56:02', '2026-09-07 21:49:07', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-07-27 22:10:49'),
(29, 29, 205, 13, '2026-09-05', '2026-09-05 18:09:08', '2026-09-05 21:52:30', 4.0, 3.5, 'LATE', '迟到 9 分钟', '/uploads/seed/evidence/02.jpg', 'PASS', '2026-07-29 22:10:26'),
(30, 30, 206, 14, '2026-10-31', '2026-10-31 17:52:36', '2026-10-31 21:30:35', 3.8, 3.6, 'EARLY', '早退 12 分钟', NULL, 'PENDING', '2026-07-31 22:10:35'),
(31, 31, 207, 15, '2026-10-29', NULL, NULL, 0, 0.0, 'ABSENT', '未签到且未请假', '/uploads/seed/evidence/01.jpg', 'PENDING', '2026-08-02 22:10:00'),
(32, 32, 208, 16, '2026-10-27', NULL, NULL, 0, 0.0, 'LEAVE', '已提交请假单', NULL, 'PASS', '2026-08-04 22:10:58'),
(33, 33, 201, 1, '2026-10-25', '2026-10-25 17:52:17', '2026-10-25 21:50:52', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-06 22:10:04'),
(34, 34, 202, 2, '2026-10-23', '2026-10-23 17:55:41', '2026-10-23 21:48:43', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-08 22:10:18'),
(35, 35, 203, 3, '2026-10-21', '2026-10-21 17:55:45', '2026-10-21 21:46:47', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-10 22:10:48'),
(36, 36, 204, 4, '2026-10-19', '2026-10-19 17:53:14', '2026-10-19 21:57:13', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-12 22:10:11'),
(37, 37, 205, 5, '2026-10-17', '2026-10-17 18:14:04', '2026-10-17 21:59:40', 4.0, 3.5, 'LATE', '迟到 9 分钟', '/uploads/seed/evidence/01.jpg', 'PENDING', '2026-08-14 22:10:48'),
(38, 38, 206, 6, '2026-10-15', '2026-10-15 17:55:52', '2026-10-15 21:33:34', 3.8, 3.6, 'EARLY', '早退 12 分钟', NULL, 'PASS', '2026-08-16 22:10:43'),
(39, 39, 207, 7, '2026-10-13', NULL, NULL, 0, 0.0, 'ABSENT', '未签到且未请假', '/uploads/seed/evidence/03.jpg', 'PASS', '2026-08-18 22:10:32'),
(40, 40, 208, 8, '2026-10-11', NULL, NULL, 0, 0.0, 'LEAVE', '已提交请假单', NULL, 'PENDING', '2026-08-20 22:10:27'),
(41, 41, 201, 9, '2026-10-09', '2026-10-09 17:56:51', '2026-10-09 21:42:56', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-22 22:10:17'),
(42, 42, 202, 10, '2026-10-07', '2026-10-07 17:53:55', '2026-10-07 21:42:37', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-24 22:10:56'),
(43, 43, 203, 11, '2026-10-05', '2026-10-05 17:53:30', '2026-10-05 21:41:16', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-26 22:10:39'),
(44, 44, 204, 12, '2026-10-03', '2026-10-03 17:59:20', '2026-10-03 21:54:59', 4.0, 4.0, 'NORMAL', NULL, NULL, 'PASS', '2026-08-28 22:10:18'),
(45, 45, 205, 13, '2026-10-01', '2026-10-01 18:21:20', '2026-10-01 21:47:34', 4.0, 3.5, 'LATE', '迟到 9 分钟', '/uploads/seed/evidence/03.jpg', 'PASS', '2026-08-30 22:10:40'),
(46, 46, 206, 14, '2026-09-29', '2026-09-29 17:57:19', '2026-09-29 21:31:44', 3.8, 3.6, 'EARLY', '早退 12 分钟', NULL, 'PASS', '2026-09-01 22:10:21');

INSERT INTO hour_summary (id, student_id, post_id, summary_month, plan_hours, actual_hours, valid_hours, limit_hours, status, confirm_time, create_time) VALUES
(1, 201, 1, '2026-05', 44.0, 44.8, 40.0, 40.0, 'OVER_LIMIT', NULL, '2026-09-01 09:00:15'),
(2, 202, 2, '2026-05', 44.0, 44.0, 40.0, 40.0, 'OVER_LIMIT', NULL, '2026-09-01 09:00:51'),
(3, 203, 3, '2026-05', 28.0, 28.4, 28.4, 40.0, 'CONFIRMED', '2026-10-01 10:00:19', '2026-09-01 09:00:48'),
(4, 204, 4, '2026-05', 40.0, 40.4, 40.4, 40.0, 'CONFIRMED', '2026-10-01 10:00:37', '2026-09-01 09:00:39'),
(5, 205, 5, '2026-05', 28.0, 28.0, 28.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:57', '2026-09-01 09:00:36'),
(6, 206, 6, '2026-05', 28.0, 28.0, 28.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:17', '2026-09-01 09:00:14'),
(7, 207, 7, '2026-05', 24.0, 24.4, 24.4, 40.0, 'CONFIRMED', '2026-10-01 10:00:57', '2026-09-01 09:00:51'),
(8, 208, 8, '2026-05', 28.0, 28.8, 28.8, 40.0, 'CONFIRMED', '2026-10-01 10:00:58', '2026-09-01 09:00:23'),
(9, 201, 1, '2026-06', 24.0, 24.0, 24.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:35', '2026-09-01 09:00:35'),
(10, 202, 2, '2026-06', 36.0, 36.0, 36.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:37', '2026-09-01 09:00:34'),
(11, 203, 3, '2026-06', 44.0, 44.0, 40.0, 40.0, 'OVER_LIMIT', NULL, '2026-09-01 09:00:55'),
(12, 204, 4, '2026-06', 28.0, 28.0, 28.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:56', '2026-09-01 09:00:07'),
(13, 205, 5, '2026-06', 36.0, 36.0, 36.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:12', '2026-09-01 09:00:44'),
(14, 206, 6, '2026-06', 32.0, 32.4, 32.4, 40.0, 'CONFIRMED', '2026-10-01 10:00:17', '2026-09-01 09:00:17'),
(15, 207, 7, '2026-06', 40.0, 39.5, 39.5, 40.0, 'CONFIRMED', '2026-10-01 10:00:05', '2026-09-01 09:00:21'),
(16, 208, 8, '2026-06', 32.0, 32.4, 32.4, 40.0, 'CONFIRMED', '2026-10-01 10:00:10', '2026-09-01 09:00:20'),
(17, 201, 1, '2026-09', 32.0, 32.0, 32.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:08', '2026-09-01 09:00:24'),
(18, 202, 2, '2026-09', 44.0, 44.8, 40.0, 40.0, 'OVER_LIMIT', NULL, '2026-09-01 09:00:26'),
(19, 203, 3, '2026-09', 36.0, 35.5, 35.5, 40.0, 'CONFIRMED', '2026-10-01 10:00:43', '2026-09-01 09:00:31'),
(20, 204, 4, '2026-09', 32.0, 32.8, 32.8, 40.0, 'CONFIRMED', '2026-10-01 10:00:44', '2026-09-01 09:00:56'),
(21, 205, 5, '2026-09', 44.0, 44.4, 40.0, 40.0, 'OVER_LIMIT', NULL, '2026-09-01 09:00:21'),
(22, 206, 6, '2026-09', 36.0, 36.0, 36.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:58', '2026-09-01 09:00:03'),
(23, 207, 7, '2026-09', 24.0, 24.8, 24.8, 40.0, 'CONFIRMED', '2026-10-01 10:00:07', '2026-09-01 09:00:33'),
(24, 208, 8, '2026-09', 24.0, 24.0, 24.0, 40.0, 'CONFIRMED', '2026-10-01 10:00:26', '2026-09-01 09:00:12'),
(25, 201, 1, '2026-10', 24.0, 24.4, 24.4, 40.0, 'PENDING', NULL, '2026-09-01 09:00:22'),
(26, 202, 2, '2026-10', 40.0, 40.4, 40.4, 40.0, 'PENDING', NULL, '2026-09-01 09:00:37'),
(27, 203, 3, '2026-10', 32.0, 31.5, 31.5, 40.0, 'PENDING', NULL, '2026-09-01 09:00:58'),
(28, 204, 4, '2026-10', 32.0, 32.4, 32.4, 40.0, 'PENDING', NULL, '2026-09-01 09:00:21'),
(29, 205, 5, '2026-10', 40.0, 40.4, 40.4, 40.0, 'PENDING', NULL, '2026-09-01 09:00:47'),
(30, 206, 6, '2026-10', 44.0, 44.4, 40.0, 40.0, 'OVER_LIMIT', NULL, '2026-09-01 09:00:26'),
(31, 207, 7, '2026-10', 36.0, 36.4, 36.4, 40.0, 'PENDING', NULL, '2026-09-01 09:00:18'),
(32, 208, 8, '2026-10', 40.0, 39.5, 39.5, 40.0, 'PENDING', NULL, '2026-09-01 09:00:06');

INSERT INTO hour_appeal (id, summary_id, student_id, appeal_hours, reason, status, handle_time, handle_remark, create_time) VALUES
(1, 17, 202, 2.0, '10 月 22 日临时顶班未计入排班，实际到岗 4 小时', 'PENDING', NULL, NULL, '2026-10-27 11:08:15'),
(2, 9, 201, 0.5, '当日系统故障导致签到失败，有老师证明', 'PASS', '2026-10-28 15:00:40', '经核实予以补录 0.5 小时', '2026-10-25 09:12:13'),
(3, 4, 207, 1.5, '周末班次调换后未同步系统，实际出勤 5.5 小时', 'REJECT', '2026-10-21 10:00:21', '调换未走审批流程，不予认定', '2026-10-11 14:30:11');

INSERT INTO subsidy_batch (id, batch_no, semester_id, summary_month, person_count, total_hours, total_amount, status, audit_time, create_time) VALUES
(1, 'SB-2026-09-A', 1, '2026-09', 8, 271.2, 5836.8, 'PAID', '2026-09-21 10:00:20', '2026-09-16 09:00:32'),
(2, 'SB-2026-10-A', 1, '2026-10', 8, 289.3, 6248.4, 'AUDITING', NULL, '2026-10-26 09:00:13');

INSERT INTO subsidy_item (id, batch_id, student_id, post_id, valid_hours, hour_rate, factor, amount, pay_status, pay_time, fail_reason, create_time) VALUES
(1, 1, 201, 1, 29.8, 24.0, 1.15, 822.48, 'PAID', '2026-09-23 14:00:42', NULL, '2026-10-22 09:30:57'),
(2, 1, 202, 2, 30.5, 24.0, 1.15, 841.8, 'PAID', '2026-09-23 14:00:27', NULL, '2026-10-22 09:30:13'),
(3, 1, 203, 3, 39.2, 25.0, 1.2, 1176.0, 'PAID', '2026-09-23 14:00:35', NULL, '2026-10-22 09:30:26'),
(4, 1, 204, 4, 21.2, 20.0, 1.2, 508.8, 'PAID', '2026-09-23 14:00:55', NULL, '2026-10-22 09:30:41'),
(5, 1, 205, 5, 24.4, 20.0, 1.15, 561.2, 'PAID', '2026-09-23 14:00:57', NULL, '2026-10-22 09:30:47'),
(6, 1, 206, 6, 23.9, 24.0, 1.15, 659.64, 'PAID', '2026-09-23 14:00:41', NULL, '2026-10-22 09:30:33'),
(7, 1, 207, 7, 22.5, 24.0, 1.0, 540.0, 'PAID', '2026-09-23 14:00:52', NULL, '2026-10-22 09:30:38'),
(8, 1, 208, 8, 31.9, 22.0, 1.0, 701.8, 'PAID', '2026-09-23 14:00:08', NULL, '2026-10-22 09:30:42'),
(9, 2, 201, 9, 39.2, 25.0, 1.0, 980.0, 'WAIT', NULL, NULL, '2026-10-22 09:30:24'),
(10, 2, 202, 10, 28.9, 24.0, 1.15, 797.64, 'WAIT', NULL, NULL, '2026-10-22 09:30:40'),
(11, 2, 203, 11, 31.9, 24.0, 1.0, 765.6, 'WAIT', NULL, NULL, '2026-10-22 09:30:57'),
(12, 2, 204, 12, 32.7, 24.0, 1.15, 902.52, 'WAIT', NULL, NULL, '2026-10-22 09:30:47'),
(13, 2, 205, 13, 20.2, 20.0, 1.15, 464.6, 'FAIL', NULL, '银行卡信息有误，退回重发', '2026-10-22 09:30:20'),
(14, 2, 206, 14, 39.4, 22.0, 1.15, 996.82, 'WAIT', NULL, NULL, '2026-10-22 09:30:14'),
(15, 2, 207, 15, 36.9, 20.0, 1.2, 885.6, 'WAIT', NULL, NULL, '2026-10-22 09:30:25'),
(16, 2, 208, 16, 23.1, 24.0, 1.2, 665.28, 'WAIT', NULL, NULL, '2026-10-22 09:30:53');

INSERT INTO term_evaluation (id, student_id, post_id, semester_id, attendance_score, duty_score, skill_score, team_score, total_score, comment, feedback, status, create_time) VALUES
(1, 201, 1, 1, 27, 22, 24, 10, 83, '技能掌握较快，建议加强时间观念。', '岗位与专业相关，希望增加培训', 'WAIT_STUDENT', '2026-10-11 16:00:17'),
(2, 202, 2, 1, 24, 30, 22, 12, 88, '技能掌握较快，建议加强时间观念。', '工作强度适中，收获较大', 'DONE', '2026-10-12 16:00:38'),
(3, 203, 3, 1, 25, 21, 25, 12, 83, '工作主动，能与同学配合完成临时任务。', '工作强度适中，收获较大', 'WAIT_STUDENT', '2026-10-13 16:00:33'),
(4, 204, 4, 1, 27, 23, 23, 9, 82, '技能掌握较快，建议加强时间观念。', '岗位与专业相关，希望增加培训', 'WAIT_STUDENT', '2026-10-14 16:00:56'),
(5, 205, 5, 1, 22, 25, 24, 13, 84, '技能掌握较快，建议加强时间观念。', '排班较为集中，建议分散', 'WAIT_STUDENT', '2026-10-15 16:00:52'),
(6, 206, 6, 1, 26, 23, 22, 11, 82, '值守认真，借还登记准确，建议下学期继续留用。', '工作强度适中，收获较大', 'DONE', '2026-10-16 16:00:40'),
(7, 207, 7, 1, 28, 28, 23, 11, 90, '技能掌握较快，建议加强时间观念。', '排班较为集中，建议分散', 'WAIT_STUDENT', '2026-10-17 16:00:34'),
(8, 208, 8, 1, 27, 30, 20, 10, 87, '工作主动，能与同学配合完成临时任务。', '岗位与专业相关，希望增加培训', 'WAIT_STUDENT', '2026-10-18 16:00:39'),
(9, 201, 9, 1, 29, 27, 18, 14, 88, '技能掌握较快，建议加强时间观念。', '岗位与专业相关，希望增加培训', 'WAIT_STUDENT', '2026-10-19 16:00:17'),
(10, 202, 10, 1, 24, 26, 19, 11, 80, '技能掌握较快，建议加强时间观念。', '岗位与专业相关，希望增加培训', 'WAIT_STUDENT', '2026-10-20 16:00:12');

INSERT INTO match_rule (id, version, w_difficulty, w_conflict, w_skill, w_hours, w_absent, w_prefer, status, effect_time, creator, create_time) VALUES
(1, 'v2', 25, 20, 20, 15, 10, 10, 'ARCHIVED', '2026-03-01 00:00:00', '王敏', '2026-03-05 09:00:33'),
(2, 'v3', 30, 15, 20, 15, 10, 10, 'ACTIVE', '2026-09-01 00:00:00', '王敏', '2026-05-04 09:00:55');

INSERT INTO match_score (id, student_id, post_id, application_id, rule_version, score_difficulty, score_conflict, score_skill, score_hours, score_absent, score_prefer, total_score, grade, snapshot_json, adjust_grade, adjust_reason, adjust_by, create_time) VALUES
(1, 201, 1, 1, 'v3', 60, 90, 70, 70, 90, 50, 70.0, 'B', '{"difficulty":60,"conflict":90,"skill":70,"hours":70,"absent":90,"prefer":50}', NULL, NULL, NULL, '2026-09-11 16:20:06'),
(2, 202, 2, 2, 'v3', 60, 30, 50, 70, 90, 50, 57.0, 'D', '{"difficulty":60,"conflict":30,"skill":50,"hours":70,"absent":90,"prefer":50}', NULL, NULL, NULL, '2026-09-12 16:20:28'),
(3, 203, 3, 3, 'v3', 40, 30, 88, 50, 0, 75, 49.1, 'D', '{"difficulty":40,"conflict":30,"skill":88,"hours":50,"absent":0,"prefer":75}', NULL, NULL, NULL, '2026-09-13 16:20:30'),
(4, 204, 4, 4, 'v3', 40, 30, 88, 50, 90, 75, 58.1, 'D', '{"difficulty":40,"conflict":30,"skill":88,"hours":50,"absent":90,"prefer":75}', 'B', '面试沟通表达不足，暂列候补', '李强', '2026-09-14 16:20:05'),
(5, 205, 5, 5, 'v3', 40, 90, 70, 70, 90, 100, 69.0, 'C', '{"difficulty":40,"conflict":90,"skill":70,"hours":70,"absent":90,"prefer":100}', NULL, NULL, NULL, '2026-09-15 16:20:57'),
(6, 206, 6, 6, 'v3', 40, 90, 50, 85, 90, 100, 67.2, 'C', '{"difficulty":40,"conflict":90,"skill":50,"hours":85,"absent":90,"prefer":100}', NULL, NULL, NULL, '2026-09-16 16:20:23'),
(7, 207, 7, 7, 'v3', 60, 90, 96, 70, 90, 75, 77.7, 'B', '{"difficulty":60,"conflict":90,"skill":96,"hours":70,"absent":90,"prefer":75}', NULL, NULL, NULL, '2026-09-17 16:20:08'),
(8, 208, 8, 8, 'v3', 60, 90, 88, 70, 100, 75, 77.1, 'B', '{"difficulty":60,"conflict":90,"skill":88,"hours":70,"absent":100,"prefer":75}', NULL, NULL, NULL, '2026-09-18 16:20:40'),
(9, 201, 9, 9, 'v3', 40, 90, 50, 85, 0, 50, 53.2, 'D', '{"difficulty":40,"conflict":90,"skill":50,"hours":85,"absent":0,"prefer":50}', NULL, NULL, NULL, '2026-09-19 16:20:51'),
(10, 202, 10, 10, 'v3', 100, 90, 88, 85, 60, 75, 87.3, 'A', '{"difficulty":100,"conflict":90,"skill":88,"hours":85,"absent":60,"prefer":75}', NULL, NULL, NULL, '2026-09-20 16:20:13'),
(11, 203, 11, 11, 'v3', 100, 60, 96, 85, 0, 50, 76.0, 'B', '{"difficulty":100,"conflict":60,"skill":96,"hours":85,"absent":0,"prefer":50}', NULL, NULL, NULL, '2026-09-21 16:20:52'),
(12, 204, 12, 12, 'v3', 100, 30, 96, 85, 60, 100, 82.5, 'A', '{"difficulty":100,"conflict":30,"skill":96,"hours":85,"absent":60,"prefer":100}', NULL, NULL, NULL, '2026-09-22 16:20:40'),
(13, 205, 13, 13, 'v3', 40, 90, 50, 50, 100, 75, 60.5, 'C', '{"difficulty":40,"conflict":90,"skill":50,"hours":50,"absent":100,"prefer":75}', NULL, NULL, NULL, '2026-09-23 16:20:27'),
(14, 206, 14, 14, 'v3', 80, 90, 50, 85, 0, 100, 70.2, 'B', '{"difficulty":80,"conflict":90,"skill":50,"hours":85,"absent":0,"prefer":100}', NULL, NULL, NULL, '2026-09-24 16:20:56'),
(15, 207, 15, 15, 'v3', 40, 90, 88, 70, 100, 50, 68.6, 'C', '{"difficulty":40,"conflict":90,"skill":88,"hours":70,"absent":100,"prefer":50}', NULL, NULL, NULL, '2026-09-25 16:20:56'),
(16, 208, 16, 16, 'v3', 40, 60, 50, 85, 60, 100, 59.8, 'D', '{"difficulty":40,"conflict":60,"skill":50,"hours":85,"absent":60,"prefer":100}', NULL, NULL, NULL, '2026-09-26 16:20:24'),
(17, 201, 1, 17, 'v3', 60, 30, 50, 85, 0, 75, 52.8, 'D', '{"difficulty":60,"conflict":30,"skill":50,"hours":85,"absent":0,"prefer":75}', NULL, NULL, NULL, '2026-09-27 16:20:20'),
(18, 202, 2, 18, 'v3', 40, 60, 88, 70, 90, 75, 65.6, 'C', '{"difficulty":40,"conflict":60,"skill":88,"hours":70,"absent":90,"prefer":75}', NULL, NULL, NULL, '2026-09-28 16:20:04'),
(19, 203, 3, 19, 'v3', 60, 90, 88, 50, 100, 50, 71.6, 'B', '{"difficulty":60,"conflict":90,"skill":88,"hours":50,"absent":100,"prefer":50}', NULL, NULL, NULL, '2026-09-29 16:20:59'),
(20, 204, 4, 20, 'v3', 60, 60, 88, 70, 100, 50, 70.1, 'B', '{"difficulty":60,"conflict":60,"skill":88,"hours":70,"absent":100,"prefer":50}', NULL, NULL, NULL, '2026-09-30 16:20:35');

INSERT INTO work_study_log (id, biz_type, biz_no, from_status, to_status, action, reason, operator, create_time) VALUES
(1, 'APPLICATION', 'AP-2026-0381', 'SCREENING', 'EMPLOYED', '退回修改', '预算超限，退回调整', '周岚', '2026-07-03 10:05:02'),
(2, 'POST', 'WS-2026-0072', 'PENDING', 'PENDING', '发布', '岗位必要性强，同意发布', '刘颖', '2026-07-07 10:05:09'),
(3, 'POST', 'WS-2026-0073', 'SCREENING', 'RECRUITING', '录用', '岗位必要性强，同意发布', '刘颖', '2026-07-11 10:05:31'),
(4, 'APPLICATION', 'AP-2026-0384', 'SCREENING', 'PENDING', '驳回', '预算超限，退回调整', '周岚', '2026-07-15 10:05:54'),
(5, 'POST', 'WS-2026-0075', 'SCREENING', 'EMPLOYED', '审核通过', '预算超限，退回调整', '李强', '2026-07-19 10:05:39'),
(6, 'POST', 'WS-2026-0076', 'PENDING', 'PENDING', '审核通过', '岗位必要性强，同意发布', '刘颖', '2026-07-23 10:05:40'),
(7, 'APPLICATION', 'AP-2026-0387', 'PENDING', 'RECRUITING', '审核通过', '材料齐备，予以通过', '周岚', '2026-07-27 10:05:41'),
(8, 'POST', 'WS-2026-0078', 'PENDING', 'EMPLOYED', '驳回', NULL, '刘颖', '2026-07-31 10:05:07'),
(9, 'POST', 'WS-2026-0079', 'DRAFT', 'INTERVIEW', '退回修改', NULL, '李强', '2026-08-04 10:05:29'),
(10, 'APPLICATION', 'AP-2026-0390', 'SCREENING', 'INTERVIEW', '提交', '预算超限，退回调整', '王敏', '2026-08-08 10:05:51'),
(11, 'POST', 'WS-2026-0081', 'PENDING', 'RECRUITING', '驳回', '材料齐备，予以通过', '王敏', '2026-08-12 10:05:54'),
(12, 'POST', 'WS-2026-0082', 'PENDING', 'PENDING', '驳回', NULL, '李强', '2026-08-16 10:05:51'),
(13, 'APPLICATION', 'AP-2026-0393', 'SCREENING', 'INTERVIEW', '录用', '岗位必要性强，同意发布', '李强', '2026-08-20 10:05:56'),
(14, 'POST', 'WS-2026-0084', 'DRAFT', 'EMPLOYED', '退回修改', NULL, '刘颖', '2026-08-24 10:05:41'),
(15, 'POST', 'WS-2026-0085', 'PENDING', 'INTERVIEW', '录用', NULL, '李强', '2026-08-28 10:05:32'),
(16, 'APPLICATION', 'AP-2026-0396', 'SCREENING', 'RECRUITING', '退回修改', '岗位必要性强，同意发布', '周岚', '2026-09-01 10:05:06'),
(17, 'POST', 'WS-2026-0071', 'PENDING', 'INTERVIEW', '审核通过', NULL, '李强', '2026-09-05 10:05:37'),
(18, 'POST', 'WS-2026-0072', 'DRAFT', 'PENDING', '发布', '预算超限，退回调整', '刘颖', '2026-09-09 10:05:21'),
(19, 'APPLICATION', 'AP-2026-0399', 'PENDING', 'EMPLOYED', '录用', '材料齐备，予以通过', '周岚', '2026-09-13 10:05:28'),
(20, 'POST', 'WS-2026-0074', 'SCREENING', 'PENDING', '提交', NULL, '王敏', '2026-09-17 10:05:07'),
(21, 'POST', 'WS-2026-0075', 'SCREENING', 'RECRUITING', '审核通过', '岗位必要性强，同意发布', '刘颖', '2026-09-21 10:05:13'),
(22, 'APPLICATION', 'AP-2026-0402', 'DRAFT', 'EMPLOYED', '录用', '预算超限，退回调整', '周岚', '2026-09-25 10:05:39'),
(23, 'POST', 'WS-2026-0077', 'DRAFT', 'INTERVIEW', '录用', '预算超限，退回调整', '周岚', '2026-09-29 10:05:55'),
(24, 'POST', 'WS-2026-0078', 'DRAFT', 'RECRUITING', '提交', '岗位必要性强，同意发布', '王敏', '2026-10-03 10:05:39');

INSERT INTO sys_message (id, title, content, biz_type, biz_no, receiver_id, read_flag, create_time) VALUES
(1, '岗位待审批', '图书馆提交的「图书馆阅览室值班」等待审核，请及时处理。', 'POST', 'WS-2026-0071', 1, 0, '2026-10-30 09:12:23'),
(2, '工时申诉待处理', '陈思远提交 10 月工时申诉 2.0 小时，请在期限内复核。', 'APPEAL', 'APL-0001', 1, 0, '2026-10-27 11:10:45'),
(3, '补贴批次待审核', '10 月补贴批次 SB-2026-10-A 已生成，共 8 人。', 'SUBSIDY', 'SB-2026-10-A', 2, 0, '2026-10-26 09:05:22'),
(4, '面试通知', '您申请的「实验中心设备维护助理」面试时间为 11 月 2 日 14:00。', 'APPLICATION', 'AP-2026-0412', 201, 1, '2026-10-29 15:00:03'),
(5, '工时待确认', '10 月工时已汇总，请在 11 月 5 日前确认。', 'HOURS', '2026-10', 101, 0, '2026-10-28 08:40:52');

INSERT INTO sys_attachment (id, biz_type, biz_no, file_name, file_path, file_size, uploader_id, create_time) VALUES
(1, 'POST_DOC', 'WS-2026-0071', '岗位申请书.jpg', '/uploads/seed/evidence/01.jpg', 144258, 201, '2026-08-12 10:00:16'),
(2, 'STUDENT_PROOF', 'AP-2026-0382', '困难认定证明.jpg', '/uploads/seed/evidence/02.jpg', 216005, 202, '2026-08-16 10:00:46'),
(3, 'POST_DOC', 'WS-2026-0073', '困难认定证明.jpg', '/uploads/seed/evidence/03.jpg', 300845, 203, '2026-08-20 10:00:23'),
(4, 'STUDENT_PROOF', 'AP-2026-0384', '岗位申请书.jpg', '/uploads/seed/evidence/01.jpg', 365459, 204, '2026-08-24 10:00:22'),
(5, 'POST_DOC', 'WS-2026-0075', '学生证扫描件.jpg', '/uploads/seed/evidence/02.jpg', 231039, 205, '2026-08-28 10:00:18'),
(6, 'STUDENT_PROOF', 'AP-2026-0386', '困难认定证明.jpg', '/uploads/seed/evidence/03.jpg', 340542, 206, '2026-09-01 10:00:04'),
(7, 'POST_DOC', 'WS-2026-0077', '困难认定证明.jpg', '/uploads/seed/evidence/01.jpg', 300165, 207, '2026-09-05 10:00:00'),
(8, 'STUDENT_PROOF', 'AP-2026-0388', '困难认定证明.jpg', '/uploads/seed/evidence/02.jpg', 307219, 208, '2026-09-09 10:00:36'),
(9, 'POST_DOC', 'WS-2026-0079', '学生证扫描件.jpg', '/uploads/seed/evidence/03.jpg', 367429, 201, '2026-09-13 10:00:40'),
(10, 'STUDENT_PROOF', 'AP-2026-0390', '岗位申请书.jpg', '/uploads/seed/evidence/01.jpg', 323382, 202, '2026-09-17 10:00:50'),
(11, 'POST_DOC', 'WS-2026-0081', '岗位申请书.jpg', '/uploads/seed/evidence/02.jpg', 377397, 203, '2026-09-21 10:00:35'),
(12, 'STUDENT_PROOF', 'AP-2026-0392', '岗位申请书.jpg', '/uploads/seed/evidence/03.jpg', 226675, 204, '2026-09-25 10:00:43');

INSERT INTO sys_log (id, user_id, user_name, module, action, method, params, ip, cost_ms, create_time) VALUES
(1, 102, '周岚', '系统管理', '新增', '/api/application/employ', '{}', '127.0.0.1', 22, '2026-10-01 09:00:49'),
(2, 201, '刘颖', '补贴核算', '审批', '/api/post', '{}', '127.0.0.1', 421, '2026-10-02 10:01:46'),
(3, 102, '王敏', '录用管理', '导出', '/api/application/employ', '{}', '127.0.0.1', 118, '2026-10-03 11:02:43'),
(4, 2, '王敏', '考勤管理', '修改', '/api/application/employ', '{}', '127.0.0.1', 247, '2026-10-04 12:03:37'),
(5, 101, '李强', '补贴核算', '审批', '/api/attendance/verify', '{}', '127.0.0.1', 370, '2026-10-05 13:04:31'),
(6, 102, '刘颖', '系统管理', '导出', '/api/attendance/verify', '{}', '127.0.0.1', 222, '2026-10-06 14:05:56'),
(7, 1, '王敏', '系统管理', '导出', '/api/application/employ', '{}', '127.0.0.1', 229, '2026-10-07 15:06:47'),
(8, 1, '刘颖', '岗位管理', '导出', '/api/attendance/verify', '{}', '127.0.0.1', 264, '2026-10-08 16:07:34'),
(9, 2, '张一凡', '录用管理', '新增', '/api/subsidy/generate', '{}', '127.0.0.1', 380, '2026-10-09 17:08:26'),
(10, 102, '刘颖', '录用管理', '删除', '/api/post', '{}', '127.0.0.1', 341, '2026-10-10 18:09:58'),
(11, 2, '周岚', '考勤管理', '审批', '/api/application/employ', '{}', '127.0.0.1', 343, '2026-10-11 09:10:48'),
(12, 2, '李强', '系统管理', '审批', '/api/post', '{}', '127.0.0.1', 165, '2026-10-12 10:11:58'),
(13, 2, '李强', '补贴核算', '审批', '/api/application/employ', '{}', '127.0.0.1', 411, '2026-10-13 11:12:01'),
(14, 201, '周岚', '录用管理', '导出', '/api/post', '{}', '127.0.0.1', 306, '2026-10-14 12:13:04'),
(15, 101, '刘颖', '补贴核算', '导出', '/api/post', '{}', '127.0.0.1', 316, '2026-10-15 13:14:46'),
(16, 102, '张一凡', '考勤管理', '审批', '/api/attendance/verify', '{}', '127.0.0.1', 417, '2026-10-16 14:15:08'),
(17, 201, '王敏', '系统管理', '导出', '/api/post', '{}', '127.0.0.1', 343, '2026-10-17 15:16:50'),
(18, 201, '王敏', '系统管理', '导出', '/api/attendance/verify', '{}', '127.0.0.1', 422, '2026-10-18 16:17:10'),
(19, 2, '王敏', '考勤管理', '修改', '/api/application/employ', '{}', '127.0.0.1', 281, '2026-10-19 17:18:12'),
(20, 1, '刘颖', '录用管理', '审批', '/api/attendance/verify', '{}', '127.0.0.1', 300, '2026-10-20 18:19:58'),
(21, 101, '张一凡', '考勤管理', '审批', '/api/post', '{}', '127.0.0.1', 90, '2026-10-21 09:20:16'),
(22, 2, '张一凡', '岗位管理', '审批', '/api/post', '{}', '127.0.0.1', 287, '2026-10-22 10:21:18'),
(23, 101, '周岚', '录用管理', '修改', '/api/attendance/verify', '{}', '127.0.0.1', 93, '2026-10-23 11:22:11'),
(24, 1, '刘颖', '补贴核算', '删除', '/api/attendance/verify', '{}', '127.0.0.1', 408, '2026-10-24 12:23:02'),
(25, 102, '周岚', '录用管理', '删除', '/api/application/employ', '{}', '127.0.0.1', 356, '2026-10-25 13:24:00'),
(26, 2, '刘颖', '岗位管理', '审批', '/api/application/employ', '{}', '127.0.0.1', 281, '2026-10-26 14:25:59'),
(27, 2, '李强', '系统管理', '修改', '/api/attendance/verify', '{}', '127.0.0.1', 60, '2026-10-27 15:26:10'),
(28, 102, '刘颖', '补贴核算', '删除', '/api/post', '{}', '127.0.0.1', 89, '2026-10-28 16:27:23'),
(29, 102, '王敏', '系统管理', '删除', '/api/post', '{}', '127.0.0.1', 245, '2026-10-29 17:28:54'),
(30, 201, '王敏', '考勤管理', '审批', '/api/attendance/verify', '{}', '127.0.0.1', 289, '2026-10-30 18:29:45'),
(31, 2, '李强', '录用管理', '审批', '/api/post', '{}', '127.0.0.1', 280, '2026-10-01 09:30:51'),
(32, 101, '刘颖', '补贴核算', '新增', '/api/post', '{}', '127.0.0.1', 249, '2026-10-02 10:31:05'),
(33, 201, '李强', '考勤管理', '修改', '/api/application/employ', '{}', '127.0.0.1', 455, '2026-10-03 11:32:00'),
(34, 201, '刘颖', '补贴核算', '新增', '/api/attendance/verify', '{}', '127.0.0.1', 358, '2026-10-04 12:33:19'),
(35, 201, '刘颖', '录用管理', '审批', '/api/post', '{}', '127.0.0.1', 348, '2026-10-05 13:34:18'),
(36, 201, '刘颖', '录用管理', '删除', '/api/subsidy/generate', '{}', '127.0.0.1', 77, '2026-10-06 14:35:42'),
(37, 2, '李强', '系统管理', '审批', '/api/attendance/verify', '{}', '127.0.0.1', 273, '2026-10-07 15:36:35'),
(38, 101, '李强', '考勤管理', '审批', '/api/application/employ', '{}', '127.0.0.1', 217, '2026-10-08 16:37:38'),
(39, 102, '刘颖', '录用管理', '新增', '/api/subsidy/generate', '{}', '127.0.0.1', 339, '2026-10-09 17:38:10'),
(40, 1, '李强', '岗位管理', '修改', '/api/post', '{}', '127.0.0.1', 253, '2026-10-10 18:39:50');

UPDATE post_application a JOIN match_score s ON s.application_id = a.id
SET a.match_score = s.total_score WHERE a.match_score IS NULL;

SET FOREIGN_KEY_CHECKS = 1;
