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
}
