package com.example.multimodule.calendar;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
@Getter
@Setter
@AllArgsConstructor
public class Task {
    private String name;
    private LocalDate date;
    private String user;
    private String description;
    private String status;
    private String priority;
}