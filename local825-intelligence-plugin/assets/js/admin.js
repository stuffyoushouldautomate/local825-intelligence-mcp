/**
 * Local 825 Intelligence Plugin - Admin JavaScript
 * Enhanced version with AI insights, company tracking, and system logging
 */

jQuery(document).ready(function($) {
    
    // Load Local 825 Target Companies
    $('#load-local825-target-companies').on('click', function() {
        var companies = [
            'Skanska USA',
            'Turner Construction',
            'Bechtel Corporation',
            'Fluor Corporation',
            'AECOM',
            'Kiewit Corporation',
            'Walsh Group',
            'Gilbane Building Company',
            'Balfour Beatty',
            'Clark Construction Group',
            'Hensel Phelps',
            'Suffolk Construction',
            'Brasfield & Gorrie',
            'McCarthy Building Companies',
            'DPR Construction',
            'Whiting-Turner Contracting',
            'Barton Malow',
            'JE Dunn Construction',
            'Mortenson Construction',
            'PCL Construction',
            'Webcor Builders',
            'Swinerton Builders',
            'Hunt Construction Group',
            'Robins & Morton',
            'Hoar Construction'
        ];
        
        $('#local825-companies').val(companies.join('\n'));
        showNotice('Local 825 target companies loaded!', 'success');
    });
    
    // Load General Construction Companies
    $('#load-general-companies').on('click', function() {
        var companies = [
            'Lendlease',
            'Brookfield Properties',
            'Related Companies',
            'Tishman Speyer',
            'Vornado Realty Trust',
            'SL Green Realty',
            'Boston Properties',
            'Hudson Pacific Properties',
            'Kilroy Realty Corporation',
            'Alexandria Real Estate Equities',
            'Crown Castle International',
            'American Tower Corporation',
            'Digital Realty Trust',
            'Equinix',
            'Iron Mountain',
            'Prologis',
            'Public Storage',
            'Extra Space Storage',
            'CubeSmart',
            'Life Storage'
        ];
        
        $('#general-companies').val(companies.join('\n'));
        showNotice('General construction companies loaded!', 'success');
    });
    
    // AI Insight Generation
    $('#generate-ai-insight, #manual-generate-insight').on('click', function() {
        var button = $(this);
        var originalText = button.text();
        
        button.text('Generating...').prop('disabled', true);
        showNotice('Generating AI insight post...', 'info');
        
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_generate_ai_post',
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    showNotice('AI insight post generated successfully!', 'success');
                    // Refresh the page to show the new post
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                } else {
                    showNotice('Failed to generate AI insight: ' + (response.data || 'Unknown error'), 'error');
                }
            },
            error: function() {
                showNotice('Failed to generate AI insight. Please try again.', 'error');
            },
            complete: function() {
                button.text(originalText).prop('disabled', false);
            }
        });
    });
    
    // Company Analysis
    $('#run-company-analysis, #manual-generate-profiles').on('click', function() {
        var button = $(this);
        var originalText = button.text();
        
        button.text('Analyzing...').prop('disabled', true);
        showNotice('Running company analysis...', 'info');
        
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_run_company_analysis',
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    showNotice('Company analysis completed successfully!', 'success');
                    // Refresh the page to show the new posts
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                } else {
                    showNotice('Failed to run company analysis: ' + (response.data || 'Unknown error'), 'error');
                }
            },
            error: function() {
                showNotice('Failed to run company analysis. Please try again.', 'error');
            },
            complete: function() {
                button.text(originalText).prop('disabled', false);
            }
        });
    });
    
    // AI Configuration
    $('#save-ai-config').on('click', function() {
        var config = {
            relevance_threshold: $('#relevance-threshold').val(),
            insight_frequency: $('#insight-frequency').val(),
            content_quality: $('#content-quality').val()
        };
        
        // Save configuration to WordPress options
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_save_ai_config',
                config: config,
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    showNotice('AI configuration saved successfully!', 'success');
                } else {
                    showNotice('Failed to save configuration: ' + (response.data || 'Unknown error'), 'error');
                }
            },
            error: function() {
                showNotice('Failed to save configuration. Please try again.', 'error');
            }
        });
    });
    
    // System Logs
    $('#refresh-logs').on('click', function() {
        location.reload();
    });
    
    $('#export-logs').on('click', function() {
        showNotice('Export functionality coming soon!', 'info');
    });
    
    $('#clear-logs').on('click', function() {
        if (confirm('Are you sure you want to clear all system logs? This cannot be undone.')) {
            $.ajax({
                url: local825_ajax.ajax_url,
                type: 'POST',
                data: {
                    action: 'local825_clear_logs',
                    nonce: local825_ajax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        showNotice('System logs cleared successfully!', 'success');
                        setTimeout(function() {
                            location.reload();
                        }, 1000);
                    } else {
                        showNotice('Failed to clear logs: ' + (response.data || 'Unknown error'), 'error');
                    }
                },
                error: function() {
                    showNotice('Failed to clear logs. Please try again.', 'error');
                }
            });
        }
    });
    
    // Log Data Modal
    $('.view-log-data').on('click', function() {
        var logData = $(this).data('log-data');
        $('#log-data-content').text(JSON.stringify(logData, null, 2));
        $('#log-data-modal').show();
    });
    
    $('.close').on('click', function() {
        $('#log-data-modal').hide();
    });
    
    $(window).on('click', function(e) {
        if ($(e.target).is('#log-data-modal')) {
            $('#log-data-modal').hide();
        }
    });
    
    // Copy Log Entry
    $('.copy-log-entry').on('click', function() {
        var logEntry = $(this).data('log-entry');
        var textArea = document.createElement('textarea');
        textArea.value = JSON.stringify(logEntry, null, 2);
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        showNotice('Log entry copied to clipboard!', 'success');
    });
    
    // Log Filters
    $('#apply-filters').on('click', function() {
        var eventType = $('#filter-event-type').val();
        var dateRange = $('#filter-date-range').val();
        var search = $('#filter-search').val();
        
        // Apply filters to log table
        $('.log-entry').each(function() {
            var row = $(this);
            var show = true;
            
            // Event type filter
            if (eventType && !row.hasClass('log-' + eventType)) {
                show = false;
            }
            
            // Search filter
            if (search) {
                var message = row.find('td:nth-child(3)').text().toLowerCase();
                if (message.indexOf(search.toLowerCase()) === -1) {
                    show = false;
                }
            }
            
            row.toggle(show);
        });
        
        showNotice('Filters applied!', 'success');
    });
    
    $('#clear-filters').on('click', function() {
        $('#filter-event-type').val('');
        $('#filter-date-range').val('24');
        $('#filter-search').val('');
        $('.log-entry').show();
        showNotice('Filters cleared!', 'success');
    });
    
    // Real-time Monitoring
    var monitoringInterval;
    
    $('#start-monitoring').on('click', function() {
        var button = $(this);
        var stopButton = $('#stop-monitoring');
        
        button.prop('disabled', true);
        stopButton.prop('disabled', false);
        
        $('#live-logs').html('<p class="monitoring-status">Live monitoring active...</p>');
        
        // Start polling for new logs
        monitoringInterval = setInterval(function() {
            $.ajax({
                url: local825_ajax.ajax_url,
                type: 'POST',
                data: {
                    action: 'local825_get_recent_logs',
                    nonce: local825_ajax.nonce
                },
                success: function(response) {
                    if (response.success && response.data.length > 0) {
                        var newLogs = '';
                        response.data.forEach(function(log) {
                            newLogs += '<div class="live-log-entry">';
                            newLogs += '<span class="log-time">' + log.timestamp + '</span>';
                            newLogs += '<span class="log-type">' + log.event_type + '</span>';
                            newLogs += '<span class="log-message">' + log.message + '</span>';
                            newLogs += '</div>';
                        });
                        
                        $('#live-logs').prepend(newLogs);
                        
                        // Keep only last 50 entries
                        var entries = $('#live-logs .live-log-entry');
                        if (entries.length > 50) {
                            entries.slice(50).remove();
                        }
                    }
                }
            });
        }, 5000); // Poll every 5 seconds
        
        showNotice('Live monitoring started!', 'success');
    });
    
    $('#stop-monitoring').on('click', function() {
        var button = $(this);
        var startButton = $('#start-monitoring');
        
        button.prop('disabled', true);
        startButton.prop('disabled', false);
        
        if (monitoringInterval) {
            clearInterval(monitoringInterval);
        }
        
        $('#live-logs').html('<p class="monitoring-status">Live monitoring stopped.</p>');
        showNotice('Live monitoring stopped!', 'info');
    });
    
    // Export Functions
    $('#export-json').on('click', function() {
        exportLogs('json');
    });
    
    $('#export-csv').on('click', function() {
        exportLogs('csv');
    });
    
    $('#export-text').on('click', function() {
        exportLogs('text');
    });
    
    function exportLogs(format) {
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_export_logs',
                format: format,
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    // Create download link
                    var blob = new Blob([response.data], { type: 'text/plain' });
                    var url = window.URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url;
                    a.download = 'local825_logs_' + new Date().toISOString().slice(0, 10) + '.' + format;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    showNotice('Logs exported successfully!', 'success');
                } else {
                    showNotice('Failed to export logs: ' + (response.data || 'Unknown error'), 'error');
                }
            },
            error: function() {
                showNotice('Failed to export logs. Please try again.', 'error');
            }
        });
    }
    
    // Update company preview
    function updateCompanyPreview() {
        var local825Element = $('#local825-companies');
        var generalElement = $('#general-companies');
        var local825Preview = $('#local825-companies-preview');
        var generalPreview = $('#general-companies-preview');
        
        // Only update if elements exist
        if (local825Element.length && local825Preview.length) {
            var local825Companies = local825Element.val().split('\n').filter(function(company) {
                return company.trim() !== '';
            });
            local825Preview.html('<ul><li>' + local825Companies.join('</li><li>') + '</li></ul>');
        }
        
        if (generalElement.length && generalPreview.length) {
            var generalCompanies = generalElement.val().split('\n').filter(function(company) {
                return company.trim() !== '';
            });
            generalPreview.html('<ul><li>' + generalCompanies.join('</li><li>') + '</li></ul>');
        }
    }
    
    // Show notice
    function showNotice(message, type) {
        var noticeClass = type === 'success' ? 'notice-success' : 
                         type === 'error' ? 'notice-error' : 
                         type === 'info' ? 'notice-info' : 'notice-warning';
        var notice = $('<div class="notice ' + noticeClass + ' is-dismissible"><p>' + message + '</p></div>');
        
        $('.local825-admin').prepend(notice);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            notice.fadeOut();
        }, 5000);
    }
    
    // Initialize company preview only if we're on the company tracking page
    if ($('#local825-companies').length || $('#general-companies').length) {
        updateCompanyPreview();
        
        // Update preview on input change
        $('#local825-companies, #general-companies').on('input', function() {
            updateCompanyPreview();
        });
    }
    
});
