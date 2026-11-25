# -*- coding: utf-8 -*-
"""生成 NEW-021 后端：Spring Boot 3.3.5 + MyBatis-Plus + JWT + MySQL8（JDK17）。
实体/Mapper/通用 CRUD 控制器由 schema 表驱动，业务控制器手写。
"""
import pathlib, textwrap

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "main" / "java" / "com" / "grad" / "ws"
RES = ROOT / "src" / "main" / "resources"
PKG = "com.grad.ws"

# (类名, 表名, 注释, [(字段, 类型, 注释)])
L, S, I, D, DT, B = "Long", "String", "Integer", "Double", "LocalDateTime", "BigDecimal"

SCHEMA = [
    ("SysOrg", "sys_org", "组织架构", [("orgName", S, "组织名称"), ("orgType", S, "类型"), ("parentId", L, ""),
                                     ("sort", I, ""), ("status", S, ""), ("createTime", DT, "")]),
    ("SysRole", "sys_role", "角色", [("roleCode", S, "角色编码"), ("roleName", S, "角色名称"),
                                    ("dataScope", S, "数据范围"), ("sort", I, ""), ("status", S, ""), ("createTime", DT, "")]),
    ("SysUser", "sys_user", "用户", [("username", S, "登录账号"), ("password", S, "BCrypt 密文"), ("realName", S, "姓名"),
                                    ("roleId", L, ""), ("orgId", L, ""), ("studentNo", S, "学号"), ("phone", S, ""),
                                    ("email", S, ""), ("avatar", S, "头像"), ("gender", S, ""), ("status", S, ""),
                                    ("loginFail", I, "连续失败次数"), ("lockUntil", DT, "锁定截止"), ("lastLogin", DT, ""),
                                    ("createTime", DT, ""), ("updateTime", DT, ""), ("deleted", I, "")]),
    ("SysMenu", "sys_menu", "菜单", [("parentId", L, ""), ("menuName", S, ""), ("menuType", S, "M/B"), ("path", S, ""),
                                    ("perms", S, ""), ("icon", S, ""), ("sort", I, ""), ("visible", I, "1 显示 0 隐藏"),
                                    ("status", S, ""), ("createTime", DT, "")]),
    ("SysRoleMenu", "sys_role_menu", "角色菜单", [("roleId", L, ""), ("menuId", L, "")]),
    ("SysDict", "sys_dict", "字典", [("dictType", S, ""), ("dictLabel", S, ""), ("dictValue", S, ""), ("sort", I, ""), ("status", S, "")]),
    ("SysMessage", "sys_message", "站内消息", [("title", S, ""), ("content", S, ""), ("bizType", S, ""), ("bizNo", S, ""),
                                             ("receiverId", L, ""), ("readFlag", I, ""), ("createTime", DT, "")]),
    ("SysAttachment", "sys_attachment", "附件", [("bizType", S, ""), ("bizNo", S, ""), ("fileName", S, ""), ("filePath", S, ""),
                                               ("fileSize", L, ""), ("uploaderId", L, ""), ("createTime", DT, "")]),
    ("SysLog", "sys_log", "操作日志", [("userId", L, ""), ("userName", S, ""), ("module", S, ""), ("action", S, ""),
                                     ("method", S, ""), ("params", S, ""), ("ip", S, ""), ("costMs", I, ""), ("createTime", DT, "")]),
    ("Semester", "semester", "学期", [("termName", S, ""), ("startDate", "LocalDate", ""), ("endDate", "LocalDate", ""),
                                     ("monthHourLimit", B, ""), ("status", S, ""), ("createTime", DT, "")]),
    ("SubsidyStandard", "subsidy_standard", "补贴标准", [("semesterId", L, ""), ("hourRate", B, ""), ("monthHourLimit", B, ""),
                                                        ("specialFactor", B, ""), ("effectTime", DT, ""), ("createTime", DT, "")]),
    ("PostTypeFactor", "post_type_factor", "岗位系数", [("postType", S, ""), ("factor", B, ""), ("remark", S, ""), ("status", S, "")]),
    ("StudentProfile", "student_profile", "学生档案", [("userId", L, ""), ("college", S, ""), ("major", S, ""), ("grade", S, ""),
                                                      ("difficultyLevel", S, "困难认定等级"), ("skillTags", S, ""),
                                                      ("availableTime", S, ""), ("bankCard", S, ""), ("resumePath", S, ""),
                                                      ("createTime", DT, ""), ("updateTime", DT, "")]),
    ("WorkStudyPost", "work_study_post", "勤工助学岗位", [("postNo", S, "岗位编号"), ("postName", S, ""), ("deptId", L, ""),
                                                         ("postType", S, ""), ("workPlace", S, ""), ("recruitNum", I, ""),
                                                         ("hiredNum", I, ""), ("hourRate", B, ""), ("workPeriod", S, ""),
                                                         ("abilityReq", S, ""), ("postDesc", S, ""), ("budget", B, ""),
                                                         ("teacherId", L, ""), ("coverImage", S, ""), ("status", S, ""),
                                                         ("publishTime", DT, ""), ("version", I, "乐观锁版本"),
                                                         ("createTime", DT, ""), ("updateTime", DT, ""), ("deleted", I, "")]),
    ("PostApplication", "post_application", "岗位申请", [("applyNo", S, ""), ("postId", L, ""), ("studentId", L, ""),
                                                        ("applyReason", S, ""), ("availableTime", S, ""), ("resumePath", S, ""),
                                                        ("interviewTime", DT, ""), ("matchScore", D, ""), ("status", S, ""),
                                                        ("createTime", DT, ""), ("updateTime", DT, "")]),
    ("EmploymentRecord", "employment_record", "录用记录", [("postId", L, ""), ("applicationId", L, ""), ("studentId", L, ""),
                                                          ("teacherId", L, ""), ("employTime", DT, ""), ("status", S, ""),
                                                          ("remark", S, ""), ("createTime", DT, "")]),
    ("WorkShift", "work_shift", "排班", [("postId", L, ""), ("studentId", L, ""), ("shiftDate", "LocalDate", ""),
                                        ("startTime", S, ""), ("endTime", S, ""), ("workPlace", S, ""), ("planHours", B, ""),
                                        ("conflictFlag", I, ""), ("conflictReason", S, ""), ("status", S, ""), ("createTime", DT, "")]),
    ("AttendanceRecord", "attendance_record", "考勤记录", [("shiftId", L, ""), ("studentId", L, ""), ("postId", L, ""),
                                                          ("workDate", "LocalDate", ""), ("checkInTime", DT, ""), ("checkOutTime", DT, ""),
                                                          ("actualHours", B, ""), ("validHours", B, ""), ("status", S, ""),
                                                          ("abnormalReason", S, ""), ("evidenceImage", S, ""), ("verifyStatus", S, ""),
                                                          ("createTime", DT, "")]),
    ("HourSummary", "hour_summary", "月度工时", [("studentId", L, ""), ("postId", L, ""), ("summaryMonth", S, ""),
                                                ("planHours", B, ""), ("actualHours", B, ""), ("validHours", B, ""),
                                                ("limitHours", B, ""), ("status", S, ""), ("confirmTime", DT, ""), ("createTime", DT, "")]),
    ("HourAppeal", "hour_appeal", "工时申诉", [("summaryId", L, ""), ("studentId", L, ""), ("appealHours", B, ""),
                                              ("reason", S, ""), ("status", S, ""), ("handleTime", DT, ""),
                                              ("handleRemark", S, ""), ("createTime", DT, "")]),
    ("SubsidyBatch", "subsidy_batch", "补贴批次", [("batchNo", S, ""), ("semesterId", L, ""), ("summaryMonth", S, ""),
                                                  ("personCount", I, ""), ("totalHours", B, ""), ("totalAmount", B, ""),
                                                  ("status", S, ""), ("auditTime", DT, ""), ("createTime", DT, "")]),
    ("SubsidyItem", "subsidy_item", "补贴明细", [("batchId", L, ""), ("studentId", L, ""), ("postId", L, ""),
                                                ("validHours", B, ""), ("hourRate", B, ""), ("factor", B, ""), ("amount", B, ""),
                                                ("payStatus", S, ""), ("payTime", DT, ""), ("failReason", S, ""), ("createTime", DT, "")]),
    ("TermEvaluation", "term_evaluation", "学期评价", [("studentId", L, ""), ("postId", L, ""), ("semesterId", L, ""),
                                                      ("attendanceScore", I, ""), ("dutyScore", I, ""), ("skillScore", I, ""),
                                                      ("teamScore", I, ""), ("totalScore", B, ""), ("comment", S, ""),
                                                      ("feedback", S, ""), ("status", S, ""), ("createTime", DT, "")]),
    ("MatchRule", "match_rule", "匹配规则", [("version", S, ""), ("wDifficulty", I, ""), ("wConflict", I, ""), ("wSkill", I, ""),
                                            ("wHours", I, ""), ("wAbsent", I, ""), ("wPrefer", I, ""), ("status", S, ""),
                                            ("effectTime", DT, ""), ("creator", S, ""), ("createTime", DT, "")]),
    ("MatchScore", "match_score", "匹配计算留痕", [("studentId", L, ""), ("postId", L, ""), ("applicationId", L, ""),
                                                  ("ruleVersion", S, ""), ("scoreDifficulty", I, ""), ("scoreConflict", I, ""),
                                                  ("scoreSkill", I, ""), ("scoreHours", I, ""), ("scoreAbsent", I, ""),
                                                  ("scorePrefer", I, ""), ("totalScore", B, ""), ("grade", S, ""),
                                                  ("snapshotJson", S, ""), ("adjustGrade", S, ""), ("adjustReason", S, ""),
                                                  ("adjustBy", S, ""), ("createTime", DT, "")]),
    ("WorkStudyLog", "work_study_log", "业务流转时间轴", [("bizType", S, ""), ("bizNo", S, ""), ("fromStatus", S, ""),
                                                         ("toStatus", S, ""), ("action", S, ""), ("reason", S, ""),
                                                         ("operator", S, ""), ("createTime", DT, "")]),
]

