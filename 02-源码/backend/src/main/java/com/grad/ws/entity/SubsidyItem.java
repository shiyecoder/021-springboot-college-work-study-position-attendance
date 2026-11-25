package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 补贴明细 */
@Data
@TableName("subsidy_item")
public class SubsidyItem {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long batchId;
    private Long studentId;
    private Long postId;
    private BigDecimal validHours;
    private BigDecimal hourRate;
    private BigDecimal factor;
    private BigDecimal amount;
    private String payStatus;
    private LocalDateTime payTime;
    private String failReason;
    private LocalDateTime createTime;
}
