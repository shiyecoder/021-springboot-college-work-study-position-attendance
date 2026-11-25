# -*- coding: utf-8 -*-
"""NEW-021 后端核心（common/config）+ 业务控制器。"""
import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "main" / "java" / "com" / "grad" / "ws"
RES = ROOT / "src" / "main" / "resources"
PKG = "com.grad.ws"
FILES = {}


def add(rel, code):
    FILES[rel] = code.strip() + "\n"


# ---------------- pom ----------------
add("pom.xml", """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.5</version>
        <relativePath/>
    </parent>
    <groupId>com.grad</groupId>
    <artifactId>work-study</artifactId>
    <version>1.0.0</version>
    <name>work-study</name>
    <description>高校勤工助学岗位与考勤管理系统</description>
    <properties>
        <java.version>17</java.version>
        <mybatis-plus.version>3.5.7</mybatis-plus.version>
        <jjwt.version>0.12.5</jjwt.version>
    </properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
        <dependency>
            <groupId>com.baomidou</groupId><artifactId>mybatis-plus-spring-boot3-starter</artifactId>
            <version>${mybatis-plus.version}</version>
        </dependency>
        <dependency><groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId><scope>runtime</scope></dependency>
        <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-api</artifactId><version>${jjwt.version}</version></dependency>
        <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-impl</artifactId><version>${jjwt.version}</version><scope>runtime</scope></dependency>
        <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-jackson</artifactId><version>${jjwt.version}</version><scope>runtime</scope></dependency>
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
    </dependencies>
    <build>
        <finalName>work-study</finalName>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId>
                <configuration><excludes><exclude>
                    <groupId>org.projectlombok</groupId><artifactId>lombok</artifactId>
                </exclude></excludes></configuration>
            </plugin>
        </plugins>
    </build>
</project>""")

# ---------------- 配置 ----------------
add("src/main/resources/application.yml", """
server:
  port: 8082
  servlet:
    encoding:
      charset: UTF-8
      force: true

spring:
  application:
    name: work-study
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://127.0.0.1:3306/new_021?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false
    username: root
    password: "123456"
    hikari:
      maximum-pool-size: 8
      minimum-idle: 2
  servlet:
    multipart:
      max-file-size: 20MB
      max-request-size: 60MB
  jackson:
    time-zone: Asia/Shanghai

mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.nologging.NoLoggingImpl
  global-config:
    db-config:
      id-type: auto

app:
  upload-dir: ./uploads
  jwt-secret: work-study-graduation-project-2026-secret-key-please-change-it
  jwt-expire-hours: 12
  login-fail-limit: 5
  login-lock-minutes: 10

logging:
  level:
    root: warn
    com.grad.ws: info
""")

add("src/main/java/com/grad/ws/WorkStudyApplication.java", """
package com.grad.ws;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** 高校勤工助学岗位与考勤管理系统启动类 */
@SpringBootApplication
public class WorkStudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(WorkStudyApplication.class, args);
    }
}""")

add("src/main/java/com/grad/ws/common/R.java", """
package com.grad.ws.common;

import java.util.UUID;

/** 统一响应：业务码 + 提示 + 数据 + 请求编号，0 表示成功 */
public class R<T> {
    private int code;
    private String msg;
    private T data;
    private String requestId;

    public R() {
    }

    public R(int code, String msg, T data) {
        this.code = code;
        this.msg = msg;
        this.data = data;
        this.requestId = UUID.randomUUID().toString().substring(0, 8);
    }

    public static <T> R<T> ok(T data) {
        return new R<>(0, "success", data);
    }

    public static <T> R<T> ok() {
        return new R<>(0, "success", null);
    }

    public static <T> R<T> fail(int code, String msg) {
        return new R<>(code, msg, null);
    }

    public static <T> R<T> fail(String msg) {
        return new R<>(500, msg, null);
    }

    public int getCode() { return code; }
    public void setCode(int code) { this.code = code; }
    public String getMsg() { return msg; }
    public void setMsg(String msg) { this.msg = msg; }
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }
}""")

add("src/main/java/com/grad/ws/common/PageResult.java", """
package com.grad.ws.common;

import java.util.List;

/** 分页返回：总数、页码、每页条数与列表 */
public class PageResult<T> {
    private long total;
    private long page;
    private long size;
    private List<T> list;

    public PageResult(long total, long page, long size, List<T> list) {
        this.total = total;
        this.page = page;
        this.size = size;
        this.list = list;
    }

    public long getTotal() { return total; }
    public void setTotal(long total) { this.total = total; }
    public long getPage() { return page; }
    public void setPage(long page) { this.page = page; }
    public long getSize() { return size; }
    public void setSize(long size) { this.size = size; }
    public List<T> getList() { return list; }
    public void setList(List<T> list) { this.list = list; }
}""")

