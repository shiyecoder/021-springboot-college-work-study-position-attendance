package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 匹配计算留痕 */
@Data
@TableName("match_score")
public class MatchScore {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long studentId;
    private Long postId;
    private Long applicationId;
    private String ruleVersion;
    private Integer scoreDifficulty;
    private Integer scoreConflict;
    private Integer scoreSkill;
    private Integer scoreHours;
    private Integer scoreAbsent;
    private Integer scorePrefer;
    private BigDecimal totalScore;
    private String grade;
    private String snapshotJson;
    private String adjustGrade;
    private String adjustReason;
    private String adjustBy;
    private LocalDateTime createTime;
}
