# -*- coding: utf-8 -*-
"""NEW-021 业务控制器 part3：看板/文件/菜单/角色/消息/用户。"""
import pathlib

ROOT = pathlib.Path(__file__).parent
FILES = {}


def add(rel, code):
    FILES[rel] = code.strip() + "\n"


add("src/main/java/com/grad/ws/controller/DashboardController.java", """
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
}""")

add("src/main/java/com/grad/ws/controller/FileController.java", """
package com.grad.ws.controller;

import com.grad.ws.common.BizException;
import com.grad.ws.common.R;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.SysAttachment;
import com.grad.ws.mapper.SysAttachmentMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/** 文件上传：白名单扩展名校验，落盘到项目根 uploads/，返回相对路径 */
@RestController
@RequestMapping("/api/file")
public class FileController {

    private static final Set<String> ALLOW = Set.of("jpg", "jpeg", "png", "webp", "pdf", "doc", "docx", "xls", "xlsx");

    @Value("${app.upload-dir:./uploads}")
    private String uploadDir;

    private final SysAttachmentMapper attMapper;

    public FileController(SysAttachmentMapper attMapper) {
        this.attMapper = attMapper;
    }

    @PostMapping("/upload")
    public R<Map<String, Object>> upload(@RequestParam("file") MultipartFile file,
                                         @RequestParam(required = false) String bizType,
                                         @RequestParam(required = false) String bizNo) {
        if (file == null || file.isEmpty()) {
            throw new BizException("请选择要上传的文件");
        }
        String name = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = name.contains(".") ? name.substring(name.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!ALLOW.contains(ext)) {
            throw new BizException("不支持的文件类型：" + ext);
        }
        if (file.getSize() > 20 * 1024 * 1024L) {
            throw new BizException("单个文件不能超过 20MB");
        }
        try {
            String day = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            Path dir = Paths.get(uploadDir, day).toAbsolutePath().normalize();
            Files.createDirectories(dir);
            String fileName = UUID.randomUUID().toString().replace("-", "") + "." + ext;
            Path target = dir.resolve(fileName);
            file.transferTo(target);
            String rel = "/uploads/" + day + "/" + fileName;

            SysAttachment att = new SysAttachment();
            att.setBizType(bizType == null ? "COMMON" : bizType);
            att.setBizNo(bizNo);
            att.setFileName(name);
            att.setFilePath(rel);
            att.setFileSize(file.getSize());
            att.setUploaderId(UserContext.userId());
            attMapper.insert(att);

            Map<String, Object> m = new LinkedHashMap<>();
            m.put("path", rel);
            m.put("name", name);
            m.put("size", file.getSize());
            return R.ok(m);
        } catch (Exception e) {
            throw new BizException("上传失败：" + e.getMessage());
        }
    }
}""")

