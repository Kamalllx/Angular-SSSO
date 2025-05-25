angular.module('studyOrchestratorApp')
.controller('SessionsController', ['$scope', '$interval', 'ApiService', 'NotificationService',
function($scope, $interval, ApiService, NotificationService) {
    $scope.loading = true;
    $scope.sessions = [];
    $scope.activeSession = null;
    $scope.sessionTimer = null;
    $scope.timeRemaining = 0;
    $scope.isActive = false;
    $scope.isPaused = false;
    
    $scope.newSession = {
        subject: '',
        duration: 25,
        goals: [''],
        blockWebsites: true
    };

    $scope.showNewSessionForm = false;
    $scope.showSessionDetails = false;
    $scope.selectedSession = null;

    $scope.loadSessions = function() {
        $scope.loading = true;
        ApiService.getStudySessions().then(function(response) {
            $scope.sessions = response.data || [];
        }).catch(function(error) {
            NotificationService.error('Failed to load study sessions');
        }).finally(function() {
            $scope.loading = false;
        });
    };

    $scope.createSession = function() {
        if (!$scope.newSession.subject.trim()) {
            NotificationService.warning('Please enter a subject');
            return;
        }

        var sessionData = {
            subject: $scope.newSession.subject.trim(),
            duration: parseInt($scope.newSession.duration),
            goals: $scope.newSession.goals.filter(function(goal) {
                return goal.trim() !== '';
            })
        };

        ApiService.createStudySession(sessionData).then(function(response) {
            NotificationService.success('Study session created successfully');
            $scope.resetForm();
            $scope.showNewSessionForm = false;
            $scope.loadSessions();
            
            // Generate AI study plan
            $scope.generateStudyPlan(response.data);
        }).catch(function(error) {
            NotificationService.error('Failed to create study session');
        });
    };

    $scope.generateStudyPlan = function(session) {
        var planData = {
            subject: session.subject,
            duration: session.duration_minutes,
            goals: session.goals || []
        };

        ApiService.generateStudyPlan(planData).then(function(response) {
            session.studyPlan = response.data;
            NotificationService.success('AI study plan generated');
        }).catch(function(error) {
            NotificationService.warning('Could not generate AI study plan');
        });
    };

    $scope.startSession = function(session) {
        ApiService.startStudySession(session.id).then(function(response) {
            $scope.activeSession = session;
            $scope.isActive = true;
            $scope.isPaused = false;
            $scope.timeRemaining = session.duration_minutes * 60;
            
            // Block websites if enabled
            if ($scope.newSession.blockWebsites) {
                $scope.blockWebsites(session.duration_minutes);
            }
            
            $scope.startTimer();
            NotificationService.success('Study session started');
        }).catch(function(error) {
            NotificationService.error('Failed to start session');
        });
    };

    $scope.startTimer = function() {
        if ($scope.sessionTimer) {
            $interval.cancel($scope.sessionTimer);
        }

        $scope.sessionTimer = $interval(function() {
            if (!$scope.isPaused && $scope.timeRemaining > 0) {
                $scope.timeRemaining--;
                
                if ($scope.timeRemaining <= 0) {
                    $scope.completeSession();
                }
            }
        }, 1000);
    };

    $scope.pauseSession = function() {
        $scope.isPaused = !$scope.isPaused;
        NotificationService.info($scope.isPaused ? 'Session paused' : 'Session resumed');
    };

    $scope.endSession = function() {
        if ($scope.sessionTimer) {
            $interval.cancel($scope.sessionTimer);
        }

        var sessionData = {
            focus_score: 75, // This would be calculated based on user input
            completed_goals: $scope.activeSession.goals || [],
            notes: '',
            distractions: 0,
            breaks_taken: 0
        };

        ApiService.endStudySession($scope.activeSession.id, sessionData).then(function(response) {
            NotificationService.success('Study session ended successfully');
            $scope.resetSession();
            $scope.unblockWebsites();
            $scope.loadSessions();
        }).catch(function(error) {
            NotificationService.error('Failed to end session');
        });
    };

    $scope.completeSession = function() {
        NotificationService.success('🎉 Study session completed! Great work!');
        $scope.endSession();
    };

    $scope.resetSession = function() {
        $scope.activeSession = null;
        $scope.isActive = false;
        $scope.isPaused = false;
        $scope.timeRemaining = 0;
        
        if ($scope.sessionTimer) {
            $interval.cancel($scope.sessionTimer);
        }
    };

    $scope.blockWebsites = function(duration) {
        var websites = [
            'facebook.com', 'twitter.com', 'youtube.com',
            'instagram.com', 'reddit.com', 'tiktok.com'
        ];

        ApiService.blockWebsites(websites, duration).then(function(response) {
            if (response.data.success) {
                NotificationService.success('Distracting websites blocked');
            } else {
                NotificationService.warning('Website blocking failed - check permissions');
            }
        }).catch(function(error) {
            NotificationService.warning('Website blocking not available');
        });
    };

    $scope.unblockWebsites = function() {
        ApiService.unblockWebsites().then(function(response) {
            if (response.data.success) {
                NotificationService.success('Websites unblocked');
            }
        }).catch(function(error) {
            console.log('Unblock failed:', error);
        });
    };

    // Form helpers
    $scope.addGoal = function() {
        $scope.newSession.goals.push('');
    };

    $scope.removeGoal = function(index) {
        if ($scope.newSession.goals.length > 1) {
            $scope.newSession.goals.splice(index, 1);
        }
    };

    $scope.resetForm = function() {
        $scope.newSession = {
            subject: '',
            duration: 25,
            goals: [''],
            blockWebsites: true
        };
    };

    // Utility functions
    $scope.formatTime = function(seconds) {
        var minutes = Math.floor(seconds / 60);
        var remainingSeconds = seconds % 60;
        return String(minutes).padStart(2, '0') + ':' + String(remainingSeconds).padStart(2, '0');
    };

    $scope.getProgressPercentage = function() {
        if (!$scope.activeSession) return 0;
        var total = $scope.activeSession.duration_minutes * 60;
        var elapsed = total - $scope.timeRemaining;
        return (elapsed / total) * 100;
    };

    $scope.getProgressColor = function() {
        var percentage = $scope.getProgressPercentage();
        if (percentage < 50) return 'neon-green';
        if (percentage < 80) return 'neon-yellow';
        return 'neon-red';
    };

    $scope.viewSessionDetails = function(session) {
        $scope.selectedSession = session;
        $scope.showSessionDetails = true;
    };

    // Cleanup on destroy
    $scope.$on('$destroy', function() {
        if ($scope.sessionTimer) {
            $interval.cancel($scope.sessionTimer);
        }
    });
    // Add this to your sessions.controller.js
    $scope.testAIFunctionality = function() {
        console.log('Testing AI functionality...');
        
        var testData = {
            subject: 'Mathematics',
            duration: 25,
            goals: ['Solve algebra problems', 'Review calculus concepts']
        };
        
        NotificationService.info('Testing AI study plan generation...');
        
        ApiService.generateStudyPlan(testData).then(function(response) {
            console.log('AI response:', response.data);
            
            if (response.data) {
                if (response.data.ai_mode === 'real') {
                    NotificationService.success('✅ AI is working with real responses!');
                } else {
                    NotificationService.warning('⚠️ AI is working in mock mode');
                }
                
                // Display the generated plan
                $scope.showAITestResult(response.data);
            }
        }).catch(function(error) {
            console.error('AI test failed:', error);
            NotificationService.error('❌ AI functionality test failed');
        });
    };

    $scope.showAITestResult = function(plan) {
        var resultMessage = '';
        
        if (plan.study_blocks && plan.study_blocks.length > 0) {
            resultMessage += 'Study blocks generated: ' + plan.study_blocks.length + '\n';
        }
        
        if (plan.focus_techniques && plan.focus_techniques.length > 0) {
            resultMessage += 'Focus techniques: ' + plan.focus_techniques.length + '\n';
        }
        
        if (plan.ai_mode) {
            resultMessage += 'AI Mode: ' + plan.ai_mode + '\n';
        }
    
    alert('AI Test Results:\n\n' + resultMessage);
};

    // Initialize
    $scope.loadSessions();
}]);
