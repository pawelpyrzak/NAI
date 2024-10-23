package com.example.multimodule.repositories;

import com.example.multimodule.model.Group;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface GroupRepository extends JpaRepository<Group, Long> {
    @Query("SELECT g FROM Group g JOIN g.users u WHERE u.id = :userId")
    List<Group> findByUserGroups_UserId(@Param("userId") Long userId);

    Optional<Group> findByUuid(UUID uuid);

    @Query("SELECT g FROM Group g JOIN g.users u WHERE u.email = :userEmail")
    List<Group> findByUserGroupsBYUserEmail(@Param("userEmail") String userEmail);
}