package com.grad.ws.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserializer;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateSerializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/** 时间格式统一为 yyyy-MM-dd HH:mm:ss / yyyy-MM-dd，前后端一致 */
@Configuration
public class JacksonConfig {

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper om = new ObjectMapper();
        JavaTimeModule m = new JavaTimeModule();
        m.addSerializer(LocalDateTime.class, new LocalDateTimeSerializer(DTF));
        m.addDeserializer(LocalDateTime.class, new LocalDateTimeDeserializer(DTF));
        m.addSerializer(LocalDate.class, new LocalDateSerializer(DF));
        m.addDeserializer(LocalDate.class, new LocalDateDeserializer(DF));
        om.registerModule(m);
        om.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return om;
    }
}
