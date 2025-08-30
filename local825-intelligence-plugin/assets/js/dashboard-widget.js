/**
 * Local 825 Intelligence Dashboard Widget JavaScript
 * Handles real-time updates and interactions for the admin dashboard widget
 */

jQuery(document).ready(function($) {
    
    // Auto-refresh widget data every 5 minutes
    setInterval(function() {
        refreshWidgetData();
    }, 5 * 60 * 1000);
    
    // Refresh widget data function
    function refreshWidgetData() {
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_get_widget_data',
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    updateWidgetDisplay(response.data);
                }
            },
            error: function() {
                console.log('Failed to refresh widget data');
            }
        });
    }
    
    // Update widget display with new data
    function updateWidgetDisplay(data) {
        // Update connection status
        if (data.connection_status) {
            $('.connection-status .status-indicator').removeClass('connected disconnected').addClass(data.connection_status);
            $('.connection-status .status-indicator').html(
                data.connection_status === 'connected' ? 
                '<span class="dashicons dashicons-yes-alt"></span> Connected to Railway MCP Server' :
                '<span class="dashicons dashicons-no-alt"></span> Disconnected from MCP Server'
            );
        }
        
        // Update last update time
        if (data.last_update) {
            $('.connection-details strong:last').next().text(data.last_update);
        }
        
        // Update article count
        if (data.total_articles !== undefined) {
            $('.stats-grid .stat-item:first-child .stat-number').text(data.total_articles);
        }
        
        // Update recent events count
        if (data.recent_events !== undefined) {
            $('.stats-grid .stat-item:nth-child(2) .stat-number').text(data.recent_events);
        }
        
        // Update AI insights status
        if (data.ai_insights_status !== undefined) {
            $('.stats-grid .stat-item:last-child .stat-number').text(data.ai_insights_status);
        }
        
        // Update recent activity
        if (data.recent_activity && data.recent_activity.length > 0) {
            var activityHtml = '';
            data.recent_activity.forEach(function(activity) {
                activityHtml += '<div class="activity-item">';
                activityHtml += '<span class="activity-time">' + activity.time + '</span>';
                activityHtml += '<span class="activity-type">' + activity.type + '</span>';
                activityHtml += '<span class="activity-message">' + activity.message + '</span>';
                activityHtml += '</div>';
            });
            $('.activity-list').html(activityHtml);
        }
        
        // Update system health
        if (data.system_health) {
            updateSystemHealth(data.system_health);
        }
    }
    
    // Update system health indicators
    function updateSystemHealth(health) {
        // Update cron jobs status
        if (health.cron_jobs !== undefined) {
            var cronStatus = $('.health-item:first-child .health-status');
            cronStatus.removeClass('healthy warning').addClass(health.cron_jobs ? 'healthy' : 'warning');
            cronStatus.html(health.cron_jobs ? '✓ Active' : '⚠ Inactive');
        }
        
        // Update database status
        if (health.database !== undefined) {
            var dbStatus = $('.health-item:nth-child(2) .health-status');
            dbStatus.removeClass('healthy warning').addClass(health.database ? 'healthy' : 'warning');
            dbStatus.html(health.database ? '✓ Connected' : '⚠ Disconnected');
        }
    }
    
    // Add click handlers for quick action buttons
    $('.action-buttons .button').on('click', function(e) {
        // Add loading state
        var $button = $(this);
        var originalText = $button.text();
        
        $button.prop('disabled', true).html('<span class="dashicons dashicons-update spin"></span> Loading...');
        
        // Re-enable after navigation
        setTimeout(function() {
            $button.prop('disabled', false).html(originalText);
        }, 1000);
    });
    
    // Add hover effects for activity items
    $('.activity-list').on('mouseenter', '.activity-item', function() {
        $(this).css('background-color', '#f0f0f0');
    }).on('mouseleave', '.activity-item', function() {
        $(this).css('background-color', '#f9f9f9');
    });
    
    // Add click handler for activity items to show more details
    $('.activity-list').on('click', '.activity-item', function() {
        var $item = $(this);
        var type = $item.find('.activity-type').text();
        var message = $item.find('.activity-message').text();
        var time = $item.find('.activity-time').text();
        
        // Show tooltip with full message
        showActivityTooltip($item, {
            type: type,
            message: message,
            time: time
        });
    });
    
    // Show activity tooltip
    function showActivityTooltip($element, data) {
        // Remove existing tooltips
        $('.activity-tooltip').remove();
        
        var tooltip = $('<div class="activity-tooltip">' +
            '<div class="tooltip-header">' +
            '<strong>' + data.type + '</strong> at ' + data.time +
            '</div>' +
            '<div class="tooltip-content">' + data.message + '</div>' +
            '</div>');
        
        $element.append(tooltip);
        
        // Position tooltip
        var elementPos = $element.offset();
        var elementHeight = $element.outerHeight();
        
        tooltip.css({
            position: 'absolute',
            top: elementPos.top + elementHeight + 5,
            left: elementPos.left,
            zIndex: 1000
        });
        
        // Auto-hide tooltip after 3 seconds
        setTimeout(function() {
            tooltip.fadeOut(300, function() {
                $(this).remove();
            });
        }, 3000);
    }
    
    // Add CSS for tooltip
    if (!$('#activity-tooltip-styles').length) {
        $('head').append('<style id="activity-tooltip-styles">' +
            '.activity-tooltip { ' +
            'background: #333; ' +
            'color: #fff; ' +
            'padding: 10px; ' +
            'border-radius: 4px; ' +
            'box-shadow: 0 2px 10px rgba(0,0,0,0.3); ' +
            'max-width: 300px; ' +
            'font-size: 12px; ' +
            'z-index: 1000; ' +
            '}' +
            '.activity-tooltip .tooltip-header { ' +
            'border-bottom: 1px solid #555; ' +
            'padding-bottom: 5px; ' +
            'margin-bottom: 5px; ' +
            '}' +
            '.activity-tooltip .tooltip-content { ' +
            'line-height: 1.4; ' +
            '}' +
            '.dashicons.spin { ' +
            'animation: spin 1s linear infinite; ' +
            '}' +
            '@keyframes spin { ' +
            '0% { transform: rotate(0deg); } ' +
            '100% { transform: rotate(360deg); } ' +
            '}' +
            '</style>');
    }
    
    // Add refresh button functionality
    $('.connection-status').on('click', function() {
        refreshWidgetData();
        
        // Show refresh indicator
        var $status = $(this).find('.status-indicator');
        var originalText = $status.html();
        
        $status.html('<span class="dashicons dashicons-update spin"></span> Refreshing...');
        
        setTimeout(function() {
            $status.html(originalText);
        }, 2000);
    });
    
    // Add hover effect for connection status
    $('.connection-status').hover(
        function() {
            $(this).css('cursor', 'pointer');
            $(this).find('.status-indicator').css('opacity', '0.8');
        },
        function() {
            $(this).css('cursor', 'default');
            $(this).find('.status-indicator').css('opacity', '1');
        }
    );
    
    // Initialize widget with current data
    refreshWidgetData();
    
    // Add error handling for failed AJAX requests
    $(document).ajaxError(function(event, xhr, settings, error) {
        if (settings.url.includes('local825_get_widget_data')) {
            console.log('Widget data refresh failed:', error);
            
            // Show error indicator in connection status
            $('.connection-status .status-indicator').removeClass('connected').addClass('disconnected');
            $('.connection-status .status-indicator').html(
                '<span class="dashicons dashicons-warning"></span> Connection Error'
            );
        }
    });
    
    // Add success handling for successful AJAX requests
    $(document).ajaxSuccess(function(event, xhr, settings) {
        if (settings.url.includes('local825_get_widget_data')) {
            // Reset connection status on successful refresh
            $('.connection-status .status-indicator').removeClass('disconnected').addClass('connected');
            $('.connection-status .status-indicator').html(
                '<span class="dashicons dashicons-yes-alt"></span> Connected to Railway MCP Server'
            );
        }
    });
    
});
