package com.example.multimodule.controller;

import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class AuthController {

    @GetMapping("/login")
    public String login() {
        return "loginForm";
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
