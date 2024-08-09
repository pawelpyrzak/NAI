package com.example.multimodule.repositories;

import com.example.multimodule.model.Chat;
import com.example.multimodule.model.ChatPlatform;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ChatPlatformRepository extends JpaRepository<ChatPlatform, Long> {
}
