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
}
