package com.example.multimodule.security;

import com.example.multimodule.model.Group;
import com.example.multimodule.service.GroupService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.UUID;

@RequiredArgsConstructor
@Component
public class TokenInterceptor implements HandlerInterceptor {
    private final GroupService groupService;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        UUID uuid = UUID.fromString(request.getRequestURI().split("/")[2]);

        try {
            Group group = groupService.findGroupByToken(uuid);  // Sprawdzenie, czy token jest prawidłowy

            // Pobieranie zalogowanego użytkownika ze Spring Security
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                response.sendRedirect("/login");
                return false;
            }
            var groups = groupService.findGroupsByUserByEmail(authentication.getName());
            if (groups.stream().noneMatch(g -> g.getUuid().equals(group.getUuid()))) {
                response.sendRedirect("/group");  // Przekierowanie, jeśli brak dostępu
                return false;
            }
        } catch (Exception e) {
            response.sendRedirect("/group");
            return false;
        }

        return true;
    }
}

