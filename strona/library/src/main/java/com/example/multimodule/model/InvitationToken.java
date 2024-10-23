package com.example.multimodule.model;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import jakarta.persistence.*;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Getter
@Setter
@NoArgsConstructor
public class InvitationToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 32)
    private String token;

    @ManyToOne
    private Group group;

    private LocalDate expiryDate;

    public InvitationToken(String token, Group group, LocalDate expiryDate) {
        this.token = token;
        this.group = group;
        this.expiryDate = expiryDate;
    }
}