add("src/main/java/com/grad/ws/common/BizException.java", """
package com.grad.ws.common;

/** 业务异常：由全局异常处理器转成统一响应，不打印堆栈 */
public class BizException extends RuntimeException {
    public BizException(String message) {
        super(message);
    }
}""")

add("src/main/java/com/grad/ws/common/GlobalExceptionHandler.java", """
package com.grad.ws.common;

import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** 全局异常：业务异常返回 500 + 中文提示，参数校验返回 400 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public R<Void> biz(BizException e) {
        return R.fail(500, e.getMessage());
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public R<Void> valid(Exception e) {
        return R.fail(400, "参数校验失败，请检查必填项");
    }

    @ExceptionHandler(Exception.class)
    public R<Void> other(Exception e) {
        e.printStackTrace();
        return R.fail(500, "系统繁忙：" + e.getMessage());
    }
}""")

add("src/main/java/com/grad/ws/common/JwtUtil.java", """
package com.grad.ws.common;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;

/** JWT 签发与解析：载荷含 userId、姓名、角色、部门与数据范围 */
@Component
public class JwtUtil {

    @Value("${app.jwt-secret}")
    private String secret;

    @Value("${app.jwt-expire-hours:12}")
    private long expireHours;

    private SecretKey key() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    public String create(Map<String, Object> claims, Long userId) {
        Date now = new Date();
        return Jwts.builder()
                .claims(claims)
                .subject(String.valueOf(userId))
                .issuedAt(now)
                .expiration(new Date(now.getTime() + expireHours * 3600_000L))
                .signWith(key())
                .compact();
    }

    public Claims parse(String token) {
        return Jwts.parser().verifyWith(key()).build().parseSignedClaims(token).getPayload();
    }
}""")

add("src/main/java/com/grad/ws/common/UserContext.java", """
package com.grad.ws.common;

/** 当前登录人上下文（ThreadLocal）：数据范围 SELF / DEPT / ALL */
public class UserContext {

    public record LoginUser(Long id, String name, String roleCode, Long orgId, String dataScope) {
    }

    private static final ThreadLocal<LoginUser> HOLDER = new ThreadLocal<>();

    public static void set(LoginUser u) { HOLDER.set(u); }
    public static LoginUser get() { return HOLDER.get(); }

    public static Long userId() {
        LoginUser u = HOLDER.get();
        return u == null ? null : u.id();
    }

    public static String name() {
        LoginUser u = HOLDER.get();
        return u == null ? "系统" : u.name();
    }

    public static String role() {
        LoginUser u = HOLDER.get();
        return u == null ? "" : u.roleCode();
    }

    public static Long orgId() {
        LoginUser u = HOLDER.get();
        return u == null ? null : u.orgId();
    }

    public static boolean isStudent() { return "STUDENT".equals(role()); }
    public static boolean isDept() { return "DEPT".equals(role()); }
    public static boolean isAdmin() { return "ADMIN".equals(role()); }
    public static boolean isFinance() { return "FINANCE".equals(role()); }

    public static void clear() { HOLDER.remove(); }
}""")

add("src/main/java/com/grad/ws/config/MybatisPlusConfig.java", """
package com.grad.ws.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** 分页插件：所有列表走服务端分页 */
@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}""")

add("src/main/java/com/grad/ws/config/JacksonConfig.java", """
package com.grad.ws.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserializer;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateSerializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/** 时间格式统一为 yyyy-MM-dd HH:mm:ss / yyyy-MM-dd，前后端一致 */
@Configuration
public class JacksonConfig {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper om = new ObjectMapper();
        JavaTimeModule m = new JavaTimeModule();
        m.addSerializer(LocalDateTime.class, new LocalDateTimeSerializer(DTF));
        m.addDeserializer(LocalDateTime.class, new LocalDateTimeDeserializer(DTF));
        m.addSerializer(LocalDate.class, new LocalDateSerializer(DF));
        m.addDeserializer(LocalDate.class, new LocalDateDeserializer(DF));
        om.registerModule(m);
        om.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return om;
    }
}""")

