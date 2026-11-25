package com.grad.ws.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.ws.common.BizException;
import com.grad.ws.common.JwtUtil;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.*;
import com.grad.ws.mapper.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

/** 登录、当前用户、动态菜单、资料与密码 */
@Service
public class AuthService {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final SysOrgMapper orgMapper;
    private final PasswordEncoder encoder;
    private final JwtUtil jwtUtil;

    @Value("${app.login-fail-limit:5}")
    private int failLimit;
    @Value("${app.login-lock-minutes:10}")
    private int lockMinutes;

    public AuthService(SysUserMapper userMapper, SysRoleMapper roleMapper, SysMenuMapper menuMapper,
                       SysRoleMenuMapper roleMenuMapper, SysOrgMapper orgMapper,
                       PasswordEncoder encoder, JwtUtil jwtUtil) {
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.menuMapper = menuMapper;
        this.roleMenuMapper = roleMenuMapper;
        this.orgMapper = orgMapper;
        this.encoder = encoder;
        this.jwtUtil = jwtUtil;
    }

    /** 登录：连续失败 5 次锁定 10 分钟；密码仅校验不回传 */
    public Map<String, Object> login(String username, String password) {
        if (username == null || password == null) {
            throw new BizException("请输入账号和密码");
        }
        SysUser u = userMapper.selectOne(new QueryWrapper<SysUser>().eq("username", username.trim()).last("limit 1"));
        if (u == null) {
            throw new BizException("账号或密码错误");
        }
        if (u.getLockUntil() != null && u.getLockUntil().isAfter(LocalDateTime.now())) {
            throw new BizException("账号已临时锁定，请稍后再试");
        }
        if (!"1".equals(u.getStatus())) {
            throw new BizException("账号已停用，请联系管理员");
        }
        if (!encoder.matches(password, u.getPassword())) {
            int fail = (u.getLoginFail() == null ? 0 : u.getLoginFail()) + 1;
            SysUser up = new SysUser();
            up.setId(u.getId());
            up.setLoginFail(fail);
            if (fail >= failLimit) {
                up.setLockUntil(LocalDateTime.now().plusMinutes(lockMinutes));
                up.setLoginFail(0);
            }
            userMapper.updateById(up);
            throw new BizException("账号或密码错误，还可尝试 " + Math.max(0, failLimit - fail) + " 次");
        }
        SysUser up = new SysUser();
        up.setId(u.getId());
        up.setLoginFail(0);
        up.setLockUntil(null);
        up.setLastLogin(LocalDateTime.now());
        userMapper.updateById(up);

        SysRole role = roleMapper.selectById(u.getRoleId());
        Map<String, Object> claims = new HashMap<>();
        claims.put("name", u.getRealName());
        claims.put("role", role == null ? "STUDENT" : role.getRoleCode());
        claims.put("orgId", u.getOrgId());
        claims.put("scope", role == null ? "SELF" : role.getDataScope());
        String token = jwtUtil.create(claims, u.getId());

        Map<String, Object> res = new LinkedHashMap<>();
        res.put("token", token);
        res.put("user", toUser(u, role));
        res.put("menus", menusOf(u.getRoleId()));
        return res;
    }

    /** 用户信息（剔除 password 字段） */
    public Map<String, Object> toUser(SysUser u, SysRole role) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", u.getId());
        m.put("username", u.getUsername());
        m.put("realName", u.getRealName());
        m.put("studentNo", u.getStudentNo());
        m.put("phone", u.getPhone());
        m.put("email", u.getEmail());
        m.put("avatar", u.getAvatar());
        m.put("gender", u.getGender());
        m.put("orgId", u.getOrgId());
        if (u.getOrgId() != null) {
            SysOrg org = orgMapper.selectById(u.getOrgId());
            m.put("orgName", org == null ? "" : org.getOrgName());
        }
        m.put("roleId", u.getRoleId());
        m.put("roleCode", role == null ? "" : role.getRoleCode());
        m.put("roleName", role == null ? "" : role.getRoleName());
        m.put("dataScope", role == null ? "SELF" : role.getDataScope());
        return m;
    }

    /** 按角色取菜单：只用 menu_type='M' 且 visible=1 的项，按 sort 升序 */
    public List<Map<String, Object>> menusOf(Long roleId) {
        List<SysRoleMenu> rms = roleMenuMapper.selectList(new QueryWrapper<SysRoleMenu>().eq("role_id", roleId));
        Set<Long> ids = new HashSet<>();
        rms.forEach(r -> ids.add(r.getMenuId()));
        if (ids.isEmpty()) {
            return List.of();
        }
        List<SysMenu> menus = menuMapper.selectList(new QueryWrapper<SysMenu>()
                .in("id", ids).eq("menu_type", "M").eq("visible", 1).eq("status", "1").orderByAsc("sort"));
        List<Map<String, Object>> out = new ArrayList<>();
        for (SysMenu m : menus) {
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("id", m.getId());
            o.put("name", m.getMenuName());
            o.put("path", m.getPath());
            o.put("icon", m.getIcon());
            out.add(o);
        }
        return out;
    }

    public Map<String, Object> me() {
        SysUser u = userMapper.selectById(UserContext.userId());
        if (u == null) {
            throw new BizException("登录状态失效");
        }
        SysRole role = roleMapper.selectById(u.getRoleId());
        Map<String, Object> m = toUser(u, role);
        m.put("menus", menusOf(u.getRoleId()));
        return m;
    }

    public void updateProfile(String realName, String phone, String email, String avatar) {
        SysUser up = new SysUser();
        up.setId(UserContext.userId());
        up.setRealName(realName);
        up.setPhone(phone);
        up.setEmail(email);
        if (avatar != null && !avatar.isBlank()) {
            up.setAvatar(avatar);
        }
        userMapper.updateById(up);
    }

    public void changePassword(String oldPwd, String newPwd) {
        SysUser u = userMapper.selectById(UserContext.userId());
        if (u == null || !encoder.matches(oldPwd == null ? "" : oldPwd, u.getPassword())) {
            throw new BizException("原密码不正确");
        }
        if (newPwd == null || newPwd.length() < 6) {
            throw new BizException("新密码至少 6 位");
        }
        SysUser up = new SysUser();
        up.setId(u.getId());
        up.setPassword(encoder.encode(newPwd));
        userMapper.updateById(up);
    }

    public String encode(String raw) {
        return encoder.encode(raw);
    }
}
