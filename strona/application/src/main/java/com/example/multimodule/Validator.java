package com.example.multimodule;

import io.micrometer.common.util.StringUtils;
import org.apache.commons.text.StringEscapeUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Validator {
    private static final Logger LOGGER = LoggerFactory.getLogger(Validator.class);

    public static String validate(String data) {
        LOGGER.info("validate");
        if (StringUtils.isEmpty(data)) throw new NullPointerException("Please fill in all the required fields 1");
        String trimmedData = data.trim();
        String unescapedData = trimmedData.replace("\\", "");
        if (StringUtils.isEmpty(data)) throw new NullPointerException("Please fill in all the required fields 2");
        return StringEscapeUtils.escapeHtml4(unescapedData);
    }
}
