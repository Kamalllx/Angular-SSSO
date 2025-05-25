angular.module('studyOrchestratorApp')
.controller('CalendarController', ['$scope', 'ApiService', 'NotificationService',
function($scope, ApiService, NotificationService) {
    $scope.loading = true;
    $scope.events = [];
    $scope.selectedDate = new Date();
    $scope.currentView = 'month';
    $scope.showEventForm = false;
    $scope.showEventDetails = false;
    $scope.selectedEvent = null;
    
    $scope.newEvent = {
        title: '',
        start_time: '',
        duration: 30,
        description: '',
        type: 'study_session'
    };

    $scope.eventTypes = [
        { value: 'study_session', label: 'Study Session', icon: 'fa-book', color: 'neon-blue' },
        { value: 'break', label: 'Break', icon: 'fa-coffee', color: 'neon-green' },
        { value: 'assignment', label: 'Assignment', icon: 'fa-clipboard', color: 'neon-orange' },
        { value: 'exam', label: 'Exam', icon: 'fa-graduation-cap', color: 'neon-red' },
        { value: 'meeting', label: 'Meeting', icon: 'fa-users', color: 'neon-purple' }
    ];

    $scope.loadEvents = function() {
        $scope.loading = true;
        
        ApiService.getCalendarEvents().then(function(response) {
            $scope.events = response.data || [];
            $scope.processEvents();
        }).catch(function(error) {
            NotificationService.error('Failed to load calendar events');
            console.error('Calendar error:', error);
        }).finally(function() {
            $scope.loading = false;
        });
    };

    $scope.processEvents = function() {
        // Process events for display
        $scope.events.forEach(function(event) {
            event.start_date = new Date(event.start_time);
            event.end_date = new Date(event.end_time || event.start_time);
            event.typeInfo = $scope.eventTypes.find(type => type.value === event.event_type) || $scope.eventTypes[0];
        });

        $scope.generateCalendarGrid();
    };

    $scope.generateCalendarGrid = function() {
        var year = $scope.selectedDate.getFullYear();
        var month = $scope.selectedDate.getMonth();
        
        // Get first day of month and number of days
        var firstDay = new Date(year, month, 1);
        var lastDay = new Date(year, month + 1, 0);
        var daysInMonth = lastDay.getDate();
        var startDayOfWeek = firstDay.getDay();
        
        $scope.calendarDays = [];
        $scope.monthName = firstDay.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        
        // Add empty cells for days before month starts
        for (var i = 0; i < startDayOfWeek; i++) {
            $scope.calendarDays.push(null);
        }
        
        // Add days of the month
        for (var day = 1; day <= daysInMonth; day++) {
            var date = new Date(year, month, day);
            var dayEvents = $scope.events.filter(function(event) {
                return event.start_date.toDateString() === date.toDateString();
            });
            
            $scope.calendarDays.push({
                date: date,
                day: day,
                events: dayEvents,
                isToday: date.toDateString() === new Date().toDateString(),
                isWeekend: date.getDay() === 0 || date.getDay() === 6
            });
        }
    };

    $scope.createEvent = function() {
        if (!$scope.newEvent.title.trim()) {
            NotificationService.warning('Please enter an event title');
            return;
        }

        var eventData = {
            title: $scope.newEvent.title.trim(),
            start_time: $scope.newEvent.start_time,
            duration: parseInt($scope.newEvent.duration),
            description: $scope.newEvent.description.trim(),
            event_type: $scope.newEvent.type
        };

        ApiService.createCalendarEvent(eventData).then(function(response) {
            NotificationService.success('Event created successfully');
            $scope.resetEventForm();
            $scope.showEventForm = false;
            $scope.loadEvents();
        }).catch(function(error) {
            if (error.data && error.data.error && error.data.error.includes('Google Calendar service not available')) {
                NotificationService.warning('Event saved locally. Google Calendar integration not configured.');
            } else {
                NotificationService.error('Failed to create event');
            }
        });
    };

    $scope.updateEvent = function() {
        if (!$scope.selectedEvent) return;

        var eventData = {
            title: $scope.selectedEvent.title,
            description: $scope.selectedEvent.description,
            event_type: $scope.selectedEvent.event_type
        };

        ApiService.updateCalendarEvent($scope.selectedEvent.id, eventData).then(function(response) {
            NotificationService.success('Event updated successfully');
            $scope.showEventDetails = false;
            $scope.loadEvents();
        }).catch(function(error) {
            NotificationService.error('Failed to update event');
        });
    };

    $scope.deleteEvent = function(event) {
        if (!confirm('Are you sure you want to delete this event?')) return;

        ApiService.deleteCalendarEvent(event.id).then(function(response) {
            NotificationService.success('Event deleted successfully');
            $scope.showEventDetails = false;
            $scope.loadEvents();
        }).catch(function(error) {
            NotificationService.error('Failed to delete event');
        });
    };

    $scope.scheduleStudyBreak = function() {
        var breakData = {
            study_duration: 25,
            break_duration: 5,
            start_time: new Date().toISOString()
        };

        ApiService.scheduleStudyBreak(breakData).then(function(response) {
            NotificationService.success('Study break scheduled successfully');
            $scope.loadEvents();
        }).catch(function(error) {
            NotificationService.error('Failed to schedule study break');
        });
    };

    $scope.syncCalendar = function() {
        $scope.loading = true;
        
        ApiService.syncCalendar().then(function(response) {
            NotificationService.success('Calendar synced successfully');
            $scope.loadEvents();
        }).catch(function(error) {
            NotificationService.error('Failed to sync calendar');
        }).finally(function() {
            $scope.loading = false;
        });
    };

    $scope.previousMonth = function() {
        $scope.selectedDate.setMonth($scope.selectedDate.getMonth() - 1);
        $scope.generateCalendarGrid();
    };

    $scope.nextMonth = function() {
        $scope.selectedDate.setMonth($scope.selectedDate.getMonth() + 1);
        $scope.generateCalendarGrid();
    };

    $scope.selectDay = function(day) {
        if (!day) return;
        
        var timeStr = '09:00';
        var dateTime = new Date(day.date);
        var timeParts = timeStr.split(':');
        dateTime.setHours(parseInt(timeParts[0]), parseInt(timeParts[1]), 0, 0);
        
        $scope.newEvent.start_time = dateTime.toISOString().slice(0, 16);
        $scope.showEventForm = true;
    };

    $scope.viewEvent = function(event) {
        $scope.selectedEvent = angular.copy(event);
        $scope.showEventDetails = true;
    };

    $scope.resetEventForm = function() {
        $scope.newEvent = {
            title: '',
            start_time: '',
            duration: 30,
            description: '',
            type: 'study_session'
        };
    };

    $scope.closeEventForm = function() {
        $scope.showEventForm = false;
        $scope.resetEventForm();
    };

    $scope.closeEventDetails = function() {
        $scope.showEventDetails = false;
        $scope.selectedEvent = null;
    };

    $scope.formatEventTime = function(event) {
        return new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    };

    $scope.getEventTypeInfo = function(eventType) {
        return $scope.eventTypes.find(type => type.value === eventType) || $scope.eventTypes[0];
    };

    // Initialize
    $scope.loadEvents();
}]);
