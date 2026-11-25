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
}
