package com.example.multimodule;

import org.apache.commons.lang3.RandomStringUtils;

public class KeyGenerator {
    private static final int DEFAULT_LENGTH = 64;
    public static String generateRandomKey(int length) {
        return RandomStringUtils.randomAlphanumeric(length);
    }
    public static String generateRandomKey() {
        return RandomStringUtils.randomAlphanumeric(DEFAULT_LENGTH);
    }

}
