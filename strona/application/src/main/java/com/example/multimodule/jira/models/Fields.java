package com.example.multimodule.jira.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@JsonIgnoreProperties(ignoreUnknown = true)
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class Fields {
    private String summary;
    private String duedate;
    private Assignee assignee;
    private Description description;
    private Status status;
    private Priority priority;
}
