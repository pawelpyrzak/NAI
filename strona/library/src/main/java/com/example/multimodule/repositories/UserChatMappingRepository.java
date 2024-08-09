package com.example.multimodule.repositories;

import com.example.multimodule.model.UserChatMapping;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserChatMappingRepository extends JpaRepository<UserChatMapping, Long> {
}