package com.example.multimodule.jira;

import com.example.multimodule.jira.models.Issue;
import com.example.multimodule.jira.models.IssueResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;

@Service
public class JiraService {
    private final ObjectMapper objectMapper;

    private final RestTemplate restTemplate;
    private final JiraData jiraData;
    private static final HttpClient client = HttpClient.newHttpClient();

    public JiraService(
            @Value("${jira.api.url}") String baseUrl,
            @Value("${jira.user}") String user,
            @Value("${jira.api.token}") String apiToken) {
        this.objectMapper = new ObjectMapper();
        this.restTemplate = new RestTemplate();
        this.jiraData = new JiraData(baseUrl,user,apiToken);
    }

    public String sendData(String summary, String description, String projectKey, String duedate) {
        String auth = jiraData.getUser() + ":" + jiraData.getApiToken();
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));

        String jsonPayload = """
                {
                  "fields": {
                    "project": {
                      "key": "%s"
                    },
                    "summary": "%s",
                    "description": {
                      "type": "doc",
                      "version": 1,
                      "content": [
                        {
                          "type": "paragraph",
                          "content": [
                            {
                              "type": "text",
                              "text": "%s"
                            }
                          ]
                        }
                      ]
                    },
                    "issuetype": {
                      "name": "Task"
                    },
                    "duedate": "%s"
                  }
                }
                """;
        jsonPayload = String.format(jsonPayload, projectKey, summary, description, duedate);
        System.out.println(jsonPayload);
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(jiraData.getBaseUrl() + "/issue"))
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Basic " + encodedAuth)
                    .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 201) {
                System.out.println("Task created successfully!");
                return "Task created successfully!";
            } else {
                System.out.println("Failed to create task: " + response.statusCode());
                System.out.println(response.body());
                return "Failed to create task: " + response.statusCode() + " " + response.body();
            }

        } catch (Exception e) {
            System.out.println(e.getMessage());
            return e.getMessage();
        }
    }

    // Helper method to parse the response body to an Issue
    private Issue parseIssueFromResponse(String responseBody) throws JsonProcessingException {
        return objectMapper.readValue(responseBody, Issue.class);
    }

    public List<Issue> getData() {
        // Set headers and authorization
        HttpHeaders headers = createHeaders(jiraData.getUser(), jiraData.getApiToken());

        // Prepare the query
        String jqlQuery = "project=KAN";
        String url = jiraData.getBaseUrl() + "/search";

        // Create the entity with headers
        HttpEntity<String> entity = new HttpEntity<>(headers);

        // Make the GET request and parse the response
        try {
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);
            List<Issue> issues = parseIssuesFromResponse(response.getBody());
            System.out.println(issues.size());
            return issues;
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to process JSON response", e);
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve data from Jira", e);
        }
    }

    // Helper method to create headers with authentication
    private HttpHeaders createHeaders(String user, String apiToken) {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Accept", "application/json");
        headers.set("Content-Type", "application/json");

        String auth = user + ":" + apiToken;
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));
        headers.set("Authorization", "Basic " + encodedAuth);

        return headers;
    }

    // Helper method to parse the response body to a list of issues
    private List<Issue> parseIssuesFromResponse(String responseBody) throws JsonProcessingException {
        IssueResponse issueResponse = objectMapper.readValue(responseBody, IssueResponse.class);
        return issueResponse.getIssues();
    }
}