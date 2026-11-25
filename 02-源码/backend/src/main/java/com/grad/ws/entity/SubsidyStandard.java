package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 补贴标准 */
@Data
@TableName("subsidy_standard")
public class SubsidyStandard {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long semesterId;
    private BigDecimal hourRate;
    private BigDecimal monthHourLimit;
    private BigDecimal specialFactor;
    private LocalDateTime effectTime;
    private LocalDateTime createTime;
}
