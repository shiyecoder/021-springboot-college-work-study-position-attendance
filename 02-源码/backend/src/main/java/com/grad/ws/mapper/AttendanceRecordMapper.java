package com.grad.ws.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.ws.entity.AttendanceRecord;
import org.apache.ibatis.annotations.Mapper;

/** 考勤记录 Mapper */
@Mapper
public interface AttendanceRecordMapper extends BaseMapper<AttendanceRecord> {
}
