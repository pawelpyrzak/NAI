package com.example.multimodule.contract;

import com.example.multimodule.model.Group;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
public class InvitationTokenDTO {

    private Long id;

    private String token;

    private Group group;
    private String expiryDate;
    private LocalDate expiryDateTime;

    public InvitationTokenDTO(String token, Group group, LocalDate expiryDateTime) {
        this.token = token;
        this.group = group;
        this.expiryDateTime = expiryDateTime;
    }

}
