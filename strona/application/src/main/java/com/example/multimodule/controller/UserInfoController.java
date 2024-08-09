package com.example.multimodule.controller;

import com.example.multimodule.model.User;
import com.example.multimodule.service.UserInfoService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@Controller
@RequiredArgsConstructor
public class UserInfoController {
    private final UserInfoService service;
    @GetMapping("/info/{id}")
    public String showInfo(@PathVariable int id, Model model) {

        try {
           User user= service.getUserInfo(id);
            model.addAttribute("user", user);
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }

        return "userInfo";
    }
}
