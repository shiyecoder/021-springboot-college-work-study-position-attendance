package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 学期评价 */
@Data
@TableName("term_evaluation")
public class TermEvaluation {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long studentId;
    private Long postId;
    private Long semesterId;
    private Integer attendanceScore;
    private Integer dutyScore;
    private Integer skillScore;
    private Integer teamScore;
    private BigDecimal totalScore;
    private String comment;
    private String feedback;
    private String status;
    private LocalDateTime createTime;
}
