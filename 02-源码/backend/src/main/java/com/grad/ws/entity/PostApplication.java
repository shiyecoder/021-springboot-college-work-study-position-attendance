package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 岗位申请 */
@Data
@TableName("post_application")
public class PostApplication {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String applyNo;
    private Long postId;
    private Long studentId;
    private String applyReason;
    private String availableTime;
    private String resumePath;
    private LocalDateTime interviewTime;
    private Double matchScore;
    private String status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
