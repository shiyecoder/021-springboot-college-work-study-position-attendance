package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 排班 */
@Data
@TableName("work_shift")
public class WorkShift {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long postId;
    private Long studentId;
    private LocalDate shiftDate;
    private String startTime;
    private String endTime;
    private String workPlace;
    private BigDecimal planHours;
    private Integer conflictFlag;
    private String conflictReason;
    private String status;
    private LocalDateTime createTime;
}
