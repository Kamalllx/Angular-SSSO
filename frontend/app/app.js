angular.module('studyOrchestratorApp', ['ngRoute', 'ngAnimate'])
.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {
    $routeProvider
        .when('/dashboard', {
            templateUrl: 'app/views/dashboard.html',
            controller: 'DashboardController'
        })
        .when('/sessions', {
            templateUrl: 'app/views/sessions.html',
            controller: 'SessionsController'
        })
        .when('/analytics', {
            templateUrl: 'app/views/analytics.html',
            controller: 'AnalyticsController'
        })
        .when('/calendar', {
            templateUrl: 'app/views/calendar.html',
            controller: 'CalendarController'
        })
        .when('/preferences', {
            templateUrl: 'app/views/preferences.html',
            controller: 'PreferencesController'
        })
        .when('/tools', {
            templateUrl: 'app/views/tools.html',
            controller: 'ToolsController'
        })
        .otherwise({
            redirectTo: '/dashboard'
        });
    
    // DISABLE HTML5 mode to fix routing issues
    $locationProvider.html5Mode(false);
    $locationProvider.hashPrefix('!');
}])
.controller('MainController', ['$scope', '$location', '$http', 'NotificationService', 
function($scope, $location, $http, NotificationService) {
    $scope.sidebarCollapsed = false;
    $scope.systemStatus = {
        backend: false,
        ai: false,
        mcp: false
    };
    $scope.notifications = [];
    $scope.modal = {
        show: false,
        title: '',
        content: ''
    };

    // FIXED: Navigation helpers
    $scope.isActive = function(route) {
        return $location.path() === route;
    };

    $scope.toggleSidebar = function() {
        $scope.sidebarCollapsed = !$scope.sidebarCollapsed;
    };

    // Initialize system status check
    $scope.checkSystemStatus = function() {
        $http.get('http://localhost:5000/api/status').then(function(response) {
            $scope.systemStatus = {
                backend: response.data.status === 'running',
                ai: response.data.groq_available || false,
                mcp: response.data.mcp_connected || false
            };
        }).catch(function() {
            $scope.systemStatus = {
                backend: false,
                ai: false,
                mcp: false
            };
        });
    };

    // Quick start session
    $scope.quickStartSession = function() {
        // Redirect to sessions page
        $location.path('/sessions');
    };

    $scope.closeModal = function() {
        $scope.modal.show = false;
    };

    // Update page title based on route
    $scope.$on('$routeChangeSuccess', function() {
        var path = $location.path();
        var pageTitle = path.substring(1);
        $scope.currentPageTitle = pageTitle.charAt(0).toUpperCase() + pageTitle.slice(1);
    });

    // Notification handling
    $scope.getNotificationIcon = function(type) {
        switch(type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    };

    $scope.dismissNotification = function(index) {
        $scope.notifications.splice(index, 1);
    };

    // Listen for notifications
    $scope.$on('notification', function(event, data) {
        $scope.notifications.push({
            type: data.type,
            message: data.message,
            show: true
        });
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            $scope.$apply(function() {
                var index = $scope.notifications.findIndex(function(n) { 
                    return n.message === data.message; 
                });
                if (index > -1) {
                    $scope.notifications.splice(index, 1);
                }
            });
        }, 5000);
    });

    // Initialize
    $scope.checkSystemStatus();
    setInterval($scope.checkSystemStatus, 30000); // Check every 30 seconds
}]);
