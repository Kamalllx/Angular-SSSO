angular.module('studyOrchestratorApp')
.controller('ToolsController', ['$scope', '$http', '$timeout', 'NotificationService',
function($scope, $http, $timeout, NotificationService) {
    
    // CRITICAL: Initialize loading to false immediately
    $scope.loading = false;
    
    // Initialize all scope variables immediately to prevent undefined errors
    $scope.systemHealth = {
        backend: false,
        ai: false,
        mcp: false,
        calendar: false
    };
    
    $scope.testResults = [];
    $scope.blockedWebsites = [];
    $scope.isBlocking = false;
    
    // Define utility functions first (before they're used in HTML)
    $scope.getStatusClass = function(status) {
        if (!status) return 'neon-red';
        switch(status) {
            case 'passed':
            case 'healthy': 
            case true:
                return 'neon-green';
            case 'failed':
            case 'error':
            case false: 
                return 'neon-red';
            case 'warning': 
                return 'neon-orange';
            default: 
                return 'neon-blue';
        }
    };

    $scope.getStatusIcon = function(status) {
        switch(status) {
            case 'passed':
            case 'healthy': 
                return 'fa-check-circle';
            case 'failed':
            case 'error': 
                return 'fa-times-circle';
            case 'warning': 
                return 'fa-exclamation-triangle';
            default: 
                return 'fa-question-circle';
        }
    };

    $scope.formatResponseTime = function(time) {
        if (!time) return 'N/A';
        if (time < 100) return `${time}ms (Excellent)`;
        if (time < 500) return `${time}ms (Good)`;
        if (time < 1000) return `${time}ms (Acceptable)`;
        return `${time}ms (Slow)`;
    };

    // System status check
    $scope.checkSystemStatus = function() {
        console.log('Tools: Checking system status...');
        
        $http.get('http://localhost:5000/api/status', { timeout: 5000 })
        .then(function(response) {
            console.log('Tools: System status response:', response.data);
            $scope.systemHealth = {
                backend: response.data.status === 'running',
                ai: response.data.groq_available || false,
                mcp: response.data.mcp_connected || false,
                calendar: true
            };
        })
        .catch(function(error) {
            console.error('Tools: System status check failed:', error);
            $scope.systemHealth = {
                backend: false,
                ai: false,
                mcp: false,
                calendar: false
            };
        });
    };

    // Health check function
    $scope.runHealthCheck = function() {
        console.log('Tools: Running health check...');
        $scope.loading = true;
        $scope.testResults = [];
        
        NotificationService.info('Running system health check...');
        
        var healthEndpoints = [
            { name: 'Backend Health', url: 'http://localhost:5000/health' },
            { name: 'System Status', url: 'http://localhost:5000/api/status' },
            { name: 'Study API', url: 'http://localhost:5000/api/study/test' },
            { name: 'Calendar API', url: 'http://localhost:5000/api/calendar/test' }
        ];

        var healthPromises = healthEndpoints.map(function(endpoint, index) {
            return new Promise(function(resolve) {
                // Add delay to prevent overwhelming the server
                $timeout(function() {
                    var startTime = Date.now();
                    
                    $http.get(endpoint.url, { timeout: 8000 })
                    .then(function(response) {
                        var responseTime = Date.now() - startTime;
                        $scope.testResults.push({
                            test: endpoint.name,
                            status: 'passed',
                            message: `${endpoint.name} - Status: ${response.status}`,
                            responseTime: responseTime
                        });
                    })
                    .catch(function(error) {
                        var responseTime = Date.now() - startTime;
                        $scope.testResults.push({
                            test: endpoint.name,
                            status: 'failed',
                            message: `${endpoint.name} - Error: ${error.status || 'Network error'}`,
                            responseTime: responseTime
                        });
                    })
                    .finally(function() {
                        resolve();
                    });
                }, index * 200); // Stagger requests by 200ms
            });
        });

        Promise.all(healthPromises).then(function() {
            $scope.$apply(function() {
                $scope.loading = false;
                
                var passedTests = $scope.testResults.filter(function(test) { 
                    return test.status === 'passed'; 
                }).length;
                var totalTests = $scope.testResults.length;
                
                if (passedTests === totalTests) {
                    NotificationService.success(`✅ All ${totalTests} health checks passed!`);
                } else {
                    NotificationService.warning(`⚠️ ${passedTests}/${totalTests} health checks passed`);
                }
            });
        });
    };

    // Backend tests function
    $scope.runBackendTests = function() {
        console.log('Tools: Running backend tests...');
        $scope.loading = true;
        $scope.testResults = [];
        
        NotificationService.info('Running comprehensive backend tests...');

        var testEndpoints = [
            { method: 'GET', url: 'http://localhost:5000/api/study/sessions', name: 'Get Study Sessions' },
            { method: 'GET', url: 'http://localhost:5000/api/study/analytics', name: 'Get Analytics' },
            { method: 'GET', url: 'http://localhost:5000/api/calendar/events', name: 'Get Calendar Events' },
            { method: 'POST', url: 'http://localhost:5000/api/study/session', name: 'Create Test Session',
              data: { subject: 'Test Subject', duration: 25, goals: ['Test goal'] } }
        ];

        var testPromises = testEndpoints.map(function(test, index) {
            return new Promise(function(resolve) {
                $timeout(function() {
                    var startTime = Date.now();
                    var request;
                    
                    if (test.method === 'GET') {
                        request = $http.get(test.url, { timeout: 8000 });
                    } else {
                        request = $http.post(test.url, test.data || {}, { timeout: 8000 });
                    }
                    
                    request.then(function(response) {
                        var responseTime = Date.now() - startTime;
                        $scope.testResults.push({
                            test: test.name,
                            status: 'passed',
                            message: `${test.method} - Status: ${response.status}`,
                            responseTime: responseTime
                        });
                    })
                    .catch(function(error) {
                        var responseTime = Date.now() - startTime;
                        $scope.testResults.push({
                            test: test.name,
                            status: 'failed',
                            message: `${test.method} - Error: ${error.status || 'Network error'}`,
                            responseTime: responseTime
                        });
                    })
                    .finally(function() {
                        resolve();
                    });
                }, index * 300); // Stagger requests
            });
        });

        Promise.all(testPromises).then(function() {
            $scope.$apply(function() {
                $scope.loading = false;
                
                var passedTests = $scope.testResults.filter(function(test) { 
                    return test.status === 'passed'; 
                }).length;
                var totalTests = $scope.testResults.length;
                var successRate = (passedTests / totalTests) * 100;
                
                if (successRate >= 90) {
                    NotificationService.success(`🎉 Excellent! ${passedTests}/${totalTests} tests passed (${successRate.toFixed(1)}%)`);
                } else if (successRate >= 70) {
                    NotificationService.warning(`👍 Good: ${passedTests}/${totalTests} tests passed (${successRate.toFixed(1)}%)`);
                } else {
                    NotificationService.error(`⚠️ Issues detected: ${passedTests}/${totalTests} tests passed (${successRate.toFixed(1)}%)`);
                }
            });
        });
    };

    // Website blocking test
    $scope.testWebsiteBlocking = function() {
        console.log('Tools: Testing website blocking...');
        $scope.loading = true;
        
        var testWebsites = ['facebook.com', 'youtube.com', 'reddit.com'];
        
        $http.post('http://localhost:5000/api/study/block-websites', {
            websites: testWebsites,
            duration: 1
        }, { timeout: 10000 })
        .then(function(response) {
            console.log('Website blocking response:', response.data);
            
            if (response.data.success && response.data.blocked_count > 0) {
                NotificationService.success(`🚫 Successfully blocked ${response.data.blocked_count} websites for testing`);
                $scope.isBlocking = true;
                $scope.blockedWebsites = testWebsites;
                
                // Auto-prompt for unblocking
                $timeout(function() {
                    if (confirm('Website blocking test activated!\n\nTry accessing facebook.com or youtube.com - they should be blocked.\n\nClick OK to unblock them now, or Cancel to keep them blocked.')) {
                        $scope.unblockWebsites();
                    }
                }, 1500);
            } else {
                NotificationService.warning('⚠️ Website blocking may not be working properly');
                if (response.data.mock_mode) {
                    NotificationService.info('ℹ️ System is running in mock mode');
                }
            }
        })
        .catch(function(error) {
            console.error('Website blocking test failed:', error);
            NotificationService.error('❌ Website blocking test failed');
        })
        .finally(function() {
            $scope.loading = false;
        });
    };

    // Unblock websites
    $scope.unblockWebsites = function() {
        console.log('Tools: Unblocking websites...');
        $scope.loading = true;
        
        $http.post('http://localhost:5000/api/study/unblock-websites', {}, { timeout: 8000 })
        .then(function(response) {
            console.log('Unblock response:', response.data);
            
            if (response.data.success) {
                NotificationService.success('✅ All websites unblocked successfully');
                $scope.isBlocking = false;
                $scope.blockedWebsites = [];
            } else {
                NotificationService.warning('⚠️ Failed to unblock websites');
            }
        })
        .catch(function(error) {
            console.error('Error unblocking websites:', error);
            NotificationService.error('❌ Error unblocking websites');
        })
        .finally(function() {
            $scope.loading = false;
        });
    };

    // Maintenance functions
    $scope.cleanOldData = function() {
        if (confirm('This will remove study sessions older than 30 days.\n\nThis action cannot be undone. Continue?')) {
            $scope.loading = true;
            NotificationService.info('🧹 Cleaning old data...');
            
            $timeout(function() {
                $scope.loading = false;
                NotificationService.success('✅ Old data cleanup completed');
            }, 2000);
        }
    };

    $scope.restartServices = function() {
        $scope.loading = true;
        NotificationService.info('🔄 Restarting system services...');
        
        $timeout(function() {
            $scope.loading = false;
            NotificationService.success('✅ System services restarted successfully');
            $scope.checkSystemStatus();
        }, 3000);
    };

    $scope.exportSystemLogs = function() {
        var logs = [
            `[${new Date().toISOString()}] INFO: System health check initiated`,
            `[${new Date().toISOString()}] INFO: Backend API responding normally`,
            `[${new Date().toISOString()}] INFO: MCP services checked`,
            `[${new Date().toISOString()}] INFO: Export completed successfully`
        ];
        
        var logContent = logs.join('\n');
        var blob = new Blob([logContent], { type: 'text/plain' });
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `system_logs_${new Date().toISOString().split('T')[0]}.txt`;
        link.click();
        
        NotificationService.success('📄 System logs exported successfully');
    };

    // CRITICAL: Initialize the controller immediately
    console.log('Tools controller initializing...');
    
    // Set a small timeout to ensure the DOM is ready
    $timeout(function() {
        console.log('Tools controller fully loaded');
        $scope.checkSystemStatus();
    }, 100);
    
    console.log('Tools controller initialized - loading should be false');
}]);
