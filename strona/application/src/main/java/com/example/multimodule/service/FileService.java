package com.example.multimodule.service;

import com.example.multimodule.model.File;
import com.example.multimodule.repositories.ICatalogData;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@RequiredArgsConstructor
@Service
public class FileService {
    private final ICatalogData data;
    private final GroupService groupService;

    @Transactional
    public List<String> getAllFiles(UUID uuid) {
        List<File> files = data.getFileRepository().findFileByGroupUuid(uuid);

        final List<String> list = files.stream()
                .map(file -> "<a href='/group/" + uuid + "/files/download/" + file.getId() + "'>" + file.getName() + "</a>")
                .toList();
        System.out.println(list.size());
        return list;
    }

    @Transactional
    public File getFile(Long id, UUID uuid) {
        File file = null;
        for (File f : data.getFileRepository().findFileByGroupUuid(uuid)) {
            if (f.getId().equals(id)) {
                file = f;
                break;
            }
        }
        return file;
    }

    public void verity(String name, UUID uuid) {
        var groups = groupService.findGroupsByUserByEmail(name);
        if (groups.stream().noneMatch(g -> g.getUuid().equals(uuid))) {
            throw new RuntimeException("NO access");
        }
    }
}
