package com.example.multimodule.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;


@Entity
@Table(name = "UsersRole")
@Getter
@Setter
public class UserRole {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne
    @JoinColumn(name = "Role_id")
    private Role role;

    @ManyToOne
    @JoinColumn(name = "User_id")
    private User user;
}
