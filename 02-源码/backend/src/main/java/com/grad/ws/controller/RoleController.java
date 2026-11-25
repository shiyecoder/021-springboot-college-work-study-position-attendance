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
}
