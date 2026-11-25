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
}
