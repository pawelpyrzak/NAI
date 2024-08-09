package com.example.multimodule.controller;

import com.example.multimodule.contract.GroupAnnouncementDTO;
import com.example.multimodule.contract.GroupDTO;
import com.example.multimodule.contract.InvitationTokenDTO;
import com.example.multimodule.model.Group;
import com.example.multimodule.model.GroupAnnouncement;
import com.example.multimodule.model.InvitationToken;
import com.example.multimodule.model.User;
import com.example.multimodule.service.GroupService;
import com.example.multimodule.service.MessagesService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.security.Principal;
import java.util.List;

@Controller
@RequestMapping("/groups")
@RequiredArgsConstructor
public class GroupController {
    private final GroupService groupService;
    private final MessagesService messagesService;

    @GetMapping
    public String getUserGroups(Model model, Principal principal) {
        List<Group> groups = groupService.findGroupsByUserByEmail(principal.getName());
        model.addAttribute("groups", groups);
        return "groups";
    }

    @GetMapping("/{token}")
    public String getGroupMessages(@PathVariable String token, Model model) {
        try {
            model.addAttribute("messages", messagesService.findGroupsMessagesByGroupToken(token));
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }

        return "groupMessages";
    }

    @GetMapping("/create")
    public String getFormOfCreateGroup() {
        return "groupCreate";
    }

    @GetMapping("/{token}/announcement")
    public String getGroupAnnouncement(@PathVariable String token, Model model, @AuthenticationPrincipal UserDetails userDetails) {
        try {
            Group group = groupService.findGroupByToken(token);
            User user = groupService.findUserByEmail(userDetails.getUsername());
            boolean isAdmin = groupService.isAdmin(user, group.getId());
            if (!isAdmin) {
                return "redirect:/groups/" + token;
            }
            GroupAnnouncementDTO groupAnnouncementDTO = new GroupAnnouncementDTO();
            groupAnnouncementDTO.setGroup(group);
            model.addAttribute("announcement", groupAnnouncementDTO);
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }

        return "groupAnnouncement";
    }


    @PostMapping("/{token}/announcement")
    public String GroupAnnouncement(@PathVariable String token, Model model, @AuthenticationPrincipal UserDetails userDetails, GroupAnnouncementDTO announcementDTO, BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            model.addAttribute("errors", bindingResult);
            return "signUpForm";
        }
        try {
            Group group = announcementDTO.getGroup();
            User user = groupService.findUserByEmail(userDetails.getUsername());

            boolean isAdmin = groupService.isAdmin(user, group.getId());
            if (!isAdmin) {
                model.addAttribute("error", "No permissions");
                return "groupMessages";
            }
            groupService.createGroupAnnouncement(announcementDTO, user);
            model.addAttribute("success", "Group successful create");
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }

        return "groupAnnouncement";
    }

    @GetMapping("/{token}/info")
    public String getGroupInfo(@PathVariable String token, Model model, @AuthenticationPrincipal UserDetails userDetails) {
        try {
            Group group = groupService.findGroupByToken(token);
            User user = groupService.findUserByEmail(userDetails.getUsername());
            boolean isAdmin = groupService.isAdmin(user, group.getId());
            if (!isAdmin) {
                return "redirect:/groups/" + token;
            }
            InvitationTokenDTO invitationToken =new InvitationTokenDTO();
            invitationToken.setGroup(group);
            model.addAttribute("invitationToken", invitationToken);
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }

        return "groupInfo";
    }
    @PostMapping("/create")
    public String createGroup(GroupDTO groupDTO, @AuthenticationPrincipal UserDetails userDetails, Model model) {
        try {
            groupDTO.setUserEmail(userDetails.getUsername());
            groupService.CreateGroup(groupDTO);
            model.addAttribute("success", "Group created");

        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }
        return "groupCreate";
    }
}
