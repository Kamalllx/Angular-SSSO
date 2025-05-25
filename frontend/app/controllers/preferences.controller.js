angular.module('studyOrchestratorApp')
.controller('PreferencesController', ['$scope', 'ApiService', 'NotificationService',
function($scope, ApiService, NotificationService) {
    $scope.loading = true;
    $scope.preferences = {
        default_study_duration: 25,
        default_break_duration: 5,
        preferred_study_times: ['09:00', '14:00', '19:00'],
        distracting_websites: [],
        focus_techniques: [],
        notifications_enabled: true,
        auto_block_websites: true
    };
    
    $scope.defaultWebsites = [
        'facebook.com', 'twitter.com', 'youtube.com', 'instagram.com', 
        'reddit.com', 'tiktok.com', 'netflix.com', 'twitch.tv'
    ];
    
    $scope.defaultTechniques = [
        'Pomodoro Technique', 'Time blocking', 'Active recall', 
        'Spaced repetition', 'Feynman technique', 'Mind mapping'
    ];

    $scope.newWebsite = '';
    $scope.newTechnique = '';
    $scope.activeTab = 'general';

    $scope.loadPreferences = function() {
        $scope.loading = true;
        
        ApiService.getPreferences().then(function(response) {
            var data = response.data;
            
            // Handle both object and array responses
            if (Array.isArray(data)) {
                if (data.length > 0 && typeof data[0] === 'object') {
                    $scope.preferences = angular.merge($scope.preferences, data[0]);
                }
            } else if (typeof data === 'object' && data !== null) {
                $scope.preferences = angular.merge($scope.preferences, data);
            }
            
            // Ensure arrays are properly initialized
            $scope.preferences.distracting_websites = $scope.preferences.distracting_websites || [];
            $scope.preferences.focus_techniques = $scope.preferences.focus_techniques || [];
            $scope.preferences.preferred_study_times = $scope.preferences.preferred_study_times || ['09:00', '14:00', '19:00'];
            
        }).catch(function(error) {
            NotificationService.warning('Using default preferences');
            console.log('Preferences load error:', error);
        }).finally(function() {
            $scope.loading = false;
        });
    };

    $scope.savePreferences = function() {
        $scope.loading = true;
        
        ApiService.updatePreferences($scope.preferences).then(function(response) {
            NotificationService.success('Preferences saved successfully');
        }).catch(function(error) {
            NotificationService.error('Failed to save preferences');
            console.error('Save preferences error:', error);
        }).finally(function() {
            $scope.loading = false;
        });
    };

    $scope.addWebsite = function() {
        if (!$scope.newWebsite.trim()) {
            NotificationService.warning('Please enter a website URL');
            return;
        }

        var website = $scope.newWebsite.trim().toLowerCase();
        
        // Remove protocol if present
        website = website.replace(/^https?:\/\//, '').replace(/^www\./, '');
        
        if ($scope.preferences.distracting_websites.indexOf(website) === -1) {
            $scope.preferences.distracting_websites.push(website);
            $scope.newWebsite = '';
            NotificationService.success('Website added to block list');
        } else {
            NotificationService.warning('Website already in the list');
        }
    };

    $scope.removeWebsite = function(index) {
        if (index >= 0 && index < $scope.preferences.distracting_websites.length) {
            var website = $scope.preferences.distracting_websites[index];
            $scope.preferences.distracting_websites.splice(index, 1);
            NotificationService.success(`Removed ${website} from block list`);
        }
    };

    $scope.addDefaultWebsites = function() {
        var added = 0;
        $scope.defaultWebsites.forEach(function(website) {
            if ($scope.preferences.distracting_websites.indexOf(website) === -1) {
                $scope.preferences.distracting_websites.push(website);
                added++;
            }
        });
        
        if (added > 0) {
            NotificationService.success(`Added ${added} default websites to block list`);
        } else {
            NotificationService.info('All default websites are already in the list');
        }
    };

    $scope.clearWebsites = function() {
        if (confirm('Are you sure you want to clear all blocked websites?')) {
            $scope.preferences.distracting_websites = [];
            NotificationService.success('Cleared all blocked websites');
        }
    };

    $scope.addTechnique = function() {
        if (!$scope.newTechnique.trim()) {
            NotificationService.warning('Please enter a focus technique');
            return;
        }

        var technique = $scope.newTechnique.trim();
        
        if ($scope.preferences.focus_techniques.indexOf(technique) === -1) {
            $scope.preferences.focus_techniques.push(technique);
            $scope.newTechnique = '';
            NotificationService.success('Focus technique added');
        } else {
            NotificationService.warning('Technique already in the list');
        }
    };

    $scope.removeTechnique = function(index) {
        if (index >= 0 && index < $scope.preferences.focus_techniques.length) {
            var technique = $scope.preferences.focus_techniques[index];
            $scope.preferences.focus_techniques.splice(index, 1);
            NotificationService.success(`Removed "${technique}" from techniques list`);
        }
    };

    $scope.addDefaultTechniques = function() {
        var added = 0;
        $scope.defaultTechniques.forEach(function(technique) {
            if ($scope.preferences.focus_techniques.indexOf(technique) === -1) {
                $scope.preferences.focus_techniques.push(technique);
                added++;
            }
        });
        
        if (added > 0) {
            NotificationService.success(`Added ${added} default focus techniques`);
        } else {
            NotificationService.info('All default techniques are already in the list');
        }
    };

    $scope.resetToDefaults = function() {
        if (confirm('Are you sure you want to reset all preferences to defaults?')) {
            $scope.preferences = {
                default_study_duration: 25,
                default_break_duration: 5,
                preferred_study_times: ['09:00', '14:00', '19:00'],
                distracting_websites: angular.copy($scope.defaultWebsites),
                focus_techniques: angular.copy($scope.defaultTechniques),
                notifications_enabled: true,
                auto_block_websites: true
            };
            NotificationService.success('Preferences reset to defaults');
        }
    };

    $scope.exportPreferences = function() {
        var dataStr = JSON.stringify($scope.preferences, null, 2);
        var dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        var link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'study_preferences.json';
        link.click();
        
        NotificationService.success('Preferences exported successfully');
    };

    $scope.importPreferences = function(file) {
        if (!file) return;
        
        var reader = new FileReader();
        reader.onload = function(e) {
            try {
                var importedPrefs = JSON.parse(e.target.result);
                $scope.$apply(function() {
                    $scope.preferences = angular.merge($scope.preferences, importedPrefs);
                    NotificationService.success('Preferences imported successfully');
                });
            } catch (error) {
                NotificationService.error('Invalid preferences file');
            }
        };
        reader.readAsText(file);
    };

    $scope.setTab = function(tab) {
        $scope.activeTab = tab;
    };

    $scope.getDurationOptions = function() {
        return [15, 20, 25, 30, 45, 60, 90, 120];
    };

    $scope.getBreakDurationOptions = function() {
        return [5, 10, 15, 20, 30];
    };

    // Initialize
    $scope.loadPreferences();
}]);
