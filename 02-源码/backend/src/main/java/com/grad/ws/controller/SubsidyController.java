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
}
