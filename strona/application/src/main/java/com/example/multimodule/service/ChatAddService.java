package com.example.multimodule.service;

import com.example.multimodule.Exceptions.EntityNotFoundException;
import com.example.multimodule.contract.ChatDTO;
import com.example.multimodule.contract.ChatPlatformDTO;
import com.example.multimodule.model.Chat;
import com.example.multimodule.model.Group;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ChatAddService {
    private static final Logger LOGGER = LoggerFactory.getLogger(ChatAddService.class);
    private final ICatalogData data;

    public void AddChat(ChatDTO chatDTO, Group group) throws Exception {
        LOGGER.info("chat add");
        Chat chat = data.getChatRepository().findByUuid(chatDTO.getChat_uuid()).orElseThrow(() -> new EntityNotFoundException("Nie znaleziono chatu o podanym tokenie"));
        assert chat.getChatPlatform().getName().equals(chatDTO.getChatPlatformName()) : "Nie znaleziono chatu";

        group.getChats().add(chat);
        data.getGroupRepository().save(group);
        LOGGER.info("chat end");

    }

    public List<ChatPlatformDTO> getAllChatPlatform() {
        return data.getChatPlatformRepository().findAll().stream().map(chatPlatform -> new ChatPlatformDTO(chatPlatform.getId(), chatPlatform.getName())).collect(Collectors.toList());
    }
}
