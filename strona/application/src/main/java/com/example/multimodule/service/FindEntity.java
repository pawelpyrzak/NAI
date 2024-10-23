package com.example.multimodule.service;

import com.example.multimodule.Exceptions.EntityNotFoundException;
import com.example.multimodule.model.Role;
import com.example.multimodule.model.User;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;
@Service
@RequiredArgsConstructor
public class FindEntity {
    private final ICatalogData data;
    public Role getRoleByName(String name) throws NoSuchElementException {
        return data.getRoleRepository().findByName(name).orElseThrow(() -> new NoSuchElementException("Role not found"));
    }
    public User findUserByEmail(String email) throws EntityNotFoundException {
        return data.getUserRepository().findByEmail(email).orElseThrow(() -> new EntityNotFoundException("User is not present"));
    }
}
