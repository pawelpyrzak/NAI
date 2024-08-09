package com.example.multimodule.service;

import com.example.multimodule.Exceptions.MessagesNotFoundException;
import com.example.multimodule.contract.MessagesDTO;
import com.example.multimodule.model.Message;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MessagesService {
    private final ICatalogData data;

    public List<MessagesDTO> findGroupsMessagesByGroupToken(String token) throws MessagesNotFoundException {
        List<Message> list = data.getMessageRepository().findAllByGroupToken(token);
        if (list.isEmpty()) {
            throw new MessagesNotFoundException("Brak wiadomości");
        }
        return list.stream().
                map(message -> new MessagesDTO(message.getContent(),
                        message.getUserChatMapping().getChatUser().getUsername(),
                        message.getTimestamp(),
                        message.getUserChatMapping().getChat().getName(),
                        message.getUserChatMapping().getChat().getChatPlatform().getName()
                )).toList();
    }
}