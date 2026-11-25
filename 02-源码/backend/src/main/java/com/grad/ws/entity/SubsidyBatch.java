package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 补贴批次 */
@Data
@TableName("subsidy_batch")
public class SubsidyBatch {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String batchNo;
    private Long semesterId;
    private String summaryMonth;
    private Integer personCount;
    private BigDecimal totalHours;
    private BigDecimal totalAmount;
    private String status;
    private LocalDateTime auditTime;
    private LocalDateTime createTime;
}
