package com.example.multimodule.service;

import com.example.multimodule.Exceptions.UserNotFoundException;
import com.example.multimodule.model.User;
import com.example.multimodule.repositories.ICatalogData;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserInfoService {
   private final ICatalogData data;

   public User getUserInfo(long id) throws UserNotFoundException {
      var user= data.getUserRepository().findById(id);
      if(user.isEmpty()){
         throw new UserNotFoundException("Brak Usera");
      }
      return user.get();
   }
}
