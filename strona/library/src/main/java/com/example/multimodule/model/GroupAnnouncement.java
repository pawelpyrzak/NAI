package com.example.multimodule.model;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
@NoArgsConstructor
public class GroupAnnouncement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    private Group group;

    private LocalDateTime startTime;

    private LocalDateTime endTime;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    public GroupAnnouncement(Group group, LocalDateTime startTime, LocalDateTime endTime, String content) {
        this.group = group;
        this.startTime = startTime;
        this.endTime = endTime;
        this.content = content;
    }
}
