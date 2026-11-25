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
}