add("src/main/java/com/grad/ws/config/WebConfig.java", """
package com.grad.ws.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Paths;

/** 静态资源：/uploads/** 映射到项目根目录 uploads/（相对路径，换机器可用） */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${app.upload-dir:./uploads}")
    private String uploadDir;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String abs = Paths.get(uploadDir).toAbsolutePath().normalize().toString();
        registry.addResourceHandler("/uploads/**").addResourceLocations("file:" + abs + "/").setCachePeriod(3600);
    }
}""")

add("src/main/java/com/grad/ws/config/JwtFilter.java", """
package com.grad.ws.config;

import com.grad.ws.common.JwtUtil;
import com.grad.ws.common.UserContext;
import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

/** 解析 Authorization: Bearer <token>，写入登录人上下文；请求结束清理 ThreadLocal */
@Component
public class JwtFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    public JwtFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            try {
                Claims c = jwtUtil.parse(header.substring(7));
                Long userId = Long.valueOf(c.getSubject());
                Object org = c.get("orgId");
                UserContext.set(new UserContext.LoginUser(userId, String.valueOf(c.get("name")),
                        String.valueOf(c.get("role")), org == null ? null : Long.valueOf(String.valueOf(org)),
                        String.valueOf(c.get("scope"))));
                SecurityContextHolder.getContext().setAuthentication(new UsernamePasswordAuthenticationToken(
                        userId, null, List.of(new SimpleGrantedAuthority("ROLE_" + c.get("role")))));
            } catch (Exception ignored) {
                UserContext.clear();
                SecurityContextHolder.clearContext();
            }
        }
        try {
            chain.doFilter(request, response);
        } finally {
            UserContext.clear();
            SecurityContextHolder.clearContext();
        }
    }
}""")

add("src/main/java/com/grad/ws/config/SecurityConfig.java", """
package com.grad.ws.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.grad.ws.common.R;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

/** 安全配置：无状态 JWT，登录/静态资源放行，其余需认证；401/403 返回统一 JSON */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtFilter jwtFilter;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public SecurityConfig(JwtFilter jwtFilter) {
        this.jwtFilter = jwtFilter;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(c -> c.disable())
                .cors(c -> c.configurationSource(corsSource()))
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(a -> a
                        .requestMatchers("/api/auth/login", "/api/auth/captcha").permitAll()
                        .requestMatchers("/uploads/**", "/error").permitAll()
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                        .anyRequest().authenticated())
                .exceptionHandling(e -> e
                        .authenticationEntryPoint((req, res, ex) -> write(res, 401, "登录已过期，请重新登录"))
                        .accessDeniedHandler((req, res, ex) -> write(res, 403, "没有该操作权限")))
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    private void write(HttpServletResponse res, int code, String msg) throws java.io.IOException {
        res.setStatus(200);
        res.setContentType("application/json;charset=UTF-8");
        res.getWriter().write(objectMapper.writeValueAsString(R.fail(code, msg)));
    }

    @Bean
    public CorsConfigurationSource corsSource() {
        CorsConfiguration cfg = new CorsConfiguration();
        cfg.setAllowedOriginPatterns(List.of("http://localhost:*", "http://127.0.0.1:*"));
        cfg.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        cfg.setAllowedHeaders(List.of("*"));
        cfg.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource s = new UrlBasedCorsConfigurationSource();
        s.registerCorsConfiguration("/**", cfg);
        return s;
    }
}""")

# ---------------- Auth ----------------
add("src/main/java/com/grad/ws/service/AuthService.java", """
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
}""")

add("src/main/java/com/grad/ws/controller/AuthController.java", """
package com.grad.ws.controller;

import com.grad.ws.common.R;
import com.grad.ws.service.AuthService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 认证：登录、当前用户、动态菜单、改资料、改密码 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public R<Map<String, Object>> login(@RequestBody Map<String, String> body) {
        return R.ok(authService.login(body.get("username"), body.get("password")));
    }

    @GetMapping("/me")
    public R<Map<String, Object>> me() {
        return R.ok(authService.me());
    }

    @GetMapping("/menus")
    public R<Object> menus() {
        return R.ok(authService.me().get("menus"));
    }

    @PutMapping("/profile")
    public R<Void> profile(@RequestBody Map<String, String> body) {
        authService.updateProfile(body.get("realName"), body.get("phone"), body.get("email"), body.get("avatar"));
        return R.ok();
    }

    @PostMapping("/password")
    public R<Void> password(@RequestBody Map<String, String> body) {
        authService.changePassword(body.get("oldPassword"), body.get("newPassword"));
        return R.ok();
    }
}""")

print("core part1", len(FILES))
