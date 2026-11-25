package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 业务流转时间轴 */
@Data
@TableName("work_study_log")
public class WorkStudyLog {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String bizType;
    private String bizNo;
    private String fromStatus;
    private String toStatus;
    private String action;
    private String reason;
    private String operator;
    private LocalDateTime createTime;
}
