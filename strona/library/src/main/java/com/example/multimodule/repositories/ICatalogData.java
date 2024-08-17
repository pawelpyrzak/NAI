package com.example.multimodule.repositories;

public interface ICatalogData {
    MessageRepository getMessageRepository();

    RoleRepository getRoleRepository();

    UserRepository getUserRepository();

    ChatRepository getChatRepository();

    UserGroupRoleRepository getUserGroupRoleRepository();

    GroupRepository getGroupRepository();

    ChatPlatformRepository getChatPlatformRepository();

    GroupAnnouncementRepository getGroupAnnouncementRepository();

    InvitationTokenRepository getInvitationTokenRepository();


}
