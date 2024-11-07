package com.example.multimodule.jira;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;

import java.util.Objects;


@Getter
@Setter
@RequiredArgsConstructor
public final class JiraData {
    private final String baseUrl;
    private final String user;
    private final String apiToken;
}
