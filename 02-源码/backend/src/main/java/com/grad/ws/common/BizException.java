package com.grad.ws.common;

/** 业务异常：由全局异常处理器转成统一响应，不打印堆栈 */
public class BizException extends RuntimeException {
    public BizException(String message) {
        super(message);
    }
}
