package com.example.multimodule.controller;

import com.example.multimodule.model.File;
import com.example.multimodule.service.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;

import java.security.Principal;
import java.util.UUID;

@RequiredArgsConstructor
@Controller
@RequestMapping("/group/{uuid}/files")
public class FileController {

    private final FileService fileService;


    // Endpoint do pobierania listy wszystkich plików i wyświetlania ich na stronie HTML
    @GetMapping("")
    public String listAllFiles(Model model, @PathVariable UUID uuid) {
        model.addAttribute("files", fileService.getAllFiles(uuid));
        return "file-list";
    }

    // Endpoint do pobierania pliku po jego ID
    @GetMapping("/download/{id}")
    public ResponseEntity<byte[]> downloadFile(@PathVariable Long id, @PathVariable UUID uuid, Principal principal) {
        File fileEntity = fileService.getFile(id,uuid);
        try {
            fileService.verity(principal.getName(),uuid);
        }catch (Exception e){
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }

        if (fileEntity!=null) {
            return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + fileEntity.getName() + "\"").body(fileEntity.getData());
        }

        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
}
