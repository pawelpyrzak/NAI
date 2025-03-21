document.addEventListener("DOMContentLoaded", function () {
        const timeline = document.querySelector('.timeline');

        function toggleTaskActivity(button) {
            console.log(button);
            const taskActivity = button.closest('.task-activity');
            const hiddenTasks = taskActivity.querySelector('.hidden-tasks');
            const expandIcon = button.querySelector('.expand-tasks-icon img');
            const timelineTest = taskActivity.closest('.timeline-test');
            const Task = timelineTest.querySelector('.task-creation-with-activity');
            const point = Task.querySelector('.timeline-point');
            console.log(point)
            const nextElement = findNextTimelinePoint(point);


            // Sprawdzamy, czy sekcja jest aktualnie ukryta
            if (hiddenTasks.style.display === 'none' || hiddenTasks.style.display === '') {
                // Jeśli ukryta, pokazujemy ją
                hiddenTasks.style.display = 'block';
                // Zmiana ikony na strzałkę w górę
                expandIcon.src = "../static/images/chevron-up.svg"; // Strzałka w górę
            } else {
                // Jeśli widoczna, ukrywamy ją
                hiddenTasks.style.display = 'none';
                // Zmiana ikony na strzałkę w dół
                expandIcon.src = "../static/images/chevron-down (3).svg"; // Strzałka w dół
            }
            if (nextElement) {
                calculateDistanceBetweenPoints(point, nextElement);
            }
            // Oblicz odległość między punktami po kliknięciu dla podanego elementu

        }

        // Nasłuchiwanie na kliknięcie w przycisk
        const expandButtons = document.querySelectorAll('.expand-tasks');
        expandButtons.forEach(button => {
            button.addEventListener('click', function () {
                toggleTaskActivity(button);
            });
        });

        // Funkcja do obliczania odległości między podanym elementem a najbliższym dolnym punktem
        function calculateDistanceBetweenPoints(currentPoint, nextPoint) {
            const currentRect = currentPoint.getBoundingClientRect();
            const nextRect = nextPoint.getBoundingClientRect();
            const distance = nextRect.top - currentRect.bottom;
            if (distance) {
                console.log(`Najbliższy punkt znajduje się ${distance}px poniżej 'task-creation-with-activity'`);
                timeline.style.setProperty('--dynamic-line-height', `${distance}px`);
            } else {
                console.log("Brak punktów poniżej elementu 'task-creation-with-activity'.");
            }
        }

        function findNextTimelinePoint(startElement) {
            const parent = startElement.closest('.timeline-loop'); // Znajdź rodzica z klasą .timeline-loop
            if (!parent) return null; // Jeśli brak rodzica, zakończ

            const allPoints = parent.querySelectorAll('.timeline-point'); // Znajdź wszystkie .timeline-point w rodzicu
            const allPointsArray = Array.from(allPoints); // Zamień NodeList na tablicę
            const currentIndex = allPointsArray.indexOf(startElement); // Znajdź indeks bieżącego elementu

            if (currentIndex >= 0 && currentIndex < allPointsArray.length - 1) {
                return allPointsArray[currentIndex + 1]; // Zwróć kolejny element
            }
            return null; // Jeśli nie ma kolejnego elementu
        }

    }
)
;
