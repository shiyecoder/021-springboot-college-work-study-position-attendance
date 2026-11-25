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
}
