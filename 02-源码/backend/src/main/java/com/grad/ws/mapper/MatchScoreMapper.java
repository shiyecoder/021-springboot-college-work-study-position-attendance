package com.grad.ws.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.ws.entity.MatchScore;
import org.apache.ibatis.annotations.Mapper;

/** 匹配计算留痕 Mapper */
@Mapper
public interface MatchScoreMapper extends BaseMapper<MatchScore> {
}
