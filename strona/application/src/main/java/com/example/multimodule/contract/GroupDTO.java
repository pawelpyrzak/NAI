package com.example.multimodule.contract;

import com.example.multimodule.model.User;
import jakarta.validation.constraints.NotEmpty;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
public class GroupDTO {
    private Long id;

    private String userEmail;

    private String name;

    private User user;

    private UUID uuid;

    public GroupDTO(Long id, String name, UUID uuid) {
        this.id = id;
        this.name = name;
        this.uuid = uuid;
    }
}
