package com.example.multimodule.repositories;

import com.example.multimodule.model.GroupAnnouncement;
import org.springframework.data.jpa.repository.JpaRepository;

public interface GroupAnnouncementRepository extends JpaRepository<GroupAnnouncement, Long> {
}
