package com.example.multimodule.service;


import com.example.multimodule.Exceptions.EmailAlreadyTakenException;
import com.example.multimodule.Exceptions.InvalidEmailFormatException;
import com.example.multimodule.Exceptions.PasswordMismatchException;
import com.example.multimodule.KeyGenerator;
import com.example.multimodule.Validator;
import com.example.multimodule.contract.UserDTO;
import com.example.multimodule.model.Role;
import com.example.multimodule.model.User;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class SignUpService {
    private final ICatalogData data;

    public void registerUser(UserDTO userDto) {
        if (!userDto.getEmail().matches("^[\\w-]+(\\.[\\w-]+)*@([\\w-]+\\.)+[a-zA-Z]{2,7}$")) {
            throw new InvalidEmailFormatException("Invalid email format");
        }
        if (!userDto.getPassword().equals(userDto.getRePassword())) {
            throw new PasswordMismatchException("Passwords do not match");
        }
        if (data.getUserRepository().existsByEmail(userDto.getEmail())) {
            throw new EmailAlreadyTakenException("E-mail is already taken");
        }

        try {
            userDto = new UserDTO(
                    Validator.validate(userDto.getFirstname()),
                    Validator.validate(userDto.getLastname()),
                    Validator.validate(userDto.getPassword()),
                    Validator.validate(userDto.getRePassword()),
                    Validator.validate(userDto.getEmail())
            );

            Set<Role> roles = new HashSet<>();
            roles.add(data.getRoleRepository().findByName("User")
                    .orElseThrow(() -> new NoSuchElementException("Nie znaleziono roli")));
            User user = new User(
                    userDto.getFirstname(),
                    userDto.getLastname(),
                    KeyGenerator.generateRandomKey(10),
                    encodePassword(userDto.getPassword()),
                    userDto.getEmail(),
                    roles
            );

            data.getUserRepository().save(user);
        } catch (Exception e) {
            throw new RuntimeException("Error during user registration", e);
        }
    }

    private String encodePassword(String password) {
        return new BCryptPasswordEncoder().encode(password);
    }


}
