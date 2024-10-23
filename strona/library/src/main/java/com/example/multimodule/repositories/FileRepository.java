package com.example.multimodule.repositories;

import com.example.multimodule.model.File;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.UUID;

public interface FileRepository extends JpaRepository<File, Long> {
    @Query("SELECT f FROM File f " +
            "JOIN f.chat c " +
            "JOIN c.groups g " +
            "WHERE g.uuid = :uuid")
    List<File> findFileByGroupUuid(UUID uuid);
}
