package com.example.multimodule.contract;

import com.example.multimodule.model.Group;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class GroupAnnouncementDTO {
    private Group group;

    private LocalDateTime startTime;

    private LocalDateTime endTime;

    private String content;

}
