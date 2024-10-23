package com.example.multimodule.controller;

import com.example.multimodule.model.InvitationToken;
import com.example.multimodule.service.InvitationService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;

@Controller
@RequestMapping("/invite")
@RequiredArgsConstructor
public class InvitationController {
    private final InvitationService invitationService;

    @GetMapping("/{token}")
    public String verifyInvitation(Model model, Principal principal, @PathVariable String token) {

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return "NoLogin";
        }
        InvitationToken verToken = invitationService.VerityToken(token, principal.getName());
        model.addAttribute("groupName", verToken.getGroup().getName());
        return "invitation";
    }

    @PostMapping("/{token}")
    public String adduserToGroup(@PathVariable String token, Principal principal) {
        invitationService.addUser(token,principal.getName());
        return "redirect:/groups";
    }

}
