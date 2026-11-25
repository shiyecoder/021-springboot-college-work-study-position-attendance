package com.grad.ws.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.ws.common.PageResult;
import com.grad.ws.common.R;
import com.grad.ws.entity.HourAppeal;
import com.grad.ws.mapper.HourAppealMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 工时申诉：通用增删改查 + 服务端分页 */
@RestController
@RequestMapping("/api/appeal")
public class HourAppealController {

    private final HourAppealMapper mapper;

    public HourAppealController(HourAppealMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<HourAppeal>> page(@RequestParam(defaultValue = "1") long page,
                                     @RequestParam(defaultValue = "10") long size,
                                     @RequestParam(required = false) String kw,
                                     @RequestParam(required = false) String status,
                                     @RequestParam(required = false) Long pid) {
        QueryWrapper<HourAppeal> w = new QueryWrapper<>();
        if (kw != null && !kw.isBlank()) {
            w.like("reason", kw).or().like("id", kw);
        }
        if (status != null && !status.isBlank()) {
            w.eq("status", status);
        }
        if (pid != null) {
            w.eq("semester_id", pid);
        }
        w.orderByDesc("id");
        Page<HourAppeal> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), page, size, p.getRecords()));
    }

    @GetMapping("/list")
    public R<List<HourAppeal>> list() {
        return R.ok(mapper.selectList(new QueryWrapper<HourAppeal>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<HourAppeal> get(@PathVariable Long id) {
        return R.ok(mapper.selectById(id));
    }

    @PostMapping
    public R<HourAppeal> save(@RequestBody HourAppeal body) {
        body.setId(null);
        mapper.insert(body);
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<HourAppeal> update(@PathVariable Long id, @RequestBody HourAppeal body) {
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
