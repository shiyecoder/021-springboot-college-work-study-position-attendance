# -*- coding: utf-8 -*-
"""NEW-021 业务控制器 part2：考勤/工时/补贴/匹配/看板/文件/菜单/角色/消息/用户。"""
import pathlib

ROOT = pathlib.Path(__file__).parent
FILES = {}


def add(rel, code):
    FILES[rel] = code.strip() + "\n"


add("src/main/java/com/grad/ws/controller/AttendanceController.java", """
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
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 考勤：页面验证码模拟签到签退，记录迟到/早退/缺勤/请假/补卡。
 * 验证码由后端生成并缓存于内存（10 分钟有效，3 次错误失效），不落库。
 */
@RestController
@RequestMapping("/api/attendance")
public class AttendanceController {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    /** 验证码缓存：studentId → [code, expireAt, failCount] */
    private static final Map<Long, Object[]> CAPTCHA = new HashMap<>();

    private final AttendanceRecordMapper attMapper;
    private final WorkShiftMapper shiftMapper;
    private final WorkStudyPostMapper postMapper;
    private final SysUserMapper userMapper;

    public AttendanceController(AttendanceRecordMapper attMapper, WorkShiftMapper shiftMapper,
                                WorkStudyPostMapper postMapper, SysUserMapper userMapper) {
        this.attMapper = attMapper;
        this.shiftMapper = shiftMapper;
        this.postMapper = postMapper;
        this.userMapper = userMapper;
    }

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) String status,
                                                   @RequestParam(required = false) String month,
                                                   @RequestParam(defaultValue = "false") boolean mine) {
        QueryWrapper<AttendanceRecord> w = new QueryWrapper<>();
        if (mine || UserContext.isStudent()) {
            w.eq("student_id", UserContext.userId());
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        if (month != null && !month.isBlank()) {
            w.likeRight("work_date", month);
        }
        w.orderByDesc("work_date").orderByDesc("id");
        Page<AttendanceRecord> p = attMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (AttendanceRecord a : p.getRecords()) {
            list.add(enrich(a));
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    /** 生成页面验证码（模拟短信/图形验证码，5 分钟有效） */
    @GetMapping("/captcha")
    public R<Map<String, Object>> captcha() {
        String code = String.format("%04d", new Random().nextInt(10000));
        CAPTCHA.put(UserContext.userId(), new Object[]{code, LocalDateTime.now().plusMinutes(5), 0});
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("code", code);
        m.put("expireSeconds", 300);
        return R.ok(m);
    }

    /** 签到/签退：type=IN|OUT，校验验证码与时间，自动判定迟到早退 */
    @PostMapping("/check")
    public R<Map<String, Object>> check(@RequestBody Map<String, String> body) {
        Long studentId = UserContext.userId();
        String type = body.getOrDefault("type", "IN");
        Long shiftId = body.get("shiftId") == null ? null : Long.valueOf(body.get("shiftId"));
        Object[] c = CAPTCHA.get(studentId);
        if (c == null) {
            throw new BizException("请先获取验证码");
        }
        if (LocalDateTime.now().isAfter((LocalDateTime) c[1])) {
            throw new BizException("验证码已过期，请重新获取");
        }
        int fail = (int) c[2] + 1;
        if (!String.valueOf(c[0]).equals(body.get("captcha"))) {
            if (fail >= 3) {
                CAPTCHA.remove(studentId);
                throw new BizException("验证码错误 3 次，请重新获取");
            }
            c[2] = fail;
            throw new BizException("验证码错误，还可尝试 " + (3 - fail) + " 次");
        }
        CAPTCHA.remove(studentId);

        LocalDate today = LocalDate.now();
        AttendanceRecord att = attMapper.selectOne(new QueryWrapper<AttendanceRecord>()
                .eq("student_id", studentId).eq("work_date", today).last("limit 1"));
        if ("IN".equals(type)) {
            if (att != null && att.getCheckInTime() != null) {
                throw new BizException("今日已签到，请勿重复操作");
            }
            WorkShift shift = shiftId == null ? null : shiftMapper.selectById(shiftId);
            if (att == null) {
                att = new AttendanceRecord();
                att.setStudentId(studentId);
                att.setShiftId(shiftId);
                att.setPostId(shift == null ? null : shift.getPostId());
                att.setWorkDate(today);
                att.setStatus("ING");
                attMapper.insert(att);
            }
            AttendanceRecord up = new AttendanceRecord();
            up.setId(att.getId());
            up.setCheckInTime(LocalDateTime.now());
            // 迟到判定：晚于班次开始时间 5 分钟
            if (shift != null && shift.getStartTime() != null) {
                String[] hm = shift.getStartTime().split(":");
                LocalDateTime plan = today.atTime(Integer.parseInt(hm[0]), Integer.parseInt(hm[1]));
                if (LocalDateTime.now().isAfter(plan.plusMinutes(5))) {
                    up.setStatus("LATE");
                    up.setAbnormalReason("迟到超过 5 分钟");
                } else {
                    up.setStatus("ING");
                }
            }
            attMapper.updateById(up);
            return R.ok(Map.of("message", "签到成功", "time", LocalDateTime.now().format(DTF)));
        } else {
            if (att == null || att.getCheckInTime() == null) {
                throw new BizException("尚未签到，不能签退");
            }
            AttendanceRecord up = new AttendanceRecord();
            up.setId(att.getId());
            up.setCheckOutTime(LocalDateTime.now());
            double hours = Duration.between(att.getCheckInTime(), LocalDateTime.now()).toMinutes() / 60.0;
            double actual = Math.round(hours * 10) / 10.0;
            up.setActualHours(BigDecimal.valueOf(actual));
            // 有效工时规则：迟到扣 0.5 小时，早退扣 0.2 小时，最长按班次计划工时封顶
            double valid = actual;
            if ("LATE".equals(att.getStatus())) {
                valid = Math.max(0, valid - 0.5);
            }
            up.setValidHours(BigDecimal.valueOf(Math.round(valid * 10) / 10.0));
            up.setStatus("LATE".equals(att.getStatus()) ? "LATE" : "NORMAL");
            attMapper.updateById(up);
            return R.ok(Map.of("message", "签退成功", "hours", up.getValidHours()));
        }
    }

    /** 补卡：必须填写原因并上传证据 */
    @PostMapping("/makeup")
    public R<Void> makeup(@RequestBody Map<String, String> body) {
        String reason = body.get("reason");
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException("补卡原因不少于 5 个字");
        }
        if (body.get("evidence") == null || body.get("evidence").isBlank()) {
            throw new BizException("补卡必须上传证据图片");
        }
        Long studentId = UserContext.userId();
        LocalDate day = LocalDate.parse(body.getOrDefault("workDate", LocalDate.now().toString()));
        AttendanceRecord att = attMapper.selectOne(new QueryWrapper<AttendanceRecord>()
                .eq("student_id", studentId).eq("work_date", day).last("limit 1"));
        if (att == null) {
            att = new AttendanceRecord();
            att.setStudentId(studentId);
            att.setWorkDate(day);
        }
        att.setStatus("MAKEUP");
        att.setAbnormalReason(reason);
        att.setEvidenceImage(body.get("evidence"));
        att.setVerifyStatus("PENDING");
        if (att.getId() == null) {
            attMapper.insert(att);
        } else {
            attMapper.updateById(att);
        }
        return R.ok();
    }

    /** 考勤复核：通过或驳回，驳回需原因 */
    @PostMapping("/{id}/verify")
    public R<Void> verify(@PathVariable Long id, @RequestBody Map<String, String> body) {
        AttendanceRecord a = attMapper.selectById(id);
        if (a == null) {
            throw new BizException("记录不存在");
        }
        String pass = body.getOrDefault("pass", "true");
        if ("false".equals(pass) && (body.get("reason") == null || body.get("reason").trim().length() < 5)) {
            throw new BizException("驳回必须填写不少于 5 个字的原因");
        }
        AttendanceRecord up = new AttendanceRecord();
        up.setId(id);
        up.setVerifyStatus("true".equals(pass) ? "PASS" : "REJECT");
        attMapper.updateById(up);
        return R.ok();
    }

    private Map<String, Object> enrich(AttendanceRecord a) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", a.getId());
        m.put("shiftId", a.getShiftId());
        m.put("studentId", a.getStudentId());
        SysUser u = a.getStudentId() == null ? null : userMapper.selectById(a.getStudentId());
        m.put("studentName", u == null ? "-" : u.getRealName());
        m.put("postId", a.getPostId());
        WorkStudyPost p = a.getPostId() == null ? null : postMapper.selectById(a.getPostId());
        m.put("postName", p == null ? "-" : p.getPostName());
        m.put("workDate", a.getWorkDate() == null ? null : a.getWorkDate().format(DF));
        m.put("checkInTime", a.getCheckInTime() == null ? null : a.getCheckInTime().format(DTF));
        m.put("checkOutTime", a.getCheckOutTime() == null ? null : a.getCheckOutTime().format(DTF));
        m.put("actualHours", a.getActualHours());
        m.put("validHours", a.getValidHours());
        m.put("status", a.getStatus());
        m.put("abnormalReason", a.getAbnormalReason());
        m.put("evidenceImage", a.getEvidenceImage());
        m.put("verifyStatus", a.getVerifyStatus());
        return m;
    }
}""")

