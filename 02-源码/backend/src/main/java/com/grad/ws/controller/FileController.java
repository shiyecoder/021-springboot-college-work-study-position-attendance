package com.grad.ws.controller;

import com.grad.ws.common.BizException;
import com.grad.ws.common.R;
import com.grad.ws.common.UserContext;
import com.grad.ws.entity.SysAttachment;
import com.grad.ws.mapper.SysAttachmentMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/** 文件上传：白名单扩展名校验，落盘到项目根 uploads/，返回相对路径 */
@RestController
@RequestMapping("/api/file")
public class FileController {

    private static final Set<String> ALLOW = Set.of("jpg", "jpeg", "png", "webp", "pdf", "doc", "docx", "xls", "xlsx");

    @Value("${app.upload-dir:./uploads}")
    private String uploadDir;

    private final SysAttachmentMapper attMapper;

    public FileController(SysAttachmentMapper attMapper) {
        this.attMapper = attMapper;
    }

    @PostMapping("/upload")
    public R<Map<String, Object>> upload(@RequestParam("file") MultipartFile file,
                                         @RequestParam(required = false) String bizType,
                                         @RequestParam(required = false) String bizNo) {
        if (file == null || file.isEmpty()) {
            throw new BizException("请选择要上传的文件");
        }
        String name = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = name.contains(".") ? name.substring(name.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!ALLOW.contains(ext)) {
            throw new BizException("不支持的文件类型：" + ext);
        }
        if (file.getSize() > 20 * 1024 * 1024L) {
            throw new BizException("单个文件不能超过 20MB");
        }
        try {
            String day = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
            Path dir = Paths.get(uploadDir, day).toAbsolutePath().normalize();
            Files.createDirectories(dir);
            String fileName = UUID.randomUUID().toString().replace("-", "") + "." + ext;
            Path target = dir.resolve(fileName);
            file.transferTo(target);
            String rel = "/uploads/" + day + "/" + fileName;

            SysAttachment att = new SysAttachment();
            att.setBizType(bizType == null ? "COMMON" : bizType);
            att.setBizNo(bizNo);
            att.setFileName(name);
            att.setFilePath(rel);
            att.setFileSize(file.getSize());
            att.setUploaderId(UserContext.userId());
            attMapper.insert(att);

            Map<String, Object> m = new LinkedHashMap<>();
            m.put("path", rel);
            m.put("name", name);
            m.put("size", file.getSize());
            return R.ok(m);
        } catch (Exception e) {
            throw new BizException("上传失败：" + e.getMessage());
        }
    }
}
