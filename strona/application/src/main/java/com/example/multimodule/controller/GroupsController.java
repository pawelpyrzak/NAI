package com.example.multimodule.controller;

import com.example.multimodule.Validator;
import com.example.multimodule.contract.GroupDTO;
import com.example.multimodule.model.Group;
import com.example.multimodule.service.GroupService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.security.Principal;
import java.util.List;

@Controller
@RequestMapping("/groups")
@RequiredArgsConstructor
class GroupsController {
    private final GroupService groupService;
    private static final Logger LOGGER = LoggerFactory.getLogger(GroupsController.class);


    @GetMapping
    public String getUserGroups(Model model, Principal principal) {
        List<Group> groups = groupService.findGroupsByUserByEmail(principal.getName());
        model.addAttribute("groups", groups);
        return "groups";
    }

    @GetMapping("/create")
    public String getFormOfCreateGroup() {
        return "groupCreate";
    }

    @PostMapping("/create")
    public String createGroup(GroupDTO groupDTO, @AuthenticationPrincipal UserDetails userDetails, Model model, BindingResult result) {
        if (!result.hasErrors()) {
            try {
                groupDTO.setUserEmail(userDetails.getUsername());
                groupService.CreateGroup(groupDTO);
                model.addAttribute("success", "Group created");
            } catch (Exception e) {
                model.addAttribute("error", e.getMessage());
            }
        } else {
            model.addAttribute("errors", result);
        }
        return "groupCreate";
    }
}
