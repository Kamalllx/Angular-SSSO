angular.module('studyOrchestratorApp')
.controller('AnalyticsController', ['$scope', 'ApiService', 'NotificationService',
function($scope, ApiService, NotificationService) {
    $scope.loading = true;
    $scope.analytics = {
        weeklyStats: {},
        productivityTrends: {},
        subjectPerformance: {},
        focusInsights: {},
        recommendations: {}
    };
    $scope.chartData = {};
    
    $scope.timeFilter = 'week'; // week, month, year
    $scope.selectedSubject = 'all';
    $scope.subjects = [];

    $scope.loadAnalytics = function() {
        $scope.loading = true;
        
        ApiService.getAnalytics().then(function(response) {
            $scope.analytics = response.data;
            $scope.processAnalyticsData();
            $scope.createCharts();
        }).catch(function(error) {
            NotificationService.error('Failed to load analytics');
            console.error('Analytics error:', error);
        }).finally(function() {
            $scope.loading = false;
        });

        // Load sessions for subject filtering
        ApiService.getStudySessions().then(function(response) {
            var sessions = response.data || [];
            var subjectSet = new Set(['all']);
            sessions.forEach(function(session) {
                if (session.subject) {
                    subjectSet.add(session.subject);
                }
            });
            $scope.subjects = Array.from(subjectSet);
        });
    };

    $scope.processAnalyticsData = function() {
        // Process data for charts
        var stats = $scope.analytics.weekly_stats || {};
        
        $scope.chartData = {
            weeklyProgress: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                data: [2, 3, 1, 4, 2, 3, 2], // Mock data - replace with real data
                colors: ['#00f3ff']
            },
            focusDistribution: {
                labels: ['High Focus', 'Medium Focus', 'Low Focus'],
                data: [40, 35, 25],
                colors: ['#39ff14', '#ffff00', '#ff073a']
            },
            subjectBreakdown: {
                labels: ['Math', 'Programming', 'Science', 'Language'],
                data: [30, 25, 20, 25],
                colors: ['#00f3ff', '#39ff14', '#bf00ff', '#ff006e']
            }
        };
    };

    $scope.createCharts = function() {
        // Create weekly progress chart
        setTimeout(function() {
            var ctx1 = document.getElementById('weeklyProgressChart');
            if (ctx1) {
                new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: $scope.chartData.weeklyProgress.labels,
                        datasets: [{
                            label: 'Study Hours',
                            data: $scope.chartData.weeklyProgress.data,
                            borderColor: '#00f3ff',
                            backgroundColor: 'rgba(0, 243, 255, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            pointBackgroundColor: '#00f3ff',
                            pointBorderColor: '#00f3ff',
                            pointHoverBackgroundColor: '#ffffff',
                            pointHoverBorderColor: '#00f3ff'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#ffffff'
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    color: '#ffffff'
                                },
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                }
                            },
                            x: {
                                ticks: {
                                    color: '#ffffff'
                                },
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                }
                            }
                        }
                    }
                });
            }

            // Create focus distribution chart
            var ctx2 = document.getElementById('focusChart');
            if (ctx2) {
                new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: $scope.chartData.focusDistribution.labels,
                        datasets: [{
                            data: $scope.chartData.focusDistribution.data,
                            backgroundColor: $scope.chartData.focusDistribution.colors,
                            borderWidth: 2,
                            borderColor: '#0a0a0f'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    color: '#ffffff',
                                    padding: 20
                                }
                            }
                        }
                    }
                });
            }

            // Create subject breakdown chart
            var ctx3 = document.getElementById('subjectChart');
            if (ctx3) {
                new Chart(ctx3, {
                    type: 'bar',
                    data: {
                        labels: $scope.chartData.subjectBreakdown.labels,
                        datasets: [{
                            label: 'Study Time (hours)',
                            data: $scope.chartData.subjectBreakdown.data,
                            backgroundColor: $scope.chartData.subjectBreakdown.colors,
                            borderWidth: 1,
                            borderColor: $scope.chartData.subjectBreakdown.colors
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    color: '#ffffff'
                                },
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                }
                            },
                            x: {
                                ticks: {
                                    color: '#ffffff'
                                },
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                }
                            }
                        }
                    }
                });
            }
        }, 100);
    };

    $scope.changeTimeFilter = function(filter) {
        $scope.timeFilter = filter;
        $scope.loadAnalytics();
    };

    $scope.exportData = function() {
        // Create CSV export
        var csvContent = "data:text/csv;charset=utf-8,";
        csvContent += "Metric,Value\n";
        csvContent += `Total Sessions,${$scope.analytics.weekly_stats?.total_sessions || 0}\n`;
        csvContent += `Total Hours,${$scope.analytics.weekly_stats?.total_hours || 0}\n`;
        csvContent += `Average Focus,${$scope.analytics.weekly_stats?.avg_focus || 0}%\n`;
        csvContent += `Goals Completed,${$scope.analytics.weekly_stats?.total_goals_completed || 0}\n`;

        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "study_analytics.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        NotificationService.success('Analytics data exported successfully');
    };

    $scope.getRecommendationIcon = function(type) {
        switch(type) {
            case 'schedule': return 'fa-calendar';
            case 'break': return 'fa-pause';
            case 'environment': return 'fa-home';
            default: return 'fa-lightbulb';
        }
    };

    $scope.getInsightClass = function(type) {
        switch(type) {
            case 'improvement': return 'neon-orange';
            case 'warning': return 'neon-red';
            case 'success': return 'neon-green';
            default: return 'neon-blue';
        }
    };

    // Initialize
    $scope.loadAnalytics();
}]);
