package com.example.multimodule.contract;

import com.example.multimodule.model.User;
import jakarta.persistence.Lob;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class FileDTO {

    private String name;

    @Lob
    private byte[] data;

}
