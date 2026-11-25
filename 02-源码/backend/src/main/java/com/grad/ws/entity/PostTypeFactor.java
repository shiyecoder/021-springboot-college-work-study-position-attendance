package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 岗位系数 */
@Data
@TableName("post_type_factor")
public class PostTypeFactor {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String postType;
    private BigDecimal factor;
    private String remark;
    private String status;
}
