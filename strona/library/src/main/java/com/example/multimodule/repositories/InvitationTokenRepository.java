package com.example.multimodule.repositories;

import com.example.multimodule.model.Group;
import com.example.multimodule.model.InvitationToken;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface InvitationTokenRepository extends JpaRepository<InvitationToken, Long> {
    Optional<InvitationToken> findByToken(String token);
    List<InvitationToken> findByGroup_Id(Long Group_Id);
}