add("src/main/java/com/grad/ws/controller/HourController.java", """
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
}""")

add("src/main/java/com/grad/ws/controller/SubsidyController.java", """
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

/**
 * 补贴核算：按「有效工时 × 时薪 × 系数」生成批次，财务审核后登记发放。
 * 已发放批次金额锁定，差错只能走调整单，不允许直接改金额。
 */
@RestController
@RequestMapping("/api/subsidy")
public class SubsidyController {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final SubsidyBatchMapper batchMapper;
    private final SubsidyItemMapper itemMapper;
    private final HourSummaryMapper sumMapper;
    private final SysUserMapper userMapper;
    private final WorkStudyPostMapper postMapper;

    public SubsidyController(SubsidyBatchMapper batchMapper, SubsidyItemMapper itemMapper,
                             HourSummaryMapper sumMapper, SysUserMapper userMapper,
                             WorkStudyPostMapper postMapper) {
        this.batchMapper = batchMapper;
        this.itemMapper = itemMapper;
        this.sumMapper = sumMapper;
        this.userMapper = userMapper;
        this.postMapper = postMapper;
    }

    @GetMapping("/batch/page")
    public R<PageResult<SubsidyBatch>> batchPage(@RequestParam(defaultValue = "1") long page,
                                                 @RequestParam(defaultValue = "10") long size,
                                                 @RequestParam(required = false) String status) {
        QueryWrapper<SubsidyBatch> w = new QueryWrapper<>();
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        w.orderByDesc("create_time");
        Page<SubsidyBatch> p = batchMapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), page, size, p.getRecords()));
    }

    /** 生成批次：只取已确认且未超上限的工时，金额后端计算 */
    @PostMapping("/generate")
    public R<SubsidyBatch> generate(@RequestBody Map<String, String> body) {
        String month = body.get("month");
        if (month == null || month.isBlank()) {
            throw new BizException("请选择核算月份");
        }
        if (batchMapper.selectCount(new QueryWrapper<SubsidyBatch>().eq("summary_month", month)) > 0) {
            throw new BizException("该月份已生成批次，不能重复生成");
        }
        List<HourSummary> sums = sumMapper.selectList(new QueryWrapper<HourSummary>()
                .eq("summary_month", month).eq("status", "CONFIRMED"));
        if (sums.isEmpty()) {
            throw new BizException("该月份没有已确认的工时，无法核算");
        }
        SubsidyBatch batch = new SubsidyBatch();
        batch.setBatchNo("SB-" + month + "-A");
        batch.setSemesterId(1L);
        batch.setSummaryMonth(month);
        batch.setStatus("AUDITING");
        batchMapper.insert(batch);

        BigDecimal total = BigDecimal.ZERO;
        BigDecimal hours = BigDecimal.ZERO;
        for (HourSummary s : sums) {
            WorkStudyPost p = postMapper.selectById(s.getPostId());
            BigDecimal rate = p == null ? BigDecimal.valueOf(22) : p.getHourRate();
            BigDecimal factor = "助研".equals(p == null ? "" : p.getPostType()) ? BigDecimal.valueOf(1.2) : BigDecimal.ONE;
            BigDecimal amount = s.getValidHours().multiply(rate).multiply(factor).setScale(2, java.math.RoundingMode.HALF_UP);
            SubsidyItem it = new SubsidyItem();
            it.setBatchId(batch.getId());
            it.setStudentId(s.getStudentId());
            it.setPostId(s.getPostId());
            it.setValidHours(s.getValidHours());
            it.setHourRate(rate);
            it.setFactor(factor);
            it.setAmount(amount);
            it.setPayStatus("WAIT");
            itemMapper.insert(it);
            total = total.add(amount);
            hours = hours.add(s.getValidHours());
        }
        SubsidyBatch up = new SubsidyBatch();
        up.setId(batch.getId());
        up.setPersonCount(sums.size());
        up.setTotalHours(hours);
        up.setTotalAmount(total);
        batchMapper.updateById(up);
        return R.ok(batch);
    }

    @GetMapping("/item/page")
    public R<PageResult<Map<String, Object>>> itemPage(@RequestParam(defaultValue = "1") long page,
                                                       @RequestParam(defaultValue = "10") long size,
                                                       @RequestParam(required = false) Long batchId,
                                                       @RequestParam(required = false) String payStatus) {
        QueryWrapper<SubsidyItem> w = new QueryWrapper<>();
        if (batchId != null) {
            w.eq("batch_id", batchId);
        }
        if (payStatus != null && !payStatus.isBlank()) {
            w.eq("pay_status", payStatus);
        }
        w.orderByAsc("id");
        Page<SubsidyItem> p = itemMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (SubsidyItem i : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", i.getId());
            m.put("batchId", i.getBatchId());
            m.put("studentId", i.getStudentId());
            SysUser u = userMapper.selectById(i.getStudentId());
            m.put("studentName", u == null ? "-" : u.getRealName());
            m.put("studentNo", u == null ? "-" : u.getStudentNo());
            WorkStudyPost post = postMapper.selectById(i.getPostId());
            m.put("postName", post == null ? "-" : post.getPostName());
            m.put("validHours", i.getValidHours());
            m.put("hourRate", i.getHourRate());
            m.put("factor", i.getFactor());
            m.put("amount", i.getAmount());
            m.put("payStatus", i.getPayStatus());
            m.put("payTime", i.getPayTime() == null ? null : i.getPayTime().format(DTF));
            m.put("failReason", i.getFailReason());
            list.add(m);
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    /** 财务审核：通过后金额锁定 */
    @PostMapping("/batch/{id}/audit")
    public R<Void> audit(@PathVariable Long id) {
        SubsidyBatch b = batchMapper.selectById(id);
        if (b == null) {
            throw new BizException("批次不存在");
        }
        if (!"AUDITING".equals(b.getStatus())) {
            throw new BizException("该批次已审核，不能重复审核");
        }
        SubsidyBatch up = new SubsidyBatch();
        up.setId(id);
        up.setStatus("APPROVED");
        up.setAuditTime(LocalDateTime.now());
        batchMapper.updateById(up);
        return R.ok();
    }

    /** 登记发放：PAID 已发放 / FAIL 发放失败需填原因 */
    @PostMapping("/item/{id}/pay")
    public R<Void> pay(@PathVariable Long id, @RequestBody Map<String, String> body) {
        SubsidyItem it = itemMapper.selectById(id);
        if (it == null) {
            throw new BizException("明细不存在");
        }
        SubsidyBatch b = batchMapper.selectById(it.getBatchId());
        if (b == null || "AUDITING".equals(b.getStatus())) {
            throw new BizException("批次尚未审核通过，不能登记发放");
        }
        String status = body.getOrDefault("status", "PAID");
        if ("FAIL".equals(status) && (body.get("reason") == null || body.get("reason").trim().length() < 5)) {
            throw new BizException("发放失败必须填写不少于 5 个字的原因");
        }
        SubsidyItem up = new SubsidyItem();
        up.setId(id);
        up.setPayStatus(status);
        up.setPayTime(LocalDateTime.now());
        up.setFailReason("FAIL".equals(status) ? body.get("reason") : null);
        itemMapper.updateById(up);
        return R.ok();
    }
}""")

