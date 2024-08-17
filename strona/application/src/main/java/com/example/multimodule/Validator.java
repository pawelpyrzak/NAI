package com.example.multimodule;

import io.micrometer.common.util.StringUtils;
import org.apache.commons.text.StringEscapeUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static io.micrometer.common.util.StringUtils.isEmpty;
import static org.apache.commons.text.StringEscapeUtils.escapeHtml4;

public class Validator {
    private static final Logger LOGGER = LoggerFactory.getLogger(Validator.class);

    public static String validate(String data) {
        LOGGER.info("validate");
        data= escapeHtml4(data.trim().replace("\\", ""));
        if (isEmpty(data)) throw new NullPointerException("Please fill in all the required fields");
        return data;
    }
}
