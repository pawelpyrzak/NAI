package com.example.multimodule.repositories;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
@Getter
public class BotsDataCatalog implements ICatalogData {

    private final MessageRepository messageRepository;

    private final ChatRepository chatRepository;

    private final UserRepository userRepository;

    private final RoleRepository roleRepository;

    private final UserGroupRoleRepository userGroupRoleRepository;

    private final GroupRepository groupRepository;

    private final ChatPlatformRepository chatPlatformRepository;

    private final GroupAnnouncementRepository groupAnnouncementRepository;

    private final InvitationTokenRepository invitationTokenRepository;
    private final FileRepository fileRepository;

}
