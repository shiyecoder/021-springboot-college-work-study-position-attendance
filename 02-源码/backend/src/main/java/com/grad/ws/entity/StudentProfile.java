package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 学生档案 */
@Data
@TableName("student_profile")
public class StudentProfile {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String college;
    private String major;
    private String grade;
    /** 困难认定等级 */
    private String difficultyLevel;
    private String skillTags;
    private String availableTime;
    private String bankCard;
    private String resumePath;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
