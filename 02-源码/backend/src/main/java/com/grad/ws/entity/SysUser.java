package com.grad.ws.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;


/** 用户 */
@Data
@TableName("sys_user")
public class SysUser {

    @TableId(type = IdType.AUTO)
    private Long id;
    /** 登录账号 */
    private String username;
    /** BCrypt 密文 */
    private String password;
    /** 姓名 */
    private String realName;
    private Long roleId;
    private Long orgId;
    /** 学号 */
    private String studentNo;
    private String phone;
    private String email;
    /** 头像 */
    private String avatar;
    private String gender;
    private String status;
    /** 连续失败次数 */
    private Integer loginFail;
    /** 锁定截止 */
    private LocalDateTime lockUntil;
    private LocalDateTime lastLogin;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    @TableLogic
    private Integer deleted;
}
