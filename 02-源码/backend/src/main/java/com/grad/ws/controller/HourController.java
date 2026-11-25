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
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/** 工时：月末汇总、老师确认、学生申诉、超上限特别审批 */
@RestController
@RequestMapping("/api/hour")
public class HourController {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final HourSummaryMapper sumMapper;
    private final HourAppealMapper appealMapper;
    private final SysUserMapper userMapper;
    private final WorkStudyPostMapper postMapper;

    public HourController(HourSummaryMapper sumMapper, HourAppealMapper appealMapper,
                          SysUserMapper userMapper, WorkStudyPostMapper postMapper) {
        this.sumMapper = sumMapper;
        this.appealMapper = appealMapper;
        this.userMapper = userMapper;
        this.postMapper = postMapper;
    }

    @GetMapping("/summary/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) String month,
                                                   @RequestParam(required = false) String status,
                                                   @RequestParam(defaultValue = "false") boolean mine) {
        QueryWrapper<HourSummary> w = new QueryWrapper<>();
        if (mine || UserContext.isStudent()) {
            w.eq("student_id", UserContext.userId());
        }
        if (month != null && !month.isBlank()) {
            w.eq("summary_month", month);
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        w.orderByDesc("summary_month").orderByAsc("student_id");
        Page<HourSummary> p = sumMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (HourSummary s : p.getRecords()) {
            list.add(enrich(s));
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    @PostMapping("/summary/{id}/confirm")
    public R<Void> confirm(@PathVariable Long id) {
        HourSummary s = sumMapper.selectById(id);
        if (s == null) {
            throw new BizException("工时记录不存在");
        }
        HourSummary up = new HourSummary();
        up.setId(id);
        up.setStatus("CONFIRMED");
        up.setConfirmTime(LocalDateTime.now());
        sumMapper.updateById(up);
        return R.ok();
    }

    /** 批量确认：逐条返回成功/失败原因，不整批静默失败 */
    @PostMapping("/summary/batch-confirm")
    public R<List<Map<String, Object>>> batchConfirm(@RequestBody List<Long> ids) {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Long id : ids) {
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("id", id);
            try {
                HourSummary s = sumMapper.selectById(id);
                if (s == null) {
                    throw new BizException("记录不存在");
                }
                if ("OVER_LIMIT".equals(s.getStatus())) {
                    throw new BizException("超出月度上限，需资助中心特别审批");
                }
                HourSummary up = new HourSummary();
                up.setId(id);
                up.setStatus("CONFIRMED");
                up.setConfirmTime(LocalDateTime.now());
                sumMapper.updateById(up);
                r.put("ok", true);
            } catch (BizException e) {
                r.put("ok", false);
                r.put("msg", e.getMessage());
            }
            out.add(r);
        }
        return R.ok(out);
    }

    @PostMapping("/appeal")
    public R<HourAppeal> appeal(@RequestBody Map<String, String> body) {
        String reason = body.get("reason");
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException("申诉原因不少于 5 个字");
        }
        HourAppeal a = new HourAppeal();
        a.setSummaryId(Long.valueOf(body.get("summaryId")));
        a.setStudentId(UserContext.userId());
        a.setAppealHours(new BigDecimal(body.getOrDefault("hours", "0")));
        a.setReason(reason);
        a.setStatus("PENDING");
        appealMapper.insert(a);
        return R.ok(a);
    }

    @PostMapping("/appeal/{id}/handle")
    public R<Void> handle(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String status = body.getOrDefault("status", "PASS");
        if ("REJECT".equals(status) && (body.get("remark") == null || body.get("remark").trim().length() < 5)) {
            throw new BizException("驳回申诉必须填写不少于 5 个字的原因");
        }
        HourAppeal a = appealMapper.selectById(id);
        if (a == null) {
            throw new BizException("申诉不存在");
        }
        HourAppeal up = new HourAppeal();
        up.setId(id);
        up.setStatus(status);
        up.setHandleTime(LocalDateTime.now());
        up.setHandleRemark(body.get("remark"));
        appealMapper.updateById(up);
        if ("PASS".equals(status)) {
            HourSummary s = sumMapper.selectById(a.getSummaryId());
            if (s != null) {
                HourSummary su = new HourSummary();
                su.setId(s.getId());
                su.setValidHours(s.getValidHours().add(a.getAppealHours()));
                sumMapper.updateById(su);
            }
        }
        return R.ok();
    }

    @GetMapping("/appeal/page")
    public R<PageResult<Map<String, Object>>> appeals(@RequestParam(defaultValue = "1") long page,
                                                      @RequestParam(defaultValue = "10") long size,
                                                      @RequestParam(required = false) String status,
                                                      @RequestParam(defaultValue = "false") boolean mine) {
        QueryWrapper<HourAppeal> w = new QueryWrapper<>();
        if (mine || UserContext.isStudent()) {
            w.eq("student_id", UserContext.userId());
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        w.orderByDesc("create_time");
        Page<HourAppeal> p = appealMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (HourAppeal a : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", a.getId());
            m.put("summaryId", a.getSummaryId());
            m.put("studentId", a.getStudentId());
            SysUser u = userMapper.selectById(a.getStudentId());
            m.put("studentName", u == null ? "-" : u.getRealName());
            HourSummary s = sumMapper.selectById(a.getSummaryId());
            m.put("month", s == null ? "-" : s.getSummaryMonth());
            m.put("appealHours", a.getAppealHours());
            m.put("reason", a.getReason());
            m.put("status", a.getStatus());
            m.put("handleRemark", a.getHandleRemark());
            m.put("createTime", a.getCreateTime() == null ? null : a.getCreateTime().format(DTF));
            list.add(m);
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    private Map<String, Object> enrich(HourSummary s) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", s.getId());
        m.put("studentId", s.getStudentId());
        SysUser u = userMapper.selectById(s.getStudentId());
        m.put("studentName", u == null ? "-" : u.getRealName());
        m.put("postId", s.getPostId());
        WorkStudyPost p = s.getPostId() == null ? null : postMapper.selectById(s.getPostId());
        m.put("postName", p == null ? "-" : p.getPostName());
        m.put("summaryMonth", s.getSummaryMonth());
        m.put("planHours", s.getPlanHours());
        m.put("actualHours", s.getActualHours());
        m.put("validHours", s.getValidHours());
        m.put("limitHours", s.getLimitHours());
        m.put("status", s.getStatus());
        m.put("confirmTime", s.getConfirmTime() == null ? null : s.getConfirmTime().format(DTF));
        return m;
    }
}
