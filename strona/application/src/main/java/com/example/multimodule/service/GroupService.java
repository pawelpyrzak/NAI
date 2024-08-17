package com.example.multimodule.service;

import com.example.multimodule.Exceptions.InvalidTimeException;
import com.example.multimodule.KeyGenerator;
import com.example.multimodule.Validator;
import com.example.multimodule.contract.GroupAnnouncementDTO;
import com.example.multimodule.contract.GroupDTO;
import com.example.multimodule.model.*;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class GroupService {

    private final ICatalogData data;

    public List<Group> findGroupsByUserId(Long userId) {
        return data.getGroupRepository().findByUserGroups_UserId(userId);
    }

    public User findUserByEmail(String email) throws NoSuchElementException{
        return data.getUserRepository().findByEmail(email).orElseThrow(() -> new NoSuchElementException("User is not present"));
    }
    public Group findGroupByToken(String token) throws NoSuchElementException{
        return data.getGroupRepository().findByToken(token).orElseThrow(() -> new NoSuchElementException("Group is not present"));
    }
    public List<Group> findGroupsByUserByEmail(String email) {
        return data.getGroupRepository().findByUserGroupsBYUserEmail(email);
    }

    public void findGroupsMessagesByGroupToken(String token) {
    }

    public void CreateGroup(GroupDTO groupDTO) throws NoSuchElementException{
        String validatedName = Validator.validate(groupDTO.getName());
        Group group = new Group(validatedName, KeyGenerator.generateRandomKey(64));
        User user = data.getUserRepository().findByEmail(groupDTO.getUserEmail()).orElseThrow(() -> new NoSuchElementException("User is not present"));
        Role role = data.getRoleRepository().findByName("GroupAdmin").orElseThrow(() -> new NoSuchElementException("Role not found"));

        UserGroupRole userGroupRole = new UserGroupRole(role,user, group);
        data.getGroupRepository().save(group);
        data.getUserGroupRoleRepository().save(userGroupRole);


    }

    public Boolean isAdmin(User users, long groupId) {
        Optional<UserGroupRole> userGroup = data.getUserGroupRoleRepository()
                .findByUserIdAndGroupId(users.getId(), groupId);
        return userGroup.isPresent() && userGroup.get().getRole().getName().equals("GroupAdmin");
    }
    public void createGroupAnnouncement(GroupAnnouncementDTO announcementDTO, User user) throws InvalidTimeException {
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
}
