package com.example.multimodule.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
public class Chat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ManyToOne
    @JoinColumn(name = "Group_id")
    private Group group;

    @ManyToOne
    @JoinColumn(name = "ChatPlatforms_id", nullable = false)
    private ChatPlatform chatPlatform;
}
