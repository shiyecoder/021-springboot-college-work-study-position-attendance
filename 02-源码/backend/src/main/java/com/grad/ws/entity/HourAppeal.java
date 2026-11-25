package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 工时申诉 */
@Data
@TableName("hour_appeal")
public class HourAppeal {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long summaryId;
    private Long studentId;
    private BigDecimal appealHours;
    private String reason;
    private String status;
    private LocalDateTime handleTime;
    private String handleRemark;
    private LocalDateTime createTime;
}
