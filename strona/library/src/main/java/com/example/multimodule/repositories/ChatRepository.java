package com.example.multimodule.repositories;

import com.example.multimodule.model.Chat;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;
import java.util.UUID;

public interface ChatRepository extends JpaRepository<Chat, Long> {
    Optional<Chat> findByUuid(UUID uuid);


}
