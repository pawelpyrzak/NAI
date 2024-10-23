package com.example.multimodule.model;

import lombok.Getter;
import lombok.Setter;

import jakarta.persistence.*;

import java.util.HashSet;
import java.util.Set;

@Entity
@Getter
@Setter
@Table(name = "chatplatform")
public class ChatPlatform {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;
}
