package com.example.multimodule.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "\"Chat\"")
public class Chat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private UUID uuid;

    @Column(nullable = false)
    private String chatMainId;

    @ManyToOne
    @JoinColumn(name = "chat_Platform_id", nullable = false)
    private ChatPlatform chatPlatform;

    @OneToMany(mappedBy = "chat")
    private Set<File> files =new HashSet<>();

    @OneToMany(mappedBy = "chat")
    private Set<Message> messages =new HashSet<>();

    @ManyToMany
    @JoinTable(
            name = "Group_Chat_Mapping",
            joinColumns = @JoinColumn(name = "chat_id"),
            inverseJoinColumns = @JoinColumn(name = "group_id")
    )
    private Set<Group> groups  =new HashSet<>();

    public Chat(String name, UUID uuid, String chatMainId, ChatPlatform chatPlatform) {
        this.name = name;
        this.uuid = uuid;
        this.chatMainId = chatMainId;
        this.chatPlatform = chatPlatform;

    }
}