add("src/main/java/com/grad/ws/controller/MenuController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.ws.common.R;
import com.grad.ws.entity.SysMenu;
import com.grad.ws.mapper.SysMenuMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** 菜单管理：树形查询、增改删 */
@RestController
@RequestMapping("/api/menu")
public class MenuController {

    private final SysMenuMapper menuMapper;

    public MenuController(SysMenuMapper menuMapper) {
        this.menuMapper = menuMapper;
    }

    @GetMapping("/tree")
    public R<List<SysMenu>> tree() {
        return R.ok(menuMapper.selectList(new QueryWrapper<SysMenu>().orderByAsc("sort")));
    }

    @GetMapping("/page")
    public R<List<SysMenu>> page() {
        return R.ok(menuMapper.selectList(new QueryWrapper<SysMenu>().orderByAsc("sort")));
    }

    @PostMapping
    public R<SysMenu> save(@RequestBody SysMenu body) {
        body.setId(null);
        menuMapper.insert(body);
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<SysMenu> update(@PathVariable Long id, @RequestBody SysMenu body) {
        body.setId(id);
        menuMapper.updateById(body);
        return R.ok(body);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        menuMapper.deleteById(id);
        return R.ok();
    }
}""")

add("src/main/java/com/grad/ws/controller/RoleController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.entity.SysRole;
import com.grad.ws.entity.SysRoleMenu;
import com.grad.ws.mapper.SysRoleMapper;
import com.grad.ws.mapper.SysRoleMenuMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

/** 角色管理：分页、增改删、查询与分配菜单 */
@RestController
@RequestMapping("/api/role")
public class RoleController {

    private final SysRoleMapper roleMapper;
    private final SysRoleMenuMapper roleMenuMapper;

    public RoleController(SysRoleMapper roleMapper, SysRoleMenuMapper roleMenuMapper) {
        this.roleMapper = roleMapper;
        this.roleMenuMapper = roleMenuMapper;
    }

    @GetMapping("/page")
    public R<PageResult<SysRole>> page(@RequestParam(defaultValue = "1") long page,
                                       @RequestParam(defaultValue = "10") long size) {
        Page<SysRole> p = roleMapper.selectPage(new Page<>(page, size),
                new QueryWrapper<SysRole>().orderByAsc("sort"));
        return R.ok(new PageResult<>(p.getTotal(), page, size, p.getRecords()));
    }

    @GetMapping("/list")
    public R<List<SysRole>> list() {
        return R.ok(roleMapper.selectList(new QueryWrapper<SysRole>().orderByAsc("sort")));
    }

    @GetMapping("/{id}/menus")
    public R<List<Long>> menus(@PathVariable Long id) {
        return R.ok(roleMenuMapper.selectList(new QueryWrapper<SysRoleMenu>().eq("role_id", id))
                .stream().map(SysRoleMenu::getMenuId).collect(Collectors.toList()));
    }

    /** 为角色分配菜单：先清空再写入，事务保证一致性 */
    @PutMapping("/{id}/menus")
    @Transactional
    public R<Void> assign(@PathVariable Long id, @RequestBody List<Long> menuIds) {
        roleMenuMapper.delete(new QueryWrapper<SysRoleMenu>().eq("role_id", id));
        for (Long mid : menuIds) {
            SysRoleMenu rm = new SysRoleMenu();
            rm.setRoleId(id);
            rm.setMenuId(mid);
            roleMenuMapper.insert(rm);
        }
        return R.ok();
    }

    @PostMapping
    public R<SysRole> save(@RequestBody SysRole body) {
        body.setId(null);
        roleMapper.insert(body);
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<SysRole> update(@PathVariable Long id, @RequestBody SysRole body) {
        body.setId(id);
        roleMapper.updateById(body);
        return R.ok(body);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        roleMapper.deleteById(id);
        return R.ok();
    }
}""")

add("src/main/java/com/grad/ws/controller/UserController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.BizException;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.entity.SysOrg;
import com.grad.ws.entity.SysRole;
import com.grad.ws.entity.SysUser;
import com.grad.ws.mapper.SysOrgMapper;
import com.grad.ws.mapper.SysRoleMapper;
import com.grad.ws.mapper.SysUserMapper;
import com.grad.ws.service.AuthService;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/** 用户管理：分页（剔除密码）、新增、编辑、重置密码、启停 */
@RestController
@RequestMapping("/api/user")
public class UserController {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysOrgMapper orgMapper;
    private final AuthService authService;

    public UserController(SysUserMapper userMapper, SysRoleMapper roleMapper,
                          SysOrgMapper orgMapper, AuthService authService) {
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.orgMapper = orgMapper;
        this.authService = authService;
    }

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) String kw,
                                                   @RequestParam(required = false) Long roleId) {
        QueryWrapper<SysUser> w = new QueryWrapper<>();
        if (kw != null && !kw.isBlank()) {
            w.and(x -> x.like("real_name", kw).or().like("username", kw).or().like("student_no", kw));
        }
        if (roleId != null) {
            w.eq("role_id", roleId);
        }
        w.orderByAsc("id");
        Page<SysUser> p = userMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (SysUser u : p.getRecords()) {
            SysRole role = roleMapper.selectById(u.getRoleId());
            list.add(authService.toUser(u, role));
        }
        return R.ok(new PageResult<>(p.getTotal(), page, size, list));
    }

    @PostMapping
    public R<Void> save(@RequestBody Map<String, Object> body) {
        String username = str(body.get("username"));
        if (username == null || username.isBlank()) {
            throw new BizException("账号必填");
        }
        if (userMapper.selectCount(new QueryWrapper<SysUser>().eq("username", username)) > 0) {
            throw new BizException("账号已存在");
        }
        SysUser u = new SysUser();
        u.setUsername(username);
        u.setRealName(str(body.get("realName")));
        u.setRoleId(body.get("roleId") == null ? 3L : Long.valueOf(String.valueOf(body.get("roleId"))));
        u.setOrgId(body.get("orgId") == null ? null : Long.valueOf(String.valueOf(body.get("orgId"))));
        u.setStudentNo(str(body.get("studentNo")));
        u.setPhone(str(body.get("phone")));
        u.setEmail(str(body.get("email")));
        u.setAvatar(str(body.get("avatar")));
        u.setGender(str(body.get("gender")));
        u.setStatus("1");
        u.setLoginFail(0);
        u.setDeleted(0);
        String pwd = str(body.get("password"));
        u.setPassword(authService.encode(pwd == null || pwd.isBlank() ? "123456" : pwd));
        userMapper.insert(u);
        return R.ok();
    }

    @PutMapping("/{id}")
    public R<Void> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        SysUser u = new SysUser();
        u.setId(id);
        u.setRealName(str(body.get("realName")));
        u.setPhone(str(body.get("phone")));
        u.setEmail(str(body.get("email")));
        u.setStatus(str(body.get("status")));
        u.setAvatar(str(body.get("avatar")));
        if (body.get("roleId") != null) {
            u.setRoleId(Long.valueOf(String.valueOf(body.get("roleId"))));
        }
        userMapper.updateById(u);
        return R.ok();
    }

    @PostMapping("/{id}/reset")
    public R<Void> reset(@PathVariable Long id) {
        SysUser u = new SysUser();
        u.setId(id);
        u.setPassword(authService.encode("123456"));
        u.setLoginFail(0);
        userMapper.updateById(u);
        return R.ok();
    }

    @GetMapping("/orgs")
    public R<List<SysOrg>> orgs() {
        return R.ok(orgMapper.selectList(new QueryWrapper<SysOrg>().orderByAsc("sort")));
    }

    private String str(Object o) {
        return o == null ? null : String.valueOf(o);
    }
}""")

add("src/main/java/com/grad/ws/controller/MessageController.java", """
package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.SysMessage;
import com.grad.ws.mapper.SysMessageMapper;
import org.springframework.web.bind.annotation.*;

/** 站内消息：当前用户的消息列表与已读标记 */
@RestController
@RequestMapping("/api/message")
public class MessageController {

    private final SysMessageMapper msgMapper;

    public MessageController(SysMessageMapper msgMapper) {
        this.msgMapper = msgMapper;
    }

    @GetMapping("/page")
    public R<PageResult<SysMessage>> page(@RequestParam(defaultValue = "1") long page,
                                          @RequestParam(defaultValue = "20") long size) {
        Page<SysMessage> p = msgMapper.selectPage(new Page<>(page, size),
                new QueryWrapper<SysMessage>().eq("receiver_id", UserContext.userId()).orderByDesc("create_time"));
        return R.ok(new PageResult<>(p.getTotal(), page, size, p.getRecords()));
    }

    @PostMapping("/{id}/read")
    public R<Void> read(@PathVariable Long id) {
        SysMessage m = new SysMessage();
        m.setId(id);
        m.setReadFlag(1);
        msgMapper.updateById(m);
        return R.ok();
    }
}""")

print("biz part3", len(FILES))
