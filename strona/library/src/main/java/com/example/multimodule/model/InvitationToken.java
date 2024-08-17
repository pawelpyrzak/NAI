package com.example.multimodule.model;

import lombok.Getter;
import lombok.Setter;

import jakarta.persistence.*;
import java.sql.Timestamp;

@Entity
@Getter
@Setter
public class InvitationToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 64)
    private String token;

    @ManyToOne
    private Group group;

    private Timestamp expiryDate;
}
