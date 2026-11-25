package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 菜单 */
@Data
@TableName("sys_menu")
public class SysMenu {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long parentId;
    private String menuName;
    /** M/B */
    private String menuType;
    private String path;
    private String perms;
    private String icon;
    private Integer sort;
    /** 1 显示 0 隐藏 */
    private Integer visible;
    private String status;
    private LocalDateTime createTime;
}
