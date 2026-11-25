package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 学期 */
@Data
@TableName("semester")
public class Semester {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String termName;
    private LocalDate startDate;
    private LocalDate endDate;
    private BigDecimal monthHourLimit;
    private String status;
    private LocalDateTime createTime;
}