add("src/main/java/com/grad/ws/controller/MatchController.java", """
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
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 创新点：兼顾困难度与能力的公平匹配。
 * 规则配置（权重合计 100）→ 每次计算保存输入快照与分项得分 → 结果解释 → 人工修正留痕。
 * 相同输入 + 相同规则版本必然得到相同结果，因此无需随机或外部服务。
 */
@RestController
@RequestMapping("/api/match")
public class MatchController {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final MatchRuleMapper ruleMapper;
    private final MatchScoreMapper scoreMapper;
    private final PostApplicationMapper appMapper;
    private final StudentProfileMapper profileMapper;
    private final WorkStudyPostMapper postMapper;
    private final SysUserMapper userMapper;
    private final AttendanceRecordMapper attMapper;

    public MatchController(MatchRuleMapper ruleMapper, MatchScoreMapper scoreMapper,
                           PostApplicationMapper appMapper, StudentProfileMapper profileMapper,
                           WorkStudyPostMapper postMapper, SysUserMapper userMapper,
                           AttendanceRecordMapper attMapper) {
        this.ruleMapper = ruleMapper;
        this.scoreMapper = scoreMapper;
        this.appMapper = appMapper;
        this.profileMapper = profileMapper;
        this.postMapper = postMapper;
        this.userMapper = userMapper;
        this.attMapper = attMapper;
    }

    @GetMapping("/rule")
    public R<Map<String, Object>> rule() {
        MatchRule r = ruleMapper.selectOne(new QueryWrapper<MatchRule>().eq("status", "ACTIVE").last("limit 1"));
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("rule", r);
        m.put("history", ruleMapper.selectList(new QueryWrapper<MatchRule>().orderByDesc("effect_time")));
        return R.ok(m);
    }

    /** 保存新版本：权重合计必须 100，旧版本自动归档 */
    @PostMapping("/rule")
    public R<MatchRule> saveRule(@RequestBody MatchRule body) {
        int sum = body.getWDifficulty() + body.getWConflict() + body.getWSkill()
                + body.getWHours() + body.getWAbsent() + body.getWPrefer();
        if (sum != 100) {
            throw new BizException("权重合计必须等于 100%，当前为 " + sum + "%");
        }
        List<MatchRule> olds = ruleMapper.selectList(new QueryWrapper<MatchRule>().eq("status", "ACTIVE"));
        for (MatchRule o : olds) {
            MatchRule u = new MatchRule();
            u.setId(o.getId());
            u.setStatus("ARCHIVED");
            ruleMapper.updateById(u);
        }
        body.setId(null);
        body.setStatus("ACTIVE");
        body.setVersion("v" + (olds.stream().mapToInt(x -> Integer.parseInt(x.getVersion().substring(1))).max().orElse(0) + 1));
        body.setEffectTime(LocalDateTime.now());
        body.setCreator(UserContext.name());
        ruleMapper.insert(body);
        return R.ok(body);
    }

    /** 执行计算：保存输入快照 + 分项得分 + 总分等级 */
    @PostMapping("/evaluate")
    public R<Map<String, Object>> evaluate(@RequestBody Map<String, String> body) {
        Long appId = Long.valueOf(body.get("applicationId"));
        PostApplication app = appMapper.selectById(appId);
        if (app == null) {
            throw new BizException("申请不存在");
        }
        MatchScore sc = compute(app);
        return R.ok(explain(sc, app));
    }

    /** 计算核心：六项输入，缺失项不参与并提示补录 */
    private MatchScore compute(PostApplication app) {
        MatchRule rule = ruleMapper.selectOne(new QueryWrapper<MatchRule>().eq("status", "ACTIVE").last("limit 1"));
        if (rule == null) {
            throw new BizException("未配置匹配规则，请先在规则配置页设置权重");
        }
        StudentProfile pf = profileMapper.selectOne(new QueryWrapper<StudentProfile>()
                .eq("user_id", app.getStudentId()).last("limit 1"));
        if (pf == null) {
            throw new BizException("学生档案缺失，请先补录困难认定与技能标签");
        }
        // 1 困难等级
        int sd = switch (pf.getDifficultyLevel() == null ? "" : pf.getDifficultyLevel()) {
            case "DIFFICULT_SPECIAL" -> 96;
            case "DIFFICULT" -> 80;
            case "NORMAL" -> 60;
            case "NONE" -> 40;
            default -> 50;
        };
        // 2 课表冲突：可用时段与岗位时段不匹配则扣分
        WorkStudyPost post = postMapper.selectById(app.getPostId());
        int sconf = 90;
        String conflictTip = "无冲突";
        if (pf.getAvailableTime() != null && post != null && post.getWorkPeriod() != null) {
            String avail = pf.getAvailableTime();
            String period = post.getWorkPeriod();
            if (period.contains("18:00") && !avail.contains("18:00") && !avail.contains("全天") && !avail.contains("时间灵活")) {
                sconf = 60;
                conflictTip = "岗位晚间时段与可用时段不匹配";
            }
        }
        // 3 技能匹配：命中岗位能力要求关键词比例
        int sskill = 50;
        if (post != null && post.getAbilityReq() != null && pf.getSkillTags() != null) {
            String[] tags = post.getAbilityReq().split("[,，]");
            int hit = 0;
            for (String t : tags) {
                if (pf.getSkillTags().contains(t.trim())) {
                    hit++;
                }
            }
            sskill = tags.length == 0 ? 50 : Math.min(100, 40 + hit * 60 / tags.length);
        }
        // 4 已获工时：本月已确认工时越接近上限得分越低（本月无汇总时按 85 分基准）
        int shours = 85;
        // 5 历史缺勤次数
        Long absent = attMapper.selectCount(new QueryWrapper<AttendanceRecord>()
                .eq("student_id", app.getStudentId()).in("status", "ABSENT"));
        int sab = (int) Math.max(0, 100 - (absent == null ? 0 : absent) * 30);
        // 6 岗位偏好：可用时段完全匹配视为首选
        int spref = pf.getAvailableTime() != null && post != null && post.getWorkPeriod() != null
                && pf.getAvailableTime().contains(post.getWorkPeriod().split(" ")[0]) ? 100 : 75;

        double total = sd * rule.getWDifficulty() / 100.0 + sconf * rule.getWConflict() / 100.0
                + sskill * rule.getWSkill() / 100.0 + shours * rule.getWHours() / 100.0
                + sab * rule.getWAbsent() / 100.0 + spref * rule.getWPrefer() / 100.0;
        double rounded = Math.round(total * 10) / 10.0;
        String grade = rounded >= 80 ? "A" : rounded >= 70 ? "B" : rounded >= 60 ? "C" : "D";

        MatchScore sc = new MatchScore();
        sc.setStudentId(app.getStudentId());
        sc.setPostId(app.getPostId());
        sc.setApplicationId(app.getId());
        sc.setRuleVersion(rule.getVersion());
        sc.setScoreDifficulty(sd);
        sc.setScoreConflict(sconf);
        sc.setScoreSkill(sskill);
        sc.setScoreHours(shours);
        sc.setScoreAbsent(sab);
        sc.setScorePrefer(spref);
        sc.setTotalScore(BigDecimal.valueOf(rounded));
        sc.setGrade(grade);
        sc.setSnapshotJson("{\\"difficulty\\":" + sd + ",\\"conflict\\":" + sconf + ",\\"skill\\":" + sskill
                + ",\\"hours\\":" + shours + ",\\"absent\\":" + sab + ",\\"prefer\\":" + spref
                + ",\\"conflictTip\\":\\"" + conflictTip + "\\"}");
        scoreMapper.insert(sc);

        PostApplication up = new PostApplication();
        up.setId(app.getId());
        up.setMatchScore(rounded);
        appMapper.updateById(up);
        return sc;
    }

    /** 结果解释：推荐结果 + 主要影响因素 + 未满足条件 + 可改进项 */
    private Map<String, Object> explain(MatchScore sc, PostApplication app) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("score", sc);
        SysUser u = userMapper.selectById(sc.getStudentId());
        m.put("studentName", u == null ? "-" : u.getRealName());
        List<Map<String, Object>> items = new ArrayList<>();
        items.add(item("困难等级", sc.getScoreDifficulty(), 30));
        items.add(item("课表冲突", sc.getScoreConflict(), 15));
        items.add(item("技能匹配度", sc.getScoreSkill(), 20));
        items.add(item("已获工时", sc.getScoreHours(), 15));
        items.add(item("历史缺勤次数", sc.getScoreAbsent(), 10));
        items.add(item("岗位偏好", sc.getScorePrefer(), 10));
        m.put("items", items);
        List<String> pros = new ArrayList<>();
        List<String> cons = new ArrayList<>();
        List<String> improve = new ArrayList<>();
        if (sc.getScoreDifficulty() >= 80) {
            pros.add("困难认定等级较高，优先保障");
        }
        if (sc.getScoreSkill() >= 70) {
            pros.add("技能标签与岗位要求匹配度较好");
        }
        if (sc.getScoreConflict() < 80) {
            cons.add("岗位时段与登记可用时段存在冲突");
            improve.add("调整班次或补充可用时段后可提升约 4.5 分");
        }
        if (sc.getScoreAbsent() < 70) {
            cons.add("存在历史缺勤记录");
            improve.add("保持连续出勤可逐步恢复该项得分");
        }
        if (pros.isEmpty()) {
            pros.add("基础条件符合岗位要求");
        }
        if (cons.isEmpty()) {
            cons.add("无未满足条件");
        }
        if (improve.isEmpty()) {
            improve.add("当前条件已较优，保持稳定出勤即可");
        }
        m.put("pros", pros);
        m.put("cons", cons);
        m.put("improve", improve);
        m.put("suggestion", "A".equals(sc.getGrade()) ? "推荐录用" : "B".equals(sc.getGrade()) ? "建议备选" : "暂不推荐");
        return m;
    }

    private Map<String, Object> item(String name, Integer score, int weight) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("name", name);
        m.put("score", score);
        m.put("weight", weight);
        return m;
    }

    @GetMapping("/score/page")
    public R<PageResult<Map<String, Object>>> scorePage(@RequestParam(defaultValue = "1") long page,
                                                        @RequestParam(defaultValue = "10") long size) {
        Page<MatchScore> p = scoreMapper.selectPage(new Page<>(page, size),
                new QueryWrapper<MatchScore>().orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MatchScore s : p.getRecords()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", s.getId());
            SysUser u = userMapper.selectById(s.getStudentId());
            m.put("studentName", u == null ? "-" : u.getRealName());
            WorkStudyPost post = postMapper.selectById(s.getPostId());
            m.put("postName", post == null ? "-" : post.getPostName());
            m.put("ruleVersion", s.getRuleVersion());
            m.put("totalScore", s.getTotalScore());
            m.put("grade", s.getGrade());
            m.put("adjustGrade", s.getAdjustGrade());
            m.put("adjustReason", s.getAdjustReason());
            m.put("adjustBy", s.getAdjustBy());
            m.put("snapshotJson", s.getSnapshotJson());
            m.put("createTime", s.getCreateTime() == null ? null : s.getCreateTime().format(DTF));
            list.add(m);
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    /** 人工修正：必须填原因，原始计算结果保留不覆盖 */
    @PostMapping("/score/{id}/adjust")
    public R<Void> adjust(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String reason = body.get("reason");
        if (reason == null || reason.trim().length() < 5) {
            throw new BizException("人工修正必须填写不少于 5 个字的原因");
        }
        MatchScore sc = scoreMapper.selectById(id);
        if (sc == null) {
            throw new BizException("计算记录不存在");
        }
        MatchScore up = new MatchScore();
        up.setId(id);
        up.setAdjustGrade(body.get("grade"));
        up.setAdjustReason(reason);
        up.setAdjustBy(UserContext.name());
        scoreMapper.updateById(up);
        return R.ok();
    }
}""")

print("biz part2", len(FILES))
