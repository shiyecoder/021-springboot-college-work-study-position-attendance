package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 勤工助学岗位 */
@Data
@TableName("work_study_post")
public class WorkStudyPost {

    @TableId(type = IdType.AUTO)
    private Long id;
    /** 岗位编号 */
    private String postNo;
    private String postName;
    private Long deptId;
    private String postType;
    private String workPlace;
    private Integer recruitNum;
    private Integer hiredNum;
    private BigDecimal hourRate;
    private String workPeriod;
    private String abilityReq;
    private String postDesc;
    private BigDecimal budget;
    private Long teacherId;
    private String coverImage;
    private String status;
    private LocalDateTime publishTime;
    /** 乐观锁版本 */
    private Integer version;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    @TableLogic
    private Integer deleted;
}
