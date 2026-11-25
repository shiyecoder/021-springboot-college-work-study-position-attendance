package com.grad.ws.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.ws.entity.HourSummary;
import org.apache.ibatis.annotations.Mapper;

/** 月度工时 Mapper */
@Mapper
public interface HourSummaryMapper extends BaseMapper<HourSummary> {
}
