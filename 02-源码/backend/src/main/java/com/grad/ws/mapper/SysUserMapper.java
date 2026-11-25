package com.grad.ws.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.ws.entity.SysUser;
import org.apache.ibatis.annotations.Mapper;

/** 用户 Mapper */
@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
}
