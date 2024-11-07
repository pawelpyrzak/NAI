package com.example.multimodule.calendar;

import com.example.multimodule.calendar.CalendarService;
import com.example.multimodule.calendar.Task;
import com.example.multimodule.calendar.TaskService;
import com.example.multimodule.jira.JiraService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.security.Principal;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.temporal.TemporalAdjusters;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RequiredArgsConstructor
@Controller
public class CalendarController {
    private final CalendarService calendarService;
    private final TaskService taskService;
    private final JiraService jiraService;

    @GetMapping("/calendar")
    public String getCalendar(
            @RequestParam(value = "year", defaultValue = "-1") int year,
            @RequestParam(value = "month", defaultValue = "-1") int month,
            Model model) {

        LocalDate now = LocalDate.now();
        if (year == -1) year = now.getYear();
        if (month == -1) month = now.getMonthValue();
        LocalDate firstDayOfMonth = LocalDate.of(year, month, 1);
        model.addAttribute("year", year);
        model.addAttribute("month", month);

        var weeks = calendarService.getWeeks(firstDayOfMonth);
        Map<LocalDate, List<Task>> tasksByDate = taskService.getTasksForMonth(YearMonth.from(firstDayOfMonth), 1L);
        System.out.println(tasksByDate.keySet());
        model.addAttribute("tasksByDate", tasksByDate);
        model.addAttribute("weeks", weeks);
        return "calendar";
    }


    @GetMapping("/calendar/week")
    public String getWeek(
            @RequestParam(value = "date", required = false) String date,
            Model model) {

        LocalDate currentDate = date != null && !date.isEmpty() ? LocalDate.parse(date) : LocalDate.now();

        LocalDate startOfWeek = currentDate.with(TemporalAdjusters.previousOrSame(java.time.DayOfWeek.MONDAY));
        List<LocalDate> daysOfWeek = new ArrayList<>();

        for (int i = 0; i < 7; i++) {
            daysOfWeek.add(startOfWeek.plusDays(i));
        }
        Map<LocalDate, List<Task>> tasksByDate = taskService.getTasksForMonth(YearMonth.from(currentDate), 1L);
        model.addAttribute("tasksByDate", tasksByDate);
        model.addAttribute("days", daysOfWeek);
        model.addAttribute("currentDate", currentDate);
        System.out.println(tasksByDate.keySet());

        return "week";
    }

    @GetMapping("/create-task")
    public String showCreateTaskForm(Model model) {
        model.addAttribute("projectKey", "PROJ");
        return "TaskCreator";
    }

    @GetMapping("/tasks")
    public String showTasks(Model model) {
        model.addAttribute("tasks", taskService.getTasks());
        return "Tasks";
    }

    @PostMapping("/create-task")
    public String createTask(@RequestParam String summary,
                             @RequestParam String description,
                             @RequestParam String projectKey, @RequestParam(required = false) String duedate,
                             Model model) {
        System.out.println("Creating task: " + summary + ", " + description + ", " + projectKey);
        String message = jiraService.sendData(summary, description, projectKey, duedate);

        model.addAttribute("message", message);
        return "TaskCreator";
    }
}
