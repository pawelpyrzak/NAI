package com.example.multimodule.calendar;

import com.example.multimodule.jira.models.*;
import com.example.multimodule.jira.JiraService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TaskService {
    private final JiraService jiraService;

    public List<Task> getTasks() {
        List<Issue> issues = jiraService.getData();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        List<Task> list = new ArrayList<>();
        for (Issue issue : issues) {
            LocalDate data = null;
            String date = issue.getFields().getDuedate();
            Assignee assignee = issue.getFields().getAssignee();
            if (date != null) {
                data = LocalDate.parse(date, formatter);
            }
            Fields fields =issue.getFields();
            Task task = new Task(fields.getSummary(),
                    data, "", getFullDescription(issue),
                    fields.getStatus().getName(),
                    fields.getPriority().getName()
            );
            if (assignee != null) {
                task.setUser(assignee.getDisplayName());
            }
            list.add(task);
        }
        return list;
    }
    public Map<LocalDate, List<Task>> getTasksForMonth(YearMonth month, Long userId) {
        List<Task> tasks = getTasks().stream().filter(task ->task.getDate()!=null&&YearMonth.from(task.getDate()).equals(month)).toList();

        return tasks.stream().collect(Collectors.groupingBy(Task::getDate));
    }

    private String getFullDescription(Issue issue) {
        StringBuilder descriptionBuilder = new StringBuilder();
        Description description = issue.getFields().getDescription();

        if (description != null) {
            for (ContentItem item : description.getContent()) {
                if ("paragraph".equals(item.getType())) {
                    for (TextItem textItem : item.getContent()) {
                        if ("text".equals(textItem.getType())) {
                            descriptionBuilder.append(textItem.getText()).append("\n");
                        }
                    }
                }
            }
        }
        return descriptionBuilder.toString();
    }
}
