package com.example.multimodule.controller;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
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
    public String logout(HttpServletResponse response) {
        Cookie cookie = new Cookie("JSESSIONID", null); // Name of the cookie
        cookie.setMaxAge(0); // Setting max age to 0 deletes the cookie
        cookie.setPath("/");  // Ensure path matches the original cookie path
        response.addCookie(cookie);
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
            System.out.println(authentication.getPrincipal().toString());
        }
        return "home";
    }

    @GetMapping()
    public String showIndex() {
        return "index";
    }

}
