package com.example.multimodule.service;

import com.example.multimodule.Exceptions.InvalidTimeException;
import com.example.multimodule.KeyGenerator;
import com.example.multimodule.Validator;
import com.example.multimodule.contract.GroupAnnouncementDTO;
import com.example.multimodule.contract.GroupDTO;
import com.example.multimodule.contract.InvitationTokenDTO;
import com.example.multimodule.model.*;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class GroupService {

    private final ICatalogData data;
    private final FindEntity findEntity;

    public Group findGroupByToken(UUID uuid) throws NoSuchElementException {
        return data.getGroupRepository().findByUuid(uuid).orElseThrow(() -> new NoSuchElementException("Group is not present"));
    }

    public List<Group> findGroupsByUserByEmail(String email) {
        return data.getGroupRepository().findByUserGroupsBYUserEmail(email);
    }
    public void CreateGroup(GroupDTO groupDTO) throws NoSuchElementException {
        String validatedName = Validator.validate(groupDTO.getName());
        Group group = new Group(validatedName, UUID.randomUUID());
        User user = data.getUserRepository().findByEmail(groupDTO.getUserEmail()).orElseThrow(() -> new NoSuchElementException("User is not present"));
        user.getGroups().add(group);
        group.getUsers().add(user);
        data.getGroupRepository().save(group);

        data.getUserGroupRoleRepository().save(new UserGroupRole(findEntity.getRoleByName("GroupAdmin"), user, group));
        data.getUserGroupRoleRepository().save(new UserGroupRole(findEntity.getRoleByName("GroupUser"), user, group));


    }
    public Boolean isAdmin(User user, Group group) {
        return data.getUserGroupRoleRepository().findByGroupAndUserAndRole(group, user, findEntity.getRoleByName("GroupAdmin")).isPresent();
    }

    public void createGroupAnnouncement(GroupAnnouncementDTO announcementDTO) throws InvalidTimeException {
        String validated = Validator.validate(announcementDTO.getContent());
        GroupAnnouncement groupAnnouncement = new GroupAnnouncement();
        data.getGroupAnnouncementRepository();
        LocalDateTime teraz = LocalDateTime.now();
        if (Duration.between(announcementDTO.getEndTime(), announcementDTO.getStartTime()).toHours() < 1) {
            throw new InvalidTimeException("Start time musi być przynajmniej o 1 godzinę późniejszy niż end time.");
        }

        // Sprawdź, czy startTime nie jest wcześniejszy niż aktualny czas minus 1 godzina
        if (announcementDTO.getStartTime().isBefore(teraz.minusHours(1))) {
            throw new InvalidTimeException("Start time nie może być wcześniejszy niż 1 godzina przed aktualnym czasem.");
        }

    }

    public void addInvitationToken(InvitationTokenDTO invitationToken, Group group) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        LocalDate date = LocalDate.parse(invitationToken.getExpiryDate(), formatter);
        String token = KeyGenerator.generateRandomKey(32);
        InvitationToken invitationToken1 = new InvitationToken(token, group, date);
        data.getInvitationTokenRepository().save(invitationToken1);
    }

    public List<InvitationTokenDTO> findInvitationByGroup(Group group) {
        List<InvitationToken> invitationTokens = data.getInvitationTokenRepository().findByGroup_Id(group.getId());
        return invitationTokens.stream().map(invitationToken -> new InvitationTokenDTO(invitationToken.getToken(), group, invitationToken.getExpiryDate())).toList();
    }
}
