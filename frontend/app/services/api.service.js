angular.module('studyOrchestratorApp')
.service('ApiService', ['$http', '$q', function($http, $q) {
    var baseUrl = 'http://localhost:5000/api';
    var service = {};

    // Helper function to handle API calls
    function apiCall(method, endpoint, data) {
        var config = {
            method: method,
            url: baseUrl + endpoint,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            config.data = data;
        }

        return $http(config).catch(function(error) {
            console.error('API Error:', error);
            throw error;
        });
    }

    // System endpoints
    service.getSystemStatus = function() {
        return $http.get('http://localhost:5000/api/status');
    };

    service.getSystemHealth = function() {
        return $http.get('http://localhost:5000/health');
    };

    // Study session endpoints
    service.getStudySessions = function() {
        return apiCall('GET', '/study/sessions');
    };

    service.createStudySession = function(sessionData) {
        return apiCall('POST', '/study/session', sessionData);
    };

    service.startStudySession = function(sessionId) {
        return apiCall('POST', '/study/session/' + sessionId + '/start');
    };

    service.endStudySession = function(sessionId, sessionData) {
        return apiCall('POST', '/study/session/' + sessionId + '/end', sessionData);
    };

    service.getStudySession = function(sessionId) {
        return apiCall('GET', '/study/session/' + sessionId);
    };

    service.generateStudyPlan = function(planData) {
        return apiCall('POST', '/study/plan', planData);
    };

    // Analytics endpoints
    service.getAnalytics = function() {
        return apiCall('GET', '/study/analytics');
    };

    // Calendar endpoints
    service.getCalendarEvents = function(date) {
        var endpoint = '/calendar/events';
        if (date) {
            endpoint += '?date=' + date;
        }
        return apiCall('GET', endpoint);
    };

    service.createCalendarEvent = function(eventData) {
        return apiCall('POST', '/calendar/event', eventData);
    };

    service.updateCalendarEvent = function(eventId, eventData) {
        return apiCall('PUT', '/calendar/event/' + eventId, eventData);
    };

    service.deleteCalendarEvent = function(eventId) {
        return apiCall('DELETE', '/calendar/event/' + eventId);
    };

    service.scheduleStudyBreak = function(breakData) {
        return apiCall('POST', '/calendar/schedule-break', breakData);
    };

    service.syncCalendar = function() {
        return apiCall('POST', '/calendar/sync');
    };

    // Website blocking endpoints
    service.blockWebsites = function(websites, duration) {
        return apiCall('POST', '/study/block-websites', {
            websites: websites,
            duration: duration
        });
    };

    service.unblockWebsites = function() {
        return apiCall('POST', '/study/unblock-websites');
    };

    // Preferences endpoints
    service.getPreferences = function() {
        return apiCall('GET', '/study/preferences');
    };

    service.updatePreferences = function(preferences) {
        return apiCall('POST', '/study/preferences', preferences);
    };

    return service;
}]);
