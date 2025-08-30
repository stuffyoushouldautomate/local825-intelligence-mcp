<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$system_logs = $plugin->get_system_logs(200); // Get last 200 log entries
?>

<div class="wrap local825-admin">
    <h1 class="wp-heading-inline">
        <span class="dashicons dashicons-list-view" style="color: #d4af37;"></span>
        System Logs & Monitoring
    </h1>
    
    <div class="local825-header-actions">
        <button id="refresh-logs" class="button button-primary">
            <span class="dashicons dashicons-update"></span>
            Refresh Logs
        </button>
        <button id="export-logs" class="button button-secondary">
            <span class="dashicons dashicons-download"></span>
            Export Logs
        </button>
        <button id="clear-logs" class="button button-secondary">
            <span class="dashicons dashicons-trash"></span>
            Clear Logs
        </button>
    </div>

    <!-- Log Statistics -->
    <div class="local825-section">
        <h2>📊 Log Statistics</h2>
        
        <?php
        $log_types = array();
        $error_count = 0;
        $success_count = 0;
        $info_count = 0;
        
        foreach ($system_logs as $log) {
            $event_type = $log['event_type'];
            if (!isset($log_types[$event_type])) {
                $log_types[$event_type] = 0;
            }
            $log_types[$event_type]++;
            
            if (strpos($event_type, 'error') !== false) {
                $error_count++;
            } elseif (strpos($event_type, 'success') !== false) {
                $success_count++;
            } else {
                $info_count++;
            }
        }
        ?>
        
        <div class="log-stats-grid">
            <div class="stat-card">
                <div class="stat-number"><?php echo count($system_logs); ?></div>
                <div class="stat-label">Total Log Entries</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number"><?php echo count($log_types); ?></div>
                <div class="stat-label">Event Types</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number"><?php echo $error_count; ?></div>
                <div class="stat-label">Errors</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number"><?php echo $success_count; ?></div>
                <div class="stat-label">Success</div>
            </div>
        </div>
        
        <!-- Event Type Breakdown -->
        <div class="event-breakdown">
            <h3>Event Type Breakdown</h3>
            <div class="event-chart">
                <?php foreach ($log_types as $event_type => $count): ?>
                    <div class="event-bar">
                        <div class="event-label"><?php echo esc_html($event_type); ?></div>
                        <div class="event-bar-container">
                            <div class="event-bar-fill" style="width: <?php echo ($count / max($log_types)) * 100; ?>%"></div>
                        </div>
                        <div class="event-count"><?php echo $count; ?></div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </div>

    <!-- Log Filters -->
    <div class="local825-section">
        <h2>🔍 Log Filters</h2>
        
        <div class="log-filters">
            <div class="filter-group">
                <label for="filter-event-type">Event Type:</label>
                <select id="filter-event-type" class="regular-text">
                    <option value="">All Event Types</option>
                    <?php foreach (array_keys($log_types) as $event_type): ?>
                        <option value="<?php echo esc_attr($event_type); ?>"><?php echo esc_html($event_type); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="filter-date-range">Date Range:</label>
                <select id="filter-date-range" class="regular-text">
                    <option value="1">Last Hour</option>
                    <option value="24" selected>Last 24 Hours</option>
                    <option value="168">Last Week</option>
                    <option value="720">Last Month</option>
                    <option value="all">All Time</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="filter-search">Search:</label>
                <input type="text" id="filter-search" class="regular-text" placeholder="Search log messages...">
            </div>
            
            <div class="filter-actions">
                <button id="apply-filters" class="button button-primary">Apply Filters</button>
                <button id="clear-filters" class="button button-secondary">Clear Filters</button>
            </div>
        </div>
    </div>

    <!-- System Logs Table -->
    <div class="local825-section">
        <h2>📋 System Logs</h2>
        
        <?php if (!empty($system_logs)): ?>
            <div class="logs-table-container">
                <table class="wp-list-table widefat fixed striped logs-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Event Type</th>
                            <th>Message</th>
                            <th>User</th>
                            <th>Data</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($system_logs as $log): ?>
                            <tr class="log-entry log-<?php echo esc_attr($log['event_type']); ?>">
                                <td>
                                    <?php echo esc_html($log['timestamp']); ?>
                                </td>
                                <td>
                                    <span class="event-type-badge event-<?php echo esc_attr($log['event_type']); ?>">
                                        <?php echo esc_html($log['event_type']); ?>
                                    </span>
                                </td>
                                <td>
                                    <?php echo esc_html($log['message']); ?>
                                </td>
                                <td>
                                    <?php 
                                    if (!empty($log['user_id'])) {
                                        $user = get_user_by('id', $log['user_id']);
                                        echo $user ? esc_html($user->display_name) : 'Unknown User';
                                    } else {
                                        echo 'System';
                                    }
                                    ?>
                                </td>
                                <td>
                                    <?php if (!empty($log['data'])): ?>
                                        <button class="button button-small view-log-data" data-log-data='<?php echo esc_attr(json_encode($log['data'])); ?>'>
                                            <span class="dashicons dashicons-visibility"></span>
                                            View Data
                                        </button>
                                    <?php else: ?>
                                        <span class="no-data">No data</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <button class="button button-small copy-log-entry" data-log-entry='<?php echo esc_attr(json_encode($log)); ?>'>
                                        <span class="dashicons dashicons-clipboard"></span>
                                        Copy
                                    </button>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            
            <!-- Pagination -->
            <div class="logs-pagination">
                <span class="pagination-info">
                    Showing <?php echo count($system_logs); ?> of <?php echo count($system_logs); ?> log entries
                </span>
                <div class="pagination-controls">
                    <button class="button button-secondary" disabled>Previous</button>
                    <span class="current-page">Page 1</span>
                    <button class="button button-secondary" disabled>Next</button>
                </div>
            </div>
            
        <?php else: ?>
            <div class="no-data">
                <p>No system logs available yet. Logs will appear here as the system runs and generates events.</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Real-time Monitoring -->
    <div class="local825-section">
        <h2>🔄 Real-time Monitoring</h2>
        
        <div class="monitoring-controls">
            <button id="start-monitoring" class="button button-primary">
                <span class="dashicons dashicons-controls-play"></span>
                Start Live Monitoring
            </button>
            <button id="stop-monitoring" class="button button-secondary" disabled>
                <span class="dashicons dashicons-controls-pause"></span>
                Stop Monitoring
            </button>
        </div>
        
        <div class="live-logs-container">
            <div id="live-logs" class="live-logs">
                <p class="monitoring-status">Live monitoring not active. Click "Start Live Monitoring" to begin.</p>
            </div>
        </div>
    </div>

    <!-- Log Export Options -->
    <div class="local825-section">
        <h2>📤 Export Options</h2>
        
        <div class="export-options">
            <div class="export-option">
                <h4>JSON Export</h4>
                <p>Export logs in JSON format for external analysis and processing.</p>
                <button id="export-json" class="button button-secondary">
                    <span class="dashicons dashicons-download"></span>
                    Export JSON
                </button>
            </div>
            
            <div class="export-option">
                <h4>CSV Export</h4>
                <p>Export logs in CSV format for spreadsheet analysis.</p>
                <button id="export-csv" class="button button-secondary">
                    <span class="dashicons dashicons-download"></span>
                    Export CSV
                </button>
            </div>
            
            <div class="export-option">
                <h4>Text Log</h4>
                <p>Export logs in traditional text log format.</p>
                <button id="export-text" class="button button-secondary">
                    <span class="dashicons dashicons-download"></span>
                    Export Text
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Log Data Modal -->
<div id="log-data-modal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Log Data Details</h3>
            <span class="close">&times;</span>
        </div>
        <div class="modal-body">
            <pre id="log-data-content"></pre>
        </div>
    </div>
</div>
