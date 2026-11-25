package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.ws.common.R;
import com.grad.ws.entity.*;
import com.grad.ws.mapper.*;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.*;

/** 首页看板：6 个核心指标 + 5 个图表数据，全部后端聚合，前端不二次计算 */
@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final WorkStudyPostMapper postMapper;
    private final PostApplicationMapper appMapper;
    private final AttendanceRecordMapper attMapper;
    private final HourSummaryMapper sumMapper;
    private final SubsidyBatchMapper batchMapper;
    private final SubsidyItemMapper itemMapper;
    private final SysOrgMapper orgMapper;
    private final MatchScoreMapper scoreMapper;
    private final TermEvaluationMapper evalMapper;

    public DashboardController(WorkStudyPostMapper postMapper, PostApplicationMapper appMapper,
                               AttendanceRecordMapper attMapper, HourSummaryMapper sumMapper,
                               SubsidyBatchMapper batchMapper, SubsidyItemMapper itemMapper,
                               SysOrgMapper orgMapper, MatchScoreMapper scoreMapper,
                               TermEvaluationMapper evalMapper) {
        this.postMapper = postMapper;
        this.appMapper = appMapper;
        this.attMapper = attMapper;
        this.sumMapper = sumMapper;
        this.batchMapper = batchMapper;
        this.itemMapper = itemMapper;
        this.orgMapper = orgMapper;
        this.scoreMapper = scoreMapper;
        this.evalMapper = evalMapper;
    }

    @GetMapping("/stats")
    public R<Map<String, Object>> stats() {
        Map<String, Object> m = new LinkedHashMap<>();
        long posts = postMapper.selectCount(new QueryWrapper<WorkStudyPost>().ne("status", "FINISHED"));
        long apps = appMapper.selectCount(null);
        long employed = appMapper.selectCount(new QueryWrapper<PostApplication>().eq("status", "EMPLOYED"));
        long totalAtt = attMapper.selectCount(null);
        long absent = attMapper.selectCount(new QueryWrapper<AttendanceRecord>().in("status", "ABSENT"));
        List<HourSummary> cur = sumMapper.selectList(new QueryWrapper<HourSummary>().eq("summary_month", "2026-10"));
        BigDecimal hours = cur.stream().map(HourSummary::getValidHours).reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal amount = itemMapper.selectList(null).stream().map(SubsidyItem::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        m.put("postCount", posts);
        m.put("applyCount", apps);
        m.put("employRate", apps == 0 ? "0%" : String.format("%.1f%%", employed * 100.0 / apps));
        m.put("finishHours", hours);
        m.put("absentRate", totalAtt == 0 ? "0%" : String.format("%.1f%%", absent * 100.0 / totalAtt));
        m.put("subsidyAmount", amount);
        m.put("employedCount", employed);
        return R.ok(m);
    }

    @GetMapping("/charts")
    public R<Map<String, Object>> charts() {
        Map<String, Object> m = new LinkedHashMap<>();

        // 1 岗位状态分布
        List<Map<String, Object>> statusDist = new ArrayList<>();
        for (String s : List.of("RECRUITING", "PENDING", "FULL", "FINISHED", "DRAFT")) {
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("name", s);
            o.put("value", postMapper.selectCount(new QueryWrapper<WorkStudyPost>().eq("status", s)));
            statusDist.add(o);
        }
        m.put("statusDist", statusDist);

        // 2 近 6 个月申请趋势
        List<String> months = List.of("2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10");
        List<Long> trend = new ArrayList<>();
        for (String mm : months) {
            trend.add(appMapper.selectCount(new QueryWrapper<PostApplication>().likeRight("create_time", mm)));
        }
        m.put("months", months);
        m.put("trend", trend);

        // 3 部门工时排行
        Map<Long, BigDecimal> byDept = new LinkedHashMap<>();
        for (HourSummary s : sumMapper.selectList(new QueryWrapper<HourSummary>().eq("summary_month", "2026-10"))) {
            WorkStudyPost p = postMapper.selectById(s.getPostId());
            if (p != null) {
                byDept.merge(p.getDeptId(), s.getValidHours(), BigDecimal::add);
            }
        }
        List<Map<String, Object>> deptRank = new ArrayList<>();
        byDept.entrySet().stream().sorted((a, b) -> b.getValue().compareTo(a.getValue())).limit(5).forEach(e -> {
            SysOrg o = orgMapper.selectById(e.getKey());
            Map<String, Object> x = new LinkedHashMap<>();
            x.put("name", o == null ? "-" : o.getOrgName());
            x.put("value", e.getValue());
            deptRank.add(x);
        });
        m.put("deptRank", deptRank);

        // 4 考勤异常构成
        List<Map<String, Object>> attDist = new ArrayList<>();
        for (String s : List.of("LATE", "EARLY", "ABSENT", "MAKEUP")) {
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("name", s);
            o.put("value", attMapper.selectCount(new QueryWrapper<AttendanceRecord>().eq("status", s)));
            attDist.add(o);
        }
        m.put("attDist", attDist);

        // 5 推荐结果分布 + 人工调整率
        Map<String, Long> gradeCnt = new LinkedHashMap<>();
        for (String g : List.of("A", "B", "C", "D")) {
            gradeCnt.put(g, 0L);
        }
        for (MatchScore s : scoreMapper.selectList(null)) {
            gradeCnt.merge(s.getGrade(), 1L, Long::sum);
        }
        List<Map<String, Object>> gradeDist = new ArrayList<>();
        gradeCnt.forEach((g, c) -> {
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("name", g);
            o.put("value", c);
            gradeDist.add(o);
        });
        m.put("gradeDist", gradeDist);
        long adj = scoreMapper.selectCount(new QueryWrapper<MatchScore>().isNotNull("adjust_grade"));
        long all = scoreMapper.selectCount(null);
        m.put("adjustRate", all == 0 ? "0%" : String.format("%.1f%%", adj * 100.0 / all));

        // 6 满意度分布
        List<Map<String, Object>> sat = new ArrayList<>();
        int[] buckets = new int[4];
        for (TermEvaluation e : evalMapper.selectList(null)) {
            double t = e.getTotalScore() == null ? 0 : e.getTotalScore().doubleValue();
            if (t >= 90) buckets[0]++;
            else if (t >= 80) buckets[1]++;
            else if (t >= 70) buckets[2]++;
            else buckets[3]++;
        }
        String[] names = {"优秀(≥90)", "良好(80-89)", "合格(70-79)", "待改进(<70)"};
        for (int i = 0; i < 4; i++) {
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("name", names[i]);
            o.put("value", buckets[i]);
            sat.add(o);
        }
        m.put("satisfaction", sat);
        return R.ok(m);
    }
}
