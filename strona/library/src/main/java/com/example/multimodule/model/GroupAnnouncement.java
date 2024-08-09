package com.example.multimodule.model;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import jakarta.persistence.*;
import java.sql.Timestamp;
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
    @JoinColumn(name = "UserGroupMapping_id")
    private UserGroupMapping userGroupMapping;

    private LocalDateTime startTime;

    private LocalDateTime endTime;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    public GroupAnnouncement(LocalDateTime startTime, LocalDateTime endTime, String content) {
        this.startTime = startTime;
        this.endTime = endTime;
        this.content = content;
    }
}
