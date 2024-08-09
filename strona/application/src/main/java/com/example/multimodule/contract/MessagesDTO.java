package com.example.multimodule.contract;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class MessagesDTO {
    private String content;
    private String author;
    private LocalDateTime timestamp;
    private String chatName;
    private String platformName;

}
