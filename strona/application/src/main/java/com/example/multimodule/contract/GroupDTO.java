package com.example.multimodule.contract;

import com.example.multimodule.model.User;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class GroupDTO {
    private Long id;

    private String userEmail;

    private String name;

    private User user;

    private String token;

    public GroupDTO(Long id, String name, String token) {
        this.id = id;
        this.name = name;
        this.token = token;
    }
}
