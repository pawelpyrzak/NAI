package com.example.multimodule.model;

import lombok.Getter;
import lombok.Setter;

import jakarta.persistence.*;
import java.sql.Timestamp;

@Entity
@Table(name = "InvitationToken")
@Getter
@Setter
public class InvitationToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 64)
    private String token;

    @ManyToOne
    @JoinColumn(name = "UserGroupMapping_id")
    private UserGroupMapping userGroupMapping;

    private Timestamp expiryDate;
}
