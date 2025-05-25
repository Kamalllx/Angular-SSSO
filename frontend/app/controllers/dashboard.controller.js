angular.module('studyOrchestratorApp')
.controller('DashboardController', ['$scope', 'ApiService', 'NotificationService',
function($scope, ApiService, NotificationService) {
    $scope.loading = true;
    $scope.dashboardData = {
        weeklyStats: {},
        todaySessions: [],
        recommendations: {},
        quickStartOptions: [
            { name: 'Mathematics', icon: 'fa-calculator', color: 'neon-blue' },
            { name: 'Programming', icon: 'fa-code', color: 'neon-green' },
            { name: 'Language', icon: 'fa-language', color: 'neon-pink' },
            { name: 'Science', icon: 'fa-flask', color: 'neon-purple' },
            { name: 'History', icon: 'fa-landmark', color: 'neon-orange' },
            { name: 'Literature', icon: 'fa-book', color: 'neon-cyan' }
        ]
    };

    $scope.loadDashboard = function() {
        $scope.loading = true;
        
        // Load analytics for dashboard overview
        ApiService.getAnalytics().then(function(response) {
            $scope.dashboardData.weeklyStats = response.data.weekly_stats || {};
            $scope.dashboardData.recommendations = response.data.recommendations || {};
        }).catch(function(error) {
            NotificationService.error('Failed to load analytics data');
        });

        // Load today's sessions
        ApiService.getStudySessions().then(function(response) {
            var today = new Date().toDateString();
            $scope.dashboardData.todaySessions = (response.data || []).filter(function(session) {
                if (session.start_time) {
                    return new Date(session.start_time).toDateString() === today;
                }
                return false;
            });
        }).catch(function(error) {
            NotificationService.error('Failed to load study sessions');
        }).finally(function() {
            $scope.loading = false;
        });
    };

    $scope.quickStart = function(subject) {
        var sessionData = {
            subject: subject,
            duration: 25,
            goals: ['Complete focused study session for ' + subject]
        };

        ApiService.createStudySession(sessionData).then(function(response) {
            NotificationService.success('Quick study session created for ' + subject);
            $scope.loadDashboard();
        }).catch(function(error) {
            NotificationService.error('Failed to create study session');
        });
    };

    $scope.getSessionStatusClass = function(session) {
        if (session.end_time) return 'completed';
        if (session.start_time) return 'active';
        return 'scheduled';
    };

    $scope.formatDuration = function(minutes) {
        if (!minutes) return '0 min';
        if (minutes < 60) return minutes + ' min';
        var hours = Math.floor(minutes / 60);
        var remainingMinutes = minutes % 60;
        return hours + 'h ' + (remainingMinutes > 0 ? remainingMinutes + 'm' : '');
    };

    $scope.formatTime = function(isoString) {
        if (!isoString) return 'Not set';
        return new Date(isoString).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    };

    // Initialize dashboard
    $scope.loadDashboard();
}]);
