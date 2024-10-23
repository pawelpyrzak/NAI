package com.example.multimodule.contract;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.UUID;

@Getter
@AllArgsConstructor
public class ChatDTO {
    private UUID chat_uuid;
    private String chatPlatformName;
}
