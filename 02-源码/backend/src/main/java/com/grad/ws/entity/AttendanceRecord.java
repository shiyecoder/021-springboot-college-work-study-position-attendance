package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 考勤记录 */
@Data
@TableName("attendance_record")
public class AttendanceRecord {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long shiftId;
    private Long studentId;
    private Long postId;
    private LocalDate workDate;
    private LocalDateTime checkInTime;
    private LocalDateTime checkOutTime;
    private BigDecimal actualHours;
    private BigDecimal validHours;
    private String status;
    private String abnormalReason;
    private String evidenceImage;
    private String verifyStatus;
    private LocalDateTime createTime;
}
