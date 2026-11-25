package com.grad.ws.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.ws.entity.EmploymentRecord;
import org.apache.ibatis.annotations.Mapper;

/** 录用记录 Mapper */
@Mapper
public interface EmploymentRecordMapper extends BaseMapper<EmploymentRecord> {
}
