package com.example.multimodule.contract;

import com.example.multimodule.model.Group;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.sql.Timestamp;

@Getter
@Setter
public class InvitationTokenDTO {


    private Long id;

    @Column(length = 64)
    private String token;

    private Group group;

    private Timestamp expiryDate;
}
