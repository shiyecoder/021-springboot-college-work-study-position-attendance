package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 匹配规则 */
@Data
@TableName("match_rule")
public class MatchRule {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String version;
    private Integer wDifficulty;
    private Integer wConflict;
    private Integer wSkill;
    private Integer wHours;
    private Integer wAbsent;
    private Integer wPrefer;
    private String status;
    private LocalDateTime effectTime;
    private String creator;
    private LocalDateTime createTime;
}
