package com.example.multimodule.calendar;

import org.springframework.stereotype.Service;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
@Service
public class CalendarService {

    public List<List<LocalDate>> getWeeks(LocalDate firstDayOfMonth) {
        int daysInMonth = firstDayOfMonth.lengthOfMonth();
        List<LocalDate> daysOfMonth = new ArrayList<>();

        DayOfWeek firstDayOfWeek = firstDayOfMonth.getDayOfWeek();
        int emptyDaysBefore = (firstDayOfWeek.getValue() - DayOfWeek.MONDAY.getValue() + 7) % 7;

        LocalDate prevMonthDay = firstDayOfMonth.minusDays(emptyDaysBefore);
        for (int i = 0; i < emptyDaysBefore; i++) {
            daysOfMonth.add(prevMonthDay);
            prevMonthDay = prevMonthDay.plusDays(1);
        }

        for (int i = 1; i <= daysInMonth; i++) {
            daysOfMonth.add(firstDayOfMonth.withDayOfMonth(i));
        }

        int remainingDays = 7 - (daysOfMonth.size() % 7);
        if (remainingDays < 7) {
            LocalDate nextMonthDay = firstDayOfMonth.plusDays(daysInMonth);
            for (int i = 0; i < remainingDays; i++) {
                daysOfMonth.add(nextMonthDay);
                nextMonthDay = nextMonthDay.plusDays(1);
            }
        }

        List<List<LocalDate>> weeks = new ArrayList<>();
        for (int i = 0; i < daysOfMonth.size(); i += 7) {
            weeks.add(daysOfMonth.subList(i, Math.min(i + 7, daysOfMonth.size())));
        }
        return weeks;
    }
}
