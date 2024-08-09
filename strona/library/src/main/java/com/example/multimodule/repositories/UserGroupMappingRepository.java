package com.example.multimodule.repositories;

import com.example.multimodule.model.UserGroupMapping;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserGroupMappingRepository extends JpaRepository<UserGroupMapping, Long> {

    Optional<UserGroupMapping> findByUserIdAndGroupId(Long Uid, Long Gid);
}
