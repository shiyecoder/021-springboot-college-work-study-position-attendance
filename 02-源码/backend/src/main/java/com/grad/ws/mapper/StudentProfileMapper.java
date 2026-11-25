package com.grad.ws.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.ws.entity.StudentProfile;
import org.apache.ibatis.annotations.Mapper;

/** 学生档案 Mapper */
@Mapper
public interface StudentProfileMapper extends BaseMapper<StudentProfile> {
}
