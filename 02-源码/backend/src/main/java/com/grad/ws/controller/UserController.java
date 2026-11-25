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
}
