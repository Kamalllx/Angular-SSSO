angular.module('studyOrchestratorApp')
.service('NotificationService', ['$rootScope', function($rootScope) {
    var service = {};

    service.success = function(message) {
        $rootScope.$broadcast('notification', {
            type: 'success',
            message: message
        });
    };

    service.error = function(message) {
        $rootScope.$broadcast('notification', {
            type: 'error',
            message: message
        });
    };

    service.warning = function(message) {
        $rootScope.$broadcast('notification', {
            type: 'warning',
            message: message
        });
    };

    service.info = function(message) {
        $rootScope.$broadcast('notification', {
            type: 'info',
            message: message
        });
    };

    return service;
}]);
