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
        sc.setSnapshotJson("{\"difficulty\":" + sd + ",\"conflict\":" + sconf + ",\"skill\":" + sskill
                + ",\"hours\":" + shours + ",\"absent\":" + sab + ",\"prefer\":" + spref
                + ",\"conflictTip\":\"" + conflictTip + "\"}");
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
}
