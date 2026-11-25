package com.grad.ws.common;

import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** 全局异常：业务异常返回 500 + 中文提示，参数校验返回 400 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public R<Void> biz(BizException e) {
        return R.fail(500, e.getMessage());
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public R<Void> valid(Exception e) {
        return R.fail(400, "参数校验失败，请检查必填项");
    }

    @ExceptionHandler(Exception.class)
    public R<Void> other(Exception e) {
        e.printStackTrace();
        return R.fail(500, "系统繁忙：" + e.getMessage());
    }
}
