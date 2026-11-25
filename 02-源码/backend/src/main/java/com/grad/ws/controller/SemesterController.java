package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.entity.Semester;
import com.grad.ws.mapper.SemesterMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 学期：通用增删改查 + 服务端分页 */
@RestController
@RequestMapping("/api/semester")
public class SemesterController {

    private final SemesterMapper mapper;

    public SemesterController(SemesterMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<Semester>> page(@RequestParam(defaultValue = "1") long page,
                                     @RequestParam(defaultValue = "10") long size,
                                     @RequestParam(required = false) String kw,
                                     @RequestParam(required = false) String status,
                                     @RequestParam(required = false) Long pid) {
        QueryWrapper<Semester> w = new QueryWrapper<>();
        if (kw != null && !kw.isBlank()) {
            w.like("term_name", kw).or().like("id", kw);
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        if (pid != null) {
            w.eq("semester_id", pid);
        }
        w.orderByDesc("id");
        Page<Semester> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), page, size, p.getRecords()));
    }

    @GetMapping("/list")
    public R<List<Semester>> list() {
        return R.ok(mapper.selectList(new QueryWrapper<Semester>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<Semester> get(@PathVariable Long id) {
        return R.ok(mapper.selectById(id));
    }

    @PostMapping
    public R<Semester> save(@RequestBody Semester body) {
        body.setId(null);
        mapper.insert(body);
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<Semester> update(@PathVariable Long id, @RequestBody Semester body) {
        body.setId(id);
        mapper.updateById(body);
        return R.ok(body);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        mapper.deleteById(id);
        return R.ok();
    }
}
