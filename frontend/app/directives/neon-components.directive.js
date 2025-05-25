angular.module('studyOrchestratorApp')

// Timer Component Directive
.directive('neonTimer', function() {
    return {
        restrict: 'E',
        scope: {
            timeRemaining: '=',
            isActive: '=',
            onStart: '&',
            onPause: '&',
            onStop: '&'
        },
        template: `
            <div class="neon-timer-component">
                <div class="timer-display">
                    <div class="timer-time" ng-class="{'warning': timeRemaining <= 60, 'danger': timeRemaining <= 10}">
                        {{formatTime(timeRemaining)}}
                    </div>
                    <div class="timer-progress">
                        <div class="progress-ring">
                            <svg width="200" height="200">
                                <circle cx="100" cy="100" r="90" 
                                        fill="none" 
                                        stroke="rgba(255,255,255,0.1)" 
                                        stroke-width="8"/>
                                <circle cx="100" cy="100" r="90" 
                                        fill="none" 
                                        stroke="currentColor" 
                                        stroke-width="8"
                                        stroke-linecap="round"
                                        stroke-dasharray="{{circumference}}"
                                        stroke-dashoffset="{{strokeDashoffset}}"
                                        transform="rotate(-90 100 100)"
                                        class="progress-circle"/>
                            </svg>
                            <div class="timer-center">
                                <i class="fas" ng-class="isActive ? 'fa-pause' : 'fa-play'" 
                                   ng-click="toggleTimer()"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="timer-controls">
                    <button class="neon-btn secondary" ng-click="onStop()" ng-show="isActive">
                        <i class="fas fa-stop"></i> Stop
                    </button>
                </div>
            </div>
        `,
        link: function(scope, element, attrs) {
            scope.circumference = 2 * Math.PI * 90; // radius = 90
            
            scope.formatTime = function(seconds) {
                if (!seconds) return '00:00';
                var minutes = Math.floor(seconds / 60);
                var remainingSeconds = seconds % 60;
                return String(minutes).padStart(2, '0') + ':' + String(remainingSeconds).padStart(2, '0');
            };
            
            scope.toggleTimer = function() {
                if (scope.isActive) {
                    scope.onPause();
                } else {
                    scope.onStart();
                }
            };
            
            scope.$watch('timeRemaining', function(newVal) {
                if (newVal !== undefined) {
                    var totalTime = attrs.totalTime || 1500; // Default 25 minutes
                    var progress = (totalTime - newVal) / totalTime;
                    scope.strokeDashoffset = scope.circumference * (1 - progress);
                }
            });
        }
    };
})

// Progress Bar Directive
.directive('neonProgressBar', function() {
    return {
        restrict: 'E',
        scope: {
            value: '=',
            max: '=',
            type: '@',
            label: '@'
        },
        template: `
            <div class="neon-progress-component">
                <div class="progress-label" ng-show="label">{{label}}</div>
                <div class="progress-container">
                    <div class="progress-bar" ng-class="getProgressClass()">
                        <div class="progress-fill" 
                             ng-style="{'width': getPercentage() + '%'}"
                             ng-class="getProgressClass()">
                        </div>
                    </div>
                    <span class="progress-text">{{getPercentage()}}%</span>
                </div>
            </div>
        `,
        link: function(scope, element, attrs) {
            scope.getPercentage = function() {
                if (!scope.value || !scope.max) return 0;
                return Math.round((scope.value / scope.max) * 100);
            };
            
            scope.getProgressClass = function() {
                var percentage = scope.getPercentage();
                if (percentage >= 80) return 'progress-success';
                if (percentage >= 60) return 'progress-warning';
                return 'progress-danger';
            };
        }
    };
})

// Notification Toast Directive
.directive('neonNotification', ['$timeout', function($timeout) {
    return {
        restrict: 'E',
        scope: {
            message: '=',
            type: '=',
            show: '=',
            onDismiss: '&'
        },
        template: `
            <div class="neon-notification" ng-show="show" ng-class="type">
                <div class="notification-content">
                    <i class="fas" ng-class="getIcon()"></i>
                    <span class="notification-message">{{message}}</span>
                    <button class="notification-close" ng-click="dismiss()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `,
        link: function(scope, element, attrs) {
            scope.getIcon = function() {
                switch(scope.type) {
                    case 'success': return 'fa-check-circle';
                    case 'error': return 'fa-exclamation-circle';
                    case 'warning': return 'fa-exclamation-triangle';
                    default: return 'fa-info-circle';
                }
            };
            
            scope.dismiss = function() {
                scope.show = false;
                scope.onDismiss();
            };
            
            // Auto-dismiss after 5 seconds
            scope.$watch('show', function(newVal) {
                if (newVal) {
                    $timeout(function() {
                        scope.dismiss();
                    }, 5000);
                }
            });
        }
    };
}])

// Stats Card Directive
.directive('neonStatsCard', function() {
    return {
        restrict: 'E',
        scope: {
            title: '@',
            value: '=',
            icon: '@',
            color: '@',
            change: '@'
        },
        template: `
            <div class="neon-stats-card" ng-class="color">
                <div class="stats-icon">
                    <i class="fas {{icon}}"></i>
                </div>
                <div class="stats-content">
                    <div class="stats-value">{{value}}</div>
                    <div class="stats-title">{{title}}</div>
                    <div class="stats-change" ng-show="change" ng-class="getChangeClass()">
                        <i class="fas" ng-class="getChangeIcon()"></i>
                        {{change}}
                    </div>
                </div>
            </div>
        `,
        link: function(scope, element, attrs) {
            scope.getChangeClass = function() {
                if (!scope.change) return '';
                return scope.change.startsWith('+') ? 'positive' : 'negative';
            };
            
            scope.getChangeIcon = function() {
                if (!scope.change) return '';
                return scope.change.startsWith('+') ? 'fa-arrow-up' : 'fa-arrow-down';
            };
        }
    };
})

// Loading Spinner Directive
.directive('neonLoader', function() {
    return {
        restrict: 'E',
        scope: {
            show: '=',
            message: '@'
        },
        template: `
            <div class="neon-loader-overlay" ng-show="show">
                <div class="neon-loader">
                    <div class="loader-spinner"></div>
                    <div class="loader-message" ng-show="message">{{message}}</div>
                </div>
            </div>
        `
    };
})

// Glow Effect Directive
.directive('neonGlow', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var color = attrs.neonGlow || '#00f3ff';
            
            element.on('mouseenter', function() {
                element.css({
                    'box-shadow': `0 0 20px ${color}, 0 0 40px ${color}`,
                    'transition': 'box-shadow 0.3s ease'
                });
            });
            
            element.on('mouseleave', function() {
                element.css({
                    'box-shadow': '',
                    'transition': 'box-shadow 0.3s ease'
                });
            });
        }
    };
})

// Auto-focus Directive
.directive('neonFocus', ['$timeout', function($timeout) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            scope.$watch(attrs.neonFocus, function(newVal) {
                if (newVal) {
                    $timeout(function() {
                        element[0].focus();
                    }, 100);
                }
            });
        }
    };
}])

// Click Outside Directive
.directive('neonClickOutside', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var clickHandler = function(event) {
                if (!element[0].contains(event.target)) {
                    scope.$apply(function() {
                        scope.$eval(attrs.neonClickOutside);
                    });
                }
            };
            
            document.addEventListener('click', clickHandler);
            
            scope.$on('$destroy', function() {
                document.removeEventListener('click', clickHandler);
            });
        }
    };
});
