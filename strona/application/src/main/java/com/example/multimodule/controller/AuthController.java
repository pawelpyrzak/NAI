package com.example.multimodule.controller;

import com.example.multimodule.contract.UserDTO;
import com.example.multimodule.service.SignUpService;
import com.example.multimodule.service.UserService;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
@RequiredArgsConstructor
public class AuthController {

    private final SignUpService userService;
    private static final Logger LOGGER = LoggerFactory.getLogger(AuthController.class);

    @GetMapping("/login")
    public String login() {
        return "loginForm";
    }

    @GetMapping("/signup")
    public String showSignUpForm(Model model) {
        model.addAttribute("userDTO", new UserDTO());
        return "signUpForm";
    }

    @PostMapping("/signup")
    public String registerUser(@Valid UserDTO userDTO, BindingResult result, Model model) {
        if (result.hasErrors()) {
            model.addAttribute("errors", result);
            LOGGER.error("error {}", result);
            return "signUpForm";
        }
        try {
            userService.registerUser(userDTO);
            model.addAttribute("success", "Your account has been created successfully");
            LOGGER.info("Account created successfully for {}", userDTO.getEmail());
        } catch (RuntimeException e) {
            model.addAttribute("error", e.getMessage());
            LOGGER.error("Error during registration: {}", e.getMessage());
        }
        return "signUpForm";
    }
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        return "redirect:/login";
    }

    @GetMapping("/nologin")
    public String NoLogin() {
        return "NoLogin";
    }

    @GetMapping("/home")
    public String home(Model model) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated() && !(authentication.getPrincipal() instanceof String)) {
            model.addAttribute("username", authentication.getName());
        }
        return "home";
    }
    @GetMapping()
    public String showIndex() {
        return "index";
    }

}
