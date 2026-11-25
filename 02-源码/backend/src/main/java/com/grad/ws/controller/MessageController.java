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
}
