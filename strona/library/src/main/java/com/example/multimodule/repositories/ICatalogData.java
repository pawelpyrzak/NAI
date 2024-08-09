package com.example.multimodule.repositories;

public interface ICatalogData {
    MessageRepository getMessageRepository();

    RoleRepository getRoleRepository();

    UserRepository getUserRepository();

    ChatRepository getChatRepository();

    UserGroupMappingRepository getUserGroupMappingRepository();

    UserChatMappingRepository getUserChatMappingRepository();

    GroupRepository getGroupRepository();

    ChatPlatformRepository getChatPlatformRepository();

    GroupAnnouncementRepository getGroupAnnouncementRepository();

    InvitationTokenRepository getInvitationTokenRepository();

    UserRoleRepository getUserRoleRepository();

    ChatUserRepository getChatUserRepository();


}