IMPORTS = """package {pkg}.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
"""


def gen_entities():
    for cls, table, comment, fields in SCHEMA:
        out = [IMPORTS.format(pkg=PKG), "", f"/** {comment} */", "@Data", f'@TableName("{table}")',
               f"public class {cls} {{", "", "    @TableId(type = IdType.AUTO)", "    private Long id;"]
        for f, t, c in fields:
            if f in ("deleted",):
                out.append("    @TableLogic")
            if c:
                out.append(f"    /** {c} */")
            out.append(f"    private {t} {f};")
        out.append("}")
        p = SRC / "entity" / f"{cls}.java"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(out) + "\n", encoding="utf-8")


def gen_mappers():
    for cls, table, comment, fields in SCHEMA:
        code = f"""package {PKG}.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import {PKG}.entity.{cls};
import org.apache.ibatis.annotations.Mapper;

/** {comment} Mapper */
@Mapper
public interface {cls}Mapper extends BaseMapper<{cls}> {{
}}
"""
        p = SRC / "mapper" / f"{cls}Mapper.java"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code, encoding="utf-8")


def gen_generic_controllers():
    """简单主数据表用通用 CRUD 控制器。"""
    simple = [("SysOrg", "org"), ("SysDict", "dict"), ("Semester", "semester"),
              ("SubsidyStandard", "standard"), ("PostTypeFactor", "factor"),
              ("StudentProfile", "profile"), ("TermEvaluation", "evaluation"),
              ("SysAttachment", "attachment"), ("SysLog", "log"), ("EmploymentRecord", "employment"),
              ("HourAppeal", "appeal")]
    tpl = """package {pkg}.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import {pkg}.common.PageResult;
import {pkg}.common.R;
import {pkg}.entity.{cls};
import {pkg}.mapper.{cls}Mapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** {comment}：通用增删改查 + 服务端分页 */
@RestController
@RequestMapping("/api/{path}")
public class {cls}Controller {{

    private final {cls}Mapper mapper;

    public {cls}Controller({cls}Mapper mapper) {{
        this.mapper = mapper;
    }}

    @GetMapping("/page")
    public R<PageResult<{cls}>> page(@RequestParam(defaultValue = "1") long page,
                                     @RequestParam(defaultValue = "10") long size,
                                     @RequestParam(required = false) String kw,
                                     @RequestParam(required = false) String status,
                                     @RequestParam(required = false) Long pid) {{
        QueryWrapper<{cls}> w = new QueryWrapper<>();
        if (kw != null && !kw.isBlank()) {{
            w.like("{kwCol}", kw).or().like("id", kw);
        }}
        if (status != null && !status.isBlank()) {{
            w.eq("status", status);
        }}
        if (pid != null) {{
            w.eq("semester_id", pid);
        }}
        w.orderByDesc("id");
        Page<{cls}> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), page, size, p.getRecords()));
    }}

    @GetMapping("/list")
    public R<List<{cls}>> list() {{
        return R.ok(mapper.selectList(new QueryWrapper<{cls}>().orderByAsc("id")));
    }}

    @GetMapping("/{{id}}")
    public R<{cls}> get(@PathVariable Long id) {{
        return R.ok(mapper.selectById(id));
    }}

    @PostMapping
    public R<{cls}> save(@RequestBody {cls} body) {{
        body.setId(null);
        mapper.insert(body);
        return R.ok(body);
    }}

    @PutMapping("/{{id}}")
    public R<{cls}> update(@PathVariable Long id, @RequestBody {cls} body) {{
        body.setId(id);
        mapper.updateById(body);
        return R.ok(body);
    }}

    @DeleteMapping("/{{id}}")
    public R<Void> delete(@PathVariable Long id) {{
        mapper.deleteById(id);
        return R.ok();
    }}
}}
"""
    kwcol = {"SysOrg": "org_name", "SysDict": "dict_label", "Semester": "term_name",
             "SubsidyStandard": "semester_id", "PostTypeFactor": "post_type",
             "StudentProfile": "college", "TermEvaluation": "comment", "SysAttachment": "file_name",
             "SysLog": "action", "EmploymentRecord": "remark", "HourAppeal": "reason"}
    comments = {c: cm for c, t, cm, f in SCHEMA}
    for cls, path in simple:
        code = tpl.format(pkg=PKG, cls=cls, path=path, comment=comments[cls], kwCol=kwcol[cls])
        p = SRC / "controller" / f"{cls}Controller.java"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code, encoding="utf-8")


gen_entities()
gen_mappers()
gen_generic_controllers()
print("entities+mappers+generic controllers done")
