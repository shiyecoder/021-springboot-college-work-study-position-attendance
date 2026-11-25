package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 月度工时 */
@Data
@TableName("hour_summary")
public class HourSummary {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long studentId;
    private Long postId;
    private String summaryMonth;
    private BigDecimal planHours;
    private BigDecimal actualHours;
    private BigDecimal validHours;
    private BigDecimal limitHours;
    private String status;
    private LocalDateTime confirmTime;
    private LocalDateTime createTime;
}
