package com.example.multimodule.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@Entity
public class Group {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "group")
    private List<UserGroupMapping> userGroups;

    private String name;

    @Column( length = 64)
    private String token;

    public Group( String name, String token) {
        this.name = name;
        this.token = token;
    }
}
