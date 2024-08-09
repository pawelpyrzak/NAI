package com.example.multimodule.repositories;

import com.example.multimodule.model.ChatPlatform;
import com.example.multimodule.model.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRoleRepository extends JpaRepository<UserRole, Long> {
}
