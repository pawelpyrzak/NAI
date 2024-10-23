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
@Entity
@NoArgsConstructor
@Table(name = "\"Group\"")
public class Group {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, length = 32)
    private UUID uuid;

    @OneToMany(mappedBy = "group")
    private Set<GroupAnnouncement> announcements = new HashSet<>();

    @ManyToMany
    @JoinTable(
            name = "Group_Chat_Mapping",
            joinColumns = @JoinColumn(name = "group_id"),
            inverseJoinColumns = @JoinColumn(name = "chat_id")
    )
    private Set<Chat> chats = new HashSet<>();

    @ManyToMany
    @JoinTable(
            name = "User_Group",
            joinColumns = @JoinColumn(name = "group_id"),
            inverseJoinColumns = @JoinColumn(name = "user_id")
    )
    private Set<User> users = new HashSet<>();

    public Group(String name, UUID uuid) {
        this.name = name;
        this.uuid = uuid;
    }
}
