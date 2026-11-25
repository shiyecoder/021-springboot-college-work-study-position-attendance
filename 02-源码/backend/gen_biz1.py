# -*- coding: utf-8 -*-
"""NEW-021 业务控制器：岗位/申请/排班/考勤/工时/补贴/匹配/看板/文件/菜单/角色/消息/用户。"""
import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "main" / "java" / "com" / "grad" / "ws"
PKG = "com.grad.ws"
FILES = {}


def add(rel, code):
    FILES[rel] = code.strip() + "\n"


# ---------------- 岗位 ----------------
add("src/main/java/com/grad/ws/controller/PostController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.BizException;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.*;
import com.grad.ws.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 勤工助学岗位：分页、详情、增改删、状态流转。
 * 状态机：DRAFT → PENDING → RECRUITING → FULL → FINISHED，PENDING 可 REJECTED 退回草稿。
 */
@RestController
@RequestMapping("/api/post")
public class PostController {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final Map<String, List<String>> FLOW = new HashMap<>();

    static {
        FLOW.put("DRAFT", List.of("PENDING"));
        FLOW.put("PENDING", List.of("RECRUITING", "REJECTED"));
        FLOW.put("REJECTED", List.of("DRAFT", "PENDING"));
        FLOW.put("RECRUITING", List.of("FULL", "FINISHED"));
        FLOW.put("FULL", List.of("FINISHED", "RECRUITING"));
    }

    private final WorkStudyPostMapper postMapper;
    private final SysOrgMapper orgMapper;
    private final SysUserMapper userMapper;
    private final WorkStudyLogMapper logMapper;
    private final PostApplicationMapper appMapper;

    public PostController(WorkStudyPostMapper postMapper, SysOrgMapper orgMapper, SysUserMapper userMapper,
                          WorkStudyLogMapper logMapper, PostApplicationMapper appMapper) {
        this.postMapper = postMapper;
        this.orgMapper = orgMapper;
        this.userMapper = userMapper;
        this.logMapper = logMapper;
        this.appMapper = appMapper;
    }

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) String kw,
                                                   @RequestParam(required = false) String status,
                                                   @RequestParam(required = false) Long deptId,
                                                   @RequestParam(required = false) String postType,
                                                   @RequestParam(required = false) String workPeriod) {
        QueryWrapper<WorkStudyPost> w = new QueryWrapper<>();
        if (kw != null && !kw.isBlank()) {
            w.and(x -> x.like("post_name", kw).or().like("post_no", kw));
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        if (postType != null && !postType.isBlank()) {
            w.eq("post_type", postType);
        }
        if (workPeriod != null && !workPeriod.isBlank()) {
            w.like("work_period", workPeriod);
        }
        // 数据范围：用工老师只看本部门，管理员/财务看全部
        if (UserContext.isDept()) {
            w.eq("dept_id", UserContext.orgId());
        } else if (deptId != null) {
            w.eq("dept_id", deptId);
        }
        w.orderByDesc("update_time");
        Page<WorkStudyPost> p = postMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (WorkStudyPost post : p.getRecords()) {
            list.add(enrich(post));
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    /** 学生岗位广场：只返回招聘中 */
    @GetMapping("/square")
    public R<PageResult<Map<String, Object>>> square(@RequestParam(defaultValue = "1") long page,
                                                     @RequestParam(defaultValue = "10") long size,
                                                     @RequestParam(required = false) String kw,
                                                     @RequestParam(required = false) Long deptId,
                                                     @RequestParam(required = false) String postType) {
        QueryWrapper<WorkStudyPost> w = new QueryWrapper<WorkStudyPost>().eq("status", "RECRUITING");
        if (kw != null && !kw.isBlank()) {
            w.and(x -> x.like("post_name", kw).or().like("post_no", kw));
        }
        if (deptId != null) {
            w.eq("dept_id", deptId);
        }
        if (postType != null && !postType.isBlank()) {
            w.eq("post_type", postType);
        }
        w.orderByDesc("publish_time");
        Page<WorkStudyPost> p = postMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (WorkStudyPost post : p.getRecords()) {
            Map<String, Object> m = enrich(post);
            Long cnt = appMapper.selectCount(new QueryWrapper<PostApplication>()
                    .eq("post_id", post.getId()).ne("status", "WITHDRAWN"));
            m.put("applyCount", cnt);
            list.add(m);
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        WorkStudyPost post = postMapper.selectById(id);
        if (post == null) {
            throw new BizException("岗位不存在");
        }
        Map<String, Object> m = enrich(post);
        List<WorkStudyLog> logs = logMapper.selectList(new QueryWrapper<WorkStudyLog>()
                .eq("biz_type", "POST").eq("biz_no", post.getPostNo()).orderByDesc("create_time"));
        m.put("timeline", logs);
        m.put("applyCount", appMapper.selectCount(new QueryWrapper<PostApplication>().eq("post_id", id)));
        return R.ok(m);
    }

    @PostMapping
    public R<WorkStudyPost> save(@RequestBody WorkStudyPost body) {
        checkRequired(body);
        if (body.getPostNo() == null || body.getPostNo().isBlank()) {
            body.setPostNo(nextNo());
        }
        body.setPostNo(body.getPostNo().trim());
        if (postMapper.selectCount(new QueryWrapper<WorkStudyPost>().eq("post_no", body.getPostNo())) > 0) {
            throw new BizException("岗位编号已存在，请更换");
        }
        body.setHiredNum(0);
        body.setStatus("DRAFT");
        body.setVersion(0);
        if (UserContext.isDept()) {
            body.setDeptId(UserContext.orgId());
        }
        postMapper.insert(body);
        writeLog(body.getPostNo(), null, "DRAFT", "新建", "创建岗位草稿");
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<WorkStudyPost> update(@PathVariable Long id, @RequestBody WorkStudyPost body) {
        WorkStudyPost old = postMapper.selectById(id);
        if (old == null) {
            throw new BizException("岗位不存在");
        }
        // 乐观锁：版本号不一致说明已被他人修改
        if (body.getVersion() != null && old.getVersion() != null && !body.getVersion().equals(old.getVersion())) {
            throw new BizException("数据已被他人更新，请刷新后重试");
        }
        if (!"DRAFT".equals(old.getStatus()) && !"REJECTED".equals(old.getStatus()) && !"RECRUITING".equals(old.getStatus())) {
            throw new BizException("当前状态不允许编辑");
        }
        checkRequired(body);
        body.setId(id);
        body.setVersion((old.getVersion() == null ? 0 : old.getVersion()) + 1);
        body.setHiredNum(old.getHiredNum());
        postMapper.updateById(body);
        writeLog(old.getPostNo(), old.getStatus(), old.getStatus(), "修改", "更新岗位信息");
        return R.ok(body);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        Long used = appMapper.selectCount(new QueryWrapper<PostApplication>().eq("post_id", id));
        if (used != null && used > 0) {
            throw new BizException("该岗位已有申请记录，不能删除，请改为结束岗位");
        }
        WorkStudyPost old = postMapper.selectById(id);
        postMapper.deleteById(id);
        if (old != null) {
            writeLog(old.getPostNo(), old.getStatus(), "DELETED", "删除", "删除岗位");
        }
        return R.ok();
    }

    /** 状态流转：校验目标状态是否在允许集合内，并留痕 */
    @PostMapping("/{id}/transition")
    public R<Void> transition(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String to = body.get("toStatus");
        String reason = body.get("reason");
        WorkStudyPost post = postMapper.selectById(id);
        if (post == null) {
            throw new BizException("岗位不存在");
        }
        List<String> allowed = FLOW.getOrDefault(post.getStatus(), List.of());
        if (!allowed.contains(to)) {
            throw new BizException("当前状态「" + post.getStatus() + "」不允许流转到「" + to + "」");
        }
        if (("REJECTED".equals(to) || "FINISHED".equals(to)) && (reason == null || reason.trim().length() < 5)) {
            throw new BizException("驳回或结束必须填写不少于 5 个字的原因");
        }
        WorkStudyPost up = new WorkStudyPost();
        up.setId(id);
        up.setStatus(to);
        if ("RECRUITING".equals(to)) {
            up.setPublishTime(LocalDateTime.now());
        }
        postMapper.updateById(up);
        writeLog(post.getPostNo(), post.getStatus(), to, "流转", reason);
        return R.ok();
    }

    private void checkRequired(WorkStudyPost b) {
        if (b.getPostName() == null || b.getPostName().isBlank()) {
            throw new BizException("岗位名称必填");
        }
        if (b.getWorkPlace() == null || b.getWorkPlace().isBlank()) {
            throw new BizException("工作地点必填");
        }
        if (b.getRecruitNum() == null || b.getRecruitNum() <= 0) {
            throw new BizException("招聘人数必须大于 0");
        }
        if (b.getHourRate() == null || b.getHourRate().signum() <= 0) {
            throw new BizException("时薪标准必填");
        }
        if (b.getWorkPeriod() != null && b.getWorkPeriod().length() > 100) {
            throw new BizException("工作时段最多 100 个字符");
        }
        if (b.getAbilityReq() != null && b.getAbilityReq().length() > 100) {
            throw new BizException("能力要求最多 100 个字符");
        }
    }

    private String nextNo() {
        return "WS-2026-" + String.format("%04d", 100 + (int) (postMapper.selectCount(null) + 1));
    }

    private void writeLog(String no, String from, String to, String action, String reason) {
        WorkStudyLog log = new WorkStudyLog();
        log.setBizType("POST");
        log.setBizNo(no);
        log.setFromStatus(from);
        log.setToStatus(to);
        log.setAction(action);
        log.setReason(reason);
        log.setOperator(UserContext.name());
        logMapper.insert(log);
    }

    private Map<String, Object> enrich(WorkStudyPost p) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", p.getId());
        m.put("postNo", p.getPostNo());
        m.put("postName", p.getPostName());
        m.put("deptId", p.getDeptId());
        SysOrg org = p.getDeptId() == null ? null : orgMapper.selectById(p.getDeptId());
        m.put("deptName", org == null ? "-" : org.getOrgName());
        m.put("postType", p.getPostType());
        m.put("workPlace", p.getWorkPlace());
        m.put("recruitNum", p.getRecruitNum());
        m.put("hiredNum", p.getHiredNum());
        m.put("hourRate", p.getHourRate());
        m.put("workPeriod", p.getWorkPeriod());
        m.put("abilityReq", p.getAbilityReq());
        m.put("postDesc", p.getPostDesc());
        m.put("budget", p.getBudget());
        SysUser t = p.getTeacherId() == null ? null : userMapper.selectById(p.getTeacherId());
        m.put("teacherName", t == null ? "-" : t.getRealName());
        m.put("coverImage", p.getCoverImage());
        m.put("status", p.getStatus());
        m.put("publishTime", p.getPublishTime() == null ? null : p.getPublishTime().format(DTF));
        m.put("version", p.getVersion());
        m.put("createTime", p.getCreateTime() == null ? null : p.getCreateTime().format(DTF));
        m.put("updateTime", p.getUpdateTime() == null ? null : p.getUpdateTime().format(DTF));
        return m;
    }
}""")

# ---------------- 申请与录用 ----------------
add("src/main/java/com/grad/ws/controller/ApplicationController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.BizException;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.*;
import com.grad.ws.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 岗位申请与录用：学生提交/撤回，老师筛选/面试/录用/驳回。
 * 录用前必须校验：岗位状态为招聘中、已录用人数 < 招聘人数。
 */
@RestController
@RequestMapping("/api/application")
public class ApplicationController {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final PostApplicationMapper appMapper;
    private final WorkStudyPostMapper postMapper;
    private final SysUserMapper userMapper;
    private final SysOrgMapper orgMapper;
    private final StudentProfileMapper profileMapper;
    private final EmploymentRecordMapper empMapper;
    private final WorkStudyLogMapper logMapper;

    public ApplicationController(PostApplicationMapper appMapper, WorkStudyPostMapper postMapper,
                                 SysUserMapper userMapper, SysOrgMapper orgMapper,
                                 StudentProfileMapper profileMapper, EmploymentRecordMapper empMapper,
                                 WorkStudyLogMapper logMapper) {
        this.appMapper = appMapper;
        this.postMapper = postMapper;
        this.userMapper = userMapper;
        this.orgMapper = orgMapper;
        this.profileMapper = profileMapper;
        this.empMapper = empMapper;
        this.logMapper = logMapper;
    }

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) String kw,
                                                   @RequestParam(required = false) String status,
                                                   @RequestParam(required = false) Long postId,
                                                   @RequestParam(defaultValue = "false") boolean mine) {
        QueryWrapper<PostApplication> w = new QueryWrapper<>();
        if (mine || UserContext.isStudent()) {
            w.eq("student_id", UserContext.userId());
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        if (postId != null) {
            w.eq("post_id", postId);
        }
        w.orderByDesc("update_time");
        Page<PostApplication> p = appMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (PostApplication a : p.getRecords()) {
            Map<String, Object> m = enrich(a);
            if (kw != null && !kw.isBlank()) {
                String hit = (String.valueOf(m.get("studentName")) + m.get("postName") + m.get("applyNo"));
                if (!hit.contains(kw)) {
                    continue;
                }
            }
            list.add(m);
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    /** 同岗位候选人对比：按匹配分降序，供录用审核台使用 */
    @GetMapping("/compare")
    public R<List<Map<String, Object>>> compare(@RequestParam Long postId) {
        List<PostApplication> apps = appMapper.selectList(new QueryWrapper<PostApplication>()
                .eq("post_id", postId).notIn("status", "WITHDRAWN").orderByDesc("match_score"));
        List<Map<String, Object>> out = new ArrayList<>();
        int rank = 1;
        for (PostApplication a : apps) {
            Map<String, Object> m = enrich(a);
            m.put("rank", rank++);
            out.add(m);
        }
        return R.ok(out);
    }

    @PostMapping
    public R<PostApplication> apply(@RequestBody PostApplication body) {
        WorkStudyPost post = postMapper.selectById(body.getPostId());
        if (post == null) {
            throw new BizException("岗位不存在");
        }
        if (!"RECRUITING".equals(post.getStatus())) {
            throw new BizException("该岗位当前不在招聘中");
        }
        Long dup = appMapper.selectCount(new QueryWrapper<PostApplication>()
                .eq("post_id", body.getPostId()).eq("student_id", UserContext.userId())
                .notIn("status", "WITHDRAWN", "REJECTED"));
        if (dup != null && dup > 0) {
            throw new BizException("您已申请过该岗位，请勿重复提交");
        }
        body.setApplyNo("AP-2026-" + String.format("%04d", 500 + (int) (appMapper.selectCount(null) + 1)));
        body.setStudentId(UserContext.userId());
        body.setStatus("SCREENING");
        appMapper.insert(body);
        writeLog(body.getApplyNo(), null, "SCREENING", "提交申请", "学生提交岗位申请");
        return R.ok(body);
    }

    @PostMapping("/{id}/withdraw")
    public R<Void> withdraw(@PathVariable Long id) {
        PostApplication a = appMapper.selectById(id);
        if (a == null) {
            throw new BizException("申请不存在");
        }
        if (!"SCREENING".equals(a.getStatus()) && !"INTERVIEW".equals(a.getStatus())) {
            throw new BizException("当前状态不可撤回（仅待筛选/待面试可撤回）");
        }
        PostApplication up = new PostApplication();
        up.setId(id);
        up.setStatus("WITHDRAWN");
        appMapper.updateById(up);
        writeLog(a.getApplyNo(), a.getStatus(), "WITHDRAWN", "撤回", "学生主动撤回申请");
        return R.ok();
    }

    @PostMapping("/{id}/screen")
    public R<Void> screen(@PathVariable Long id, @RequestBody(required = false) Map<String, String> body) {
        PostApplication a = appMapper.selectById(id);
        if (a == null || !"SCREENING".equals(a.getStatus())) {
            throw new BizException("只有待筛选的申请可以进入面试");
        }
        PostApplication up = new PostApplication();
        up.setId(id);
        up.setStatus("INTERVIEW");
        if (body != null && body.get("interviewTime") != null && !body.get("interviewTime").isBlank()) {
            up.setInterviewTime(LocalDateTime.parse(body.get("interviewTime"), DTF));
        }
        appMapper.updateById(up);
        writeLog(a.getApplyNo(), "SCREENING", "INTERVIEW", "筛选通过", "资格符合，安排面试");
        return R.ok();
    }

    @PostMapping("/{id}/reject")
    public R<Void> reject(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String reason = body == null ? null : body.get("reason");
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException("驳回必须填写不少于 5 个字的原因");
        }
        PostApplication a = appMapper.selectById(id);
        if (a == null) {
            throw new BizException("申请不存在");
        }
        PostApplication up = new PostApplication();
        up.setId(id);
        up.setStatus("REJECTED");
        appMapper.updateById(up);
        record(a, "REJECTED", reason);
        writeLog(a.getApplyNo(), a.getStatus(), "REJECTED", "驳回", reason);
        return R.ok();
    }

    /** 录用：校验招聘人数上限，超员直接拒绝，不做静默截断 */
    @PostMapping("/{id}/employ")
    public R<Void> employ(@PathVariable Long id, @RequestBody(required = false) Map<String, String> body) {
        PostApplication a = appMapper.selectById(id);
        if (a == null) {
            throw new BizException("申请不存在");
        }
        WorkStudyPost post = postMapper.selectById(a.getPostId());
        if (post == null) {
            throw new BizException("岗位不存在");
        }
        int hired = post.getHiredNum() == null ? 0 : post.getHiredNum();
        if (hired >= post.getRecruitNum()) {
            throw new BizException("该岗位已录满（" + post.getRecruitNum() + " 人），不得继续录用");
        }
        PostApplication up = new PostApplication();
        up.setId(id);
        up.setStatus("EMPLOYED");
        appMapper.updateById(up);

        WorkStudyPost pu = new WorkStudyPost();
        pu.setId(post.getId());
        pu.setHiredNum(hired + 1);
        pu.setStatus(hired + 1 >= post.getRecruitNum() ? "FULL" : "RECRUITING");
        postMapper.updateById(pu);

        record(a, "EMPLOYED", body == null ? null : body.get("remark"));
        writeLog(a.getApplyNo(), a.getStatus(), "EMPLOYED", "录用", "面试通过，办理录用");
        return R.ok();
    }

    private void record(PostApplication a, String status, String remark) {
        EmploymentRecord r = new EmploymentRecord();
        r.setPostId(a.getPostId());
        r.setApplicationId(a.getId());
        r.setStudentId(a.getStudentId());
        r.setTeacherId(UserContext.userId());
        r.setEmployTime(LocalDateTime.now());
        r.setStatus(status);
        r.setRemark(remark);
        empMapper.insert(r);
    }

    private void writeLog(String no, String from, String to, String action, String reason) {
        WorkStudyLog log = new WorkStudyLog();
        log.setBizType("APPLICATION");
        log.setBizNo(no);
        log.setFromStatus(from);
        log.setToStatus(to);
        log.setAction(action);
        log.setReason(reason);
        log.setOperator(UserContext.name());
        logMapper.insert(log);
    }

    private Map<String, Object> enrich(PostApplication a) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", a.getId());
        m.put("applyNo", a.getApplyNo());
        m.put("postId", a.getPostId());
        WorkStudyPost post = postMapper.selectById(a.getPostId());
        m.put("postName", post == null ? "-" : post.getPostName());
        m.put("deptName", post == null ? "-" : orgName(post.getDeptId()));
        m.put("hourRate", post == null ? null : post.getHourRate());
        m.put("studentId", a.getStudentId());
        SysUser s = userMapper.selectById(a.getStudentId());
        m.put("studentName", s == null ? "-" : s.getRealName());
        m.put("studentNo", s == null ? "-" : s.getStudentNo());
        m.put("avatar", s == null ? null : s.getAvatar());
        StudentProfile pf = profileMapper.selectOne(new QueryWrapper<StudentProfile>()
                .eq("user_id", a.getStudentId()).last("limit 1"));
        m.put("college", pf == null ? "-" : pf.getCollege());
        m.put("difficultyLevel", pf == null ? null : pf.getDifficultyLevel());
        m.put("applyReason", a.getApplyReason());
        m.put("availableTime", a.getAvailableTime());
        m.put("resumePath", a.getResumePath());
        m.put("interviewTime", a.getInterviewTime() == null ? null : a.getInterviewTime().format(DTF));
        m.put("matchScore", a.getMatchScore());
        m.put("status", a.getStatus());
        m.put("createTime", a.getCreateTime() == null ? null : a.getCreateTime().format(DTF));
        m.put("updateTime", a.getUpdateTime() == null ? null : a.getUpdateTime().format(DTF));
        return m;
    }

    private String orgName(Long id) {
        if (id == null) {
            return "-";
        }
        SysOrg o = orgMapper.selectById(id);
        return o == null ? "-" : o.getOrgName();
    }
}""")

# ---------------- 排班 ----------------
add("src/main/java/com/grad/ws/controller/ShiftController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.BizException;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.*;
import com.grad.ws.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 排班管理：按周维护班次，后端校验两类冲突
 * 1) 同一学生同一天存在重叠时段（已有班次）
 * 2) 与学生在档案中登记的可用时段不匹配（模拟课程冲突）
 */
@RestController
@RequestMapping("/api/shift")
public class ShiftController {

    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final WorkShiftMapper shiftMapper;
    private final WorkStudyPostMapper postMapper;
    private final SysUserMapper userMapper;
    private final StudentProfileMapper profileMapper;

    public ShiftController(WorkShiftMapper shiftMapper, WorkStudyPostMapper postMapper,
                           SysUserMapper userMapper, StudentProfileMapper profileMapper) {
        this.shiftMapper = shiftMapper;
        this.postMapper = postMapper;
        this.userMapper = userMapper;
        this.profileMapper = profileMapper;
    }

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) Long postId,
                                                   @RequestParam(required = false) String weekStart,
                                                   @RequestParam(defaultValue = "false") boolean mine) {
        QueryWrapper<WorkShift> w = new QueryWrapper<>();
        if (mine || UserContext.isStudent()) {
            w.eq("student_id", UserContext.userId());
        }
        if (postId != null) {
            w.eq("post_id", postId);
        }
        if (weekStart != null && !weekStart.isBlank()) {
            LocalDate s = LocalDate.parse(weekStart);
            w.between("shift_date", s, s.plusDays(6));
        }
        w.orderByAsc("shift_date");
        Page<WorkShift> p = shiftMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (WorkShift s : p.getRecords()) {
            list.add(enrich(s));
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    @PostMapping
    public R<WorkShift> save(@RequestBody WorkShift body) {
        if (body.getStudentId() == null || body.getPostId() == null || body.getShiftDate() == null) {
            throw new BizException("学生、岗位与日期必填");
        }
        // 冲突校验一：同日已有班次
        Long dup = shiftMapper.selectCount(new QueryWrapper<WorkShift>()
                .eq("student_id", body.getStudentId()).eq("shift_date", body.getShiftDate())
                .ne(body.getId() != null, "id", body.getId()));
        if (dup != null && dup > 0) {
            throw new BizException("该学生在 " + body.getShiftDate() + " 已有班次，不能重复排班");
        }
        // 冲突校验二：与登记可用时段不匹配（模拟课程冲突）
        StudentProfile pf = profileMapper.selectOne(new QueryWrapper<StudentProfile>()
                .eq("user_id", body.getStudentId()).last("limit 1"));
        boolean conflict = false;
        String reason = null;
        if (pf != null && pf.getAvailableTime() != null && !pf.getAvailableTime().contains("时间灵活")) {
            String avail = pf.getAvailableTime();
            int weekday = body.getShiftDate().getDayOfWeek().getValue();
            String[] names = {"周一", "周二", "周三", "周四", "周五", "周六", "周日"};
            boolean weekend = weekday >= 6;
            if (!(avail.contains(names[weekday - 1]) || (weekend && avail.contains("周末")) || avail.contains("全天"))) {
                conflict = true;
                reason = "与登记可用时段不符：" + avail;
            }
        }
        body.setConflictFlag(conflict ? 1 : 0);
        body.setConflictReason(reason);
        body.setStatus(conflict ? "ADJUST" : "CONFIRMED");
        if (body.getPlanHours() == null) {
            body.setPlanHours(BigDecimal.valueOf(4));
        }
        if (body.getId() != null) {
            shiftMapper.updateById(body);
        } else {
            shiftMapper.insert(body);
        }
        return R.ok(body);
    }

    @PostMapping("/{id}/adjust")
    public R<Void> adjust(@PathVariable Long id, @RequestBody Map<String, String> body) {
        WorkShift s = shiftMapper.selectById(id);
        if (s == null) {
            throw new BizException("班次不存在");
        }
        WorkShift up = new WorkShift();
        up.setId(id);
        up.setStartTime(body.get("startTime"));
        up.setEndTime(body.get("endTime"));
        up.setStatus("CONFIRMED");
        up.setConflictFlag(0);
        up.setConflictReason(null);
        shiftMapper.updateById(up);
        return R.ok();
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        shiftMapper.deleteById(id);
        return R.ok();
    }

    private Map<String, Object> enrich(WorkShift s) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", s.getId());
        m.put("postId", s.getPostId());
        WorkStudyPost p = s.getPostId() == null ? null : postMapper.selectById(s.getPostId());
        m.put("postName", p == null ? "-" : p.getPostName());
        m.put("studentId", s.getStudentId());
        SysUser u = s.getStudentId() == null ? null : userMapper.selectById(s.getStudentId());
        m.put("studentName", u == null ? "-" : u.getRealName());
        m.put("shiftDate", s.getShiftDate() == null ? null : s.getShiftDate().format(DF));
        m.put("startTime", s.getStartTime());
        m.put("endTime", s.getEndTime());
        m.put("workPlace", s.getWorkPlace());
        m.put("planHours", s.getPlanHours());
        m.put("conflictFlag", s.getConflictFlag());
        m.put("conflictReason", s.getConflictReason());
        m.put("status", s.getStatus());
        m.put("createTime", s.getCreateTime() == null ? null : s.getCreateTime().format(DTF));
        return m;
    }
}""")

print("biz part1", len(FILES))
