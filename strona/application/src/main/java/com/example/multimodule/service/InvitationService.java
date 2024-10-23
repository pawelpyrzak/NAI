package com.example.multimodule.service;

import com.example.multimodule.Exceptions.EntityNotFoundException;
import com.example.multimodule.Exceptions.InvitationExpiredException;
import com.example.multimodule.Exceptions.UserAlreadyExistsException;
import com.example.multimodule.Validator;
import com.example.multimodule.model.Group;
import com.example.multimodule.model.InvitationToken;
import com.example.multimodule.model.User;
import com.example.multimodule.model.UserGroupRole;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class InvitationService {
    private final ICatalogData data;
    private final FindEntity findEntity;
    public InvitationToken VerityToken(String token, String name) {
        if (token.length() < 32) throw new IllegalArgumentException("Nie poprawny token");

        token = Validator.validate(token);
        InvitationToken invitation = data.getInvitationTokenRepository().findByToken(token).orElseThrow(() -> new EntityNotFoundException("not token found"));
        User user = findEntity.findUserByEmail(name);
        if (LocalDate.now().isAfter(invitation.getExpiryDate())) {
            throw new InvitationExpiredException("invitation experied: " + invitation.getExpiryDate().toString());
        }
        if (invitation.getGroup().getUsers().contains(user))
            throw new UserAlreadyExistsException("User już jest w grupie");

        return invitation;
    }

    public void addUser(String token, String name) {
        InvitationToken invitation = data.getInvitationTokenRepository().findByToken(token).orElseThrow(() -> new EntityNotFoundException("not token found"));
        User user = findEntity.findUserByEmail(name);
        Group group=invitation.getGroup();
        user.getGroups().add(group);
        group.getUsers().add(user);
        data.getUserGroupRoleRepository().save(new UserGroupRole(findEntity.getRoleByName("GroupUser"), user, group));
        data.getGroupRepository().save(group);
    }

}
