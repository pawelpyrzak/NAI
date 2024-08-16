package com.example.multimodule.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;
import java.util.Set;
import java.util.HashSet;
@Getter
@Setter
@Entity
@Table(name = "\"Group\"")

public class Group {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "group")
    private List<UserGroupMapping> userGroups;

    private String name;

    @Column( length = 64)
    private String token;

    @ManyToMany
    @JoinTable(
            name = "Group_Chat_Mapping",
            joinColumns = @JoinColumn(name = "group_id"),
            inverseJoinColumns = @JoinColumn(name = "chat_id")
    )
    private Set<Chat> chats;

    public Group( String name, String token) {
        this.name = name;
        this.token = token;
        this.chats = new HashSet<>();
    }
    public Group() {
        this.chats = new HashSet<>();
    }
}
