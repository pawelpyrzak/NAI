package com.example.multimodule.repositories;

import com.example.multimodule.model.Message;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.UUID;

public interface MessageRepository extends JpaRepository<Message, Long> {
    @Query("SELECT m FROM Message m " +
            "JOIN m.chat c " +
            "JOIN c.groups g " +
            "WHERE g.uuid = :uuid")
    List<Message> findAllByGroupToken(@Param("uuid") UUID uuid);

}