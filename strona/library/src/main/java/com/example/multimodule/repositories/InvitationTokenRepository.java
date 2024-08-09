package com.example.multimodule.repositories;

import com.example.multimodule.model.InvitationToken;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InvitationTokenRepository extends JpaRepository<InvitationToken, Long> {
}
