package com.example.multimodule.service;


import com.example.multimodule.Exceptions.EmailAlreadyTakenException;
import com.example.multimodule.Exceptions.InvalidEmailFormatException;
import com.example.multimodule.Exceptions.PasswordMismatchException;
import com.example.multimodule.Validator;
import com.example.multimodule.contract.UserDTO;
import com.example.multimodule.model.Role;
import com.example.multimodule.model.User;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SignUpService {
    private static final Logger LOGGER = LoggerFactory.getLogger(SignUpService.class);
    private final ICatalogData data;

    public void registerUser(UserDTO userDto) {

        if (!userDto.getEmail().matches("^[\\w-]+(\\.[\\w-]+)*@([\\w-]+\\.)+[a-zA-Z]{2,7}$")) {
            throw new InvalidEmailFormatException("Invalid email format");
        }
        if (data.getUserRepository().existsByEmail(userDto.getEmail())) {
            throw new EmailAlreadyTakenException("E-mail is already taken");
        }
        if (!userDto.getPassword().equals(userDto.getRePassword())) {
            throw new PasswordMismatchException("Passwords do not match");
        }
        User user = new User();
        try {
            user.setFirstName(Validator.validate(userDto.getFirstname()));
            user.setLastName(Validator.validate(userDto.getLastname()));
            user.setPassword(encodePassword(Validator.validate(userDto.getPassword())));
            user.setEmail(Validator.validate(userDto.getEmail()));
        } catch (NullPointerException e) {
            LOGGER.info("Error during Validation {}", e.getMessage());
            throw new NullPointerException(e.getMessage());
        }
        Role userRole = data.getRoleRepository().findByName("User")
                .orElseThrow(() -> new IllegalStateException("Rola 'User' nie istnieje w bazie danych"));
        user.getRoles().add(userRole);
        LOGGER.info("User created");
        data.getUserRepository().save(user);

    }

    private String encodePassword(String password) {
        return new BCryptPasswordEncoder().encode(password);
    }


}
