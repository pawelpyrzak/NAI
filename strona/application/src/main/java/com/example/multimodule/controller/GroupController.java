package com.example.multimodule.controller;

import com.example.multimodule.contract.ChatDTO;
import com.example.multimodule.contract.GroupAnnouncementDTO;
import com.example.multimodule.contract.InvitationTokenDTO;
import com.example.multimodule.model.Group;
import com.example.multimodule.service.ChatAddService;
import com.example.multimodule.service.GroupService;
import com.example.multimodule.service.MessagesService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@Controller
@RequestMapping("/group")
@RequiredArgsConstructor
public class GroupController {
    private static final Logger LOGGER = LoggerFactory.getLogger(GroupController.class);
    private final GroupService groupService;
    private final MessagesService messagesService;
    private final ChatAddService chatAddService;

    @GetMapping("")
    public String getGroup() {
        return "redirect:/groups";
    }

    @GetMapping("/{uuid}/messages")
    public String getGroupMessages(@PathVariable UUID uuid, Model model) {
        try {
            model.addAttribute("messages", messagesService.findGroupsMessagesByGroupToken(uuid));
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }
        return "groupMessages";
    }

    @GetMapping("/{uuid}")
    public String getGroupPage(@PathVariable UUID uuid) {
        return "groupPage";
    }

    @GetMapping("/{uuid}/admin/announcement")
    public String getGroupAnnouncement(@PathVariable UUID uuid, Model model) {
        GroupAnnouncementDTO groupAnnouncementDTO = new GroupAnnouncementDTO();
        groupAnnouncementDTO.setGroup(groupService.findGroupByToken(uuid));
        model.addAttribute("announcement", groupAnnouncementDTO);
        return "groupAnnouncement";
    }

    @PostMapping("/{uuid}/admin/announcement")
    public String GroupAnnouncement(@PathVariable UUID uuid, Model model, @ModelAttribute GroupAnnouncementDTO announcementDTO, BindingResult bindingResult) {
        if (!bindingResult.hasErrors()) {
            try {
                groupService.createGroupAnnouncement(announcementDTO);
                model.addAttribute("success", "Announcement created");
            } catch (Exception e) {
                model.addAttribute("error", e.getMessage());
            }
        } else {
            model.addAttribute("errors", bindingResult);
        }
        return "groupAnnouncement";
    }

    @GetMapping("/{uuid}/admin/info")
    public String getGroupInfo(@PathVariable UUID uuid, Model model) {
        try {
            Group group = groupService.findGroupByToken(uuid);
            List<InvitationTokenDTO> invitationTokens = groupService.findInvitationByGroup(group);
            model.addAttribute("invitations", invitationTokens);
            model.addAttribute("group", group);

        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }
        model.addAttribute("uuid", uuid);
        return "groupInfo";
    }

    @PostMapping("/{uuid}/admin/info")
    public String getCreateInvitationToken(@PathVariable UUID uuid, Model model, @ModelAttribute InvitationTokenDTO invitationToken) {
        System.out.println(invitationToken.getExpiryDate());
        try {
            Group group = groupService.findGroupByToken(uuid);
            groupService.addInvitationToken(invitationToken, group);
            List<InvitationTokenDTO> invitationTokens = groupService.findInvitationByGroup(group);
            model.addAttribute("invitations", invitationTokens);
            model.addAttribute("group", group);
            model.addAttribute("success", "Stworzono zaproszenie");
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }
        return "groupInfo";
    }

    @GetMapping("/{uuid}/admin/chats")
    public String showChatForm(Model model, @PathVariable UUID uuid) {
        model.addAttribute("communicators", chatAddService.getAllChatPlatform());
        model.addAttribute("uuid", uuid);
        LOGGER.info("chat get");
        return "chatAddForm";
    }

    @PostMapping("/{uuid}/admin/chats")
    public String addChat(@ModelAttribute ChatDTO chatDTO, Model model, @PathVariable UUID uuid) {
        LOGGER.info("chat post");
        Group group = groupService.findGroupByToken(uuid);
        try {
            chatAddService.AddChat(chatDTO, group);
            model.addAttribute("success", "Chat added to group");
        } catch (Exception e) {
            model.addAttribute("error", e.getMessage());
        }
        return "chatAddForm";
    }
}
