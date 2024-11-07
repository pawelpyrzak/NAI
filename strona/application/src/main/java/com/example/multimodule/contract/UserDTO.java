package com.example.multimodule.contract;

import jakarta.validation.constraints.AssertTrue;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class UserDTO {

    @NotEmpty(message = "First name is required")
    private String firstname;

    @NotEmpty(message = "Last name is required")
    private String lastname;


    @NotEmpty(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    @NotEmpty(message = "Please confirm your password")
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String rePassword;


    @NotEmpty(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;

    @AssertTrue(message = "You must agree to the terms and conditions")
    private boolean termsAgreed;

    @AssertTrue(message = "You must agree to the privacy policy")
    private boolean privacyAgreed;

    public UserDTO(String firstname, String lastname, String password, String rePassword, String email) {
        this.firstname = firstname;
        this.lastname = lastname;
        this.password = password;
        this.rePassword = rePassword;
        this.email = email;
    }
}
