package com.example.multimodule.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.HashSet;
import java.util.Set;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "\"Chat\"")
public class Chat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ManyToOne
    @JoinColumn(name = "Group_id")
    private Group group;

    @ManyToOne
    @JoinColumn(name = "Chat_Platforms_id", nullable = false)
    private ChatPlatform chatPlatform;

    @ManyToMany(mappedBy = "chats")
    private Set<Group> groups = new HashSet<>();
}
