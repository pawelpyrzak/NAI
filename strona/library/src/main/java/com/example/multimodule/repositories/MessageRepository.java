package com.example.multimodule.repositories;

import com.example.multimodule.model.Message;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface MessageRepository extends JpaRepository<Message, Long> {
    @Query("SELECT m FROM Message m WHERE m.chat.group.token = :token")
    List<Message> findAllByGroupToken(@Param("token") String token);

}