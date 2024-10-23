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
@Table(name = "\"User\"")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String email;

    @ManyToMany(mappedBy = "users")
    private Set<Group> groups = new HashSet<>();

    @ManyToMany
    @JoinTable(
            name = "users_role", // Nazwa tabeli łączącej
            joinColumns = @JoinColumn(name = "user_id"), // Klucz obcy do `User`
            inverseJoinColumns = @JoinColumn(name = "role_id") // Klucz obcy do `Role`
    )
    private Set<Role> roles = new HashSet<>();

    public User(String firstName, String lastName, String password, String email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.password = password;
        this.email = email;
    }
}
