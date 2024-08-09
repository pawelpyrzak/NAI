package com.example.multimodule.repositories;

import com.example.multimodule.model.ChatUser;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ChatUserRepository extends JpaRepository<ChatUser, Long> {

}