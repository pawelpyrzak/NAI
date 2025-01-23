document.addEventListener("DOMContentLoaded", function() {
    const expandTasks = document.querySelector('.expand-tasks');
    const hiddenTasks = document.querySelector('.hidden-tasks');
    const timelineEventTask = document.querySelector('.timeline-event.task-creation');
    const timelineEventWithActivity = document.querySelector('.timeline-event.task-creation-with-activity');
    const timeline = document.querySelector('.timeline'); 
   
    if (hiddenTasks.style.display === '' || hiddenTasks.style.display === 'none') {
        hiddenTasks.style.display = 'none'; 
        timelineEventTask.classList.remove('task-creation-expanded'); 
    } else {
        hiddenTasks.style.display = 'block'; 
        timelineEventTask.classList.add('task-creation-expanded'); 
    }

    expandTasks.addEventListener('click', function() {
        if (hiddenTasks.style.display === 'none') {
            hiddenTasks.style.display = 'block';
            timelineEventTask.classList.add('task-creation-expanded');
        } else {
            hiddenTasks.style.display = 'none';
            timelineEventTask.classList.remove('task-creation-expanded');
        }
        calculateDistanceBetweenPoints();
    });


    function calculateDistanceBetweenPoints() {
        const timelinePoints = document.querySelectorAll('.timeline-point');
        const taskCreationWithActivityRect = timelineEventWithActivity.getBoundingClientRect();
        let closestDistance = Infinity;
        let closestPoint = null;

        timelinePoints.forEach(point => {
            const pointRect = point.getBoundingClientRect();

            if (pointRect.top > taskCreationWithActivityRect.bottom) {
                const distance = pointRect.top - taskCreationWithActivityRect.bottom;

               
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestPoint = point;
                }
            }
        });

        if (closestPoint) {
            console.log(`Najbliższy punkt znajduje się ${closestDistance}px poniżej 'task-creation-with-activity'`);
            timeline.style.setProperty('--dynamic-line-height', `${closestDistance}px`);
        } else {
            console.log("Brak punktów poniżej elementu 'task-creation-with-activity'.");
        }
    }
});
