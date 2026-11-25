package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 录用记录 */
@Data
@TableName("employment_record")
public class EmploymentRecord {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long postId;
    private Long applicationId;
    private Long studentId;
    private Long teacherId;
    private LocalDateTime employTime;
    private String status;
    private String remark;
    private LocalDateTime createTime;
}
