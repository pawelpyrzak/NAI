package com.example.multimodule.repositories;

import com.example.multimodule.model.Group;
import com.example.multimodule.model.Role;
import com.example.multimodule.model.User;
import com.example.multimodule.model.UserGroupRole;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserGroupRoleRepository extends JpaRepository<UserGroupRole, Long> {

    Optional<UserGroupRole> findByUserIdAndGroupId(Long Uid, Long Gid);

    Optional<UserGroupRole> findByGroupAndUserAndRole(Group group, User user, Role role);
}
