package com.example.multimodule.security;

import com.example.multimodule.model.Group;
import com.example.multimodule.model.User;
import com.example.multimodule.service.FindEntity;
import com.example.multimodule.service.GroupService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.security.Principal;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class AdminInterceptor implements HandlerInterceptor {
    private final GroupService groupService;
    private final FindEntity findEntity;
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        Principal principal = request.getUserPrincipal();
        UUID uuid = UUID.fromString(request.getRequestURI().split("/")[2]);
        try {
            Group group = groupService.findGroupByToken(uuid);
            User user = findEntity.findUserByEmail(principal.getName());
            if (!groupService.isAdmin(user, group)) {
                response.sendRedirect("/group/" + uuid);
                return false;
            }
        }catch (Exception e){
            response.sendRedirect("/group/" + uuid);
            return false;
        }
        return true;
    }
}
