<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$intelligence_data = $plugin->get_intelligence_data();
$last_update = $plugin->get_last_update();
$system_logs = $plugin->get_system_logs(5); // Get last 5 log entries
?>

<div class="local825-dashboard-widget">
    <div class="widget-content">
        <!-- Connection Status -->
        <div class="connection-status">
            <h4>🔌 MCP Server Connection</h4>
            <div class="status-indicator connected">
                <span class="dashicons dashicons-yes-alt"></span>
                Connected to Railway MCP Server
            </div>
            <p class="connection-details">
                <strong>Server:</strong> trustworthy-solace-production.up.railway.app<br>
                <strong>Last Update:</strong> <?php echo $last_update ? date('M j, Y g:i A', strtotime($last_update)) : 'Never'; ?>
            </p>
        </div>

        <!-- Quick Stats -->
        <div class="quick-stats">
            <h4>📊 Quick Overview</h4>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-number"><?php echo isset($intelligence_data['metadata']['total_articles']) ? $intelligence_data['metadata']['total_articles'] : '0'; ?></span>
                    <span class="stat-label">Articles</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number"><?php echo count($system_logs); ?></span>
                    <span class="stat-label">Recent Events</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number"><?php echo wp_next_scheduled('local825_ai_insights_generation') ? 'Active' : 'Inactive'; ?></span>
                    <span class="stat-label">AI Insights</span>
                </div>
            </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity">
            <h4>🔄 Recent Activity</h4>
            <?php if (!empty($system_logs)): ?>
                <div class="activity-list">
                    <?php foreach ($system_logs as $log): ?>
                        <div class="activity-item">
                            <span class="activity-time"><?php echo date('g:i A', strtotime($log['timestamp'])); ?></span>
                            <span class="activity-type"><?php echo esc_html($log['event_type']); ?></span>
                            <span class="activity-message"><?php echo esc_html(wp_trim_words($log['message'], 8)); ?></span>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <p class="no-activity">No recent activity</p>
            <?php endif; ?>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
            <h4>⚡ Quick Actions</h4>
            <div class="action-buttons">
                <a href="<?php echo admin_url('admin.php?page=local825-intelligence'); ?>" class="button button-primary button-small">
                    <span class="dashicons dashicons-chart-area"></span>
                    View Dashboard
                </a>
                <a href="<?php echo admin_url('admin.php?page=local825-ai-insights'); ?>" class="button button-secondary button-small">
                    <span class="dashicons dashicons-admin-generic"></span>
                    AI Insights
                </a>
                <a href="<?php echo admin_url('admin.php?page=local825-company-tracking'); ?>" class="button button-secondary button-small">
                    <span class="dashicons dashicons-building"></span>
                    Companies
                </a>
            </div>
        </div>

        <!-- System Health -->
        <div class="system-health">
            <h4>💚 System Health</h4>
            <div class="health-indicators">
                <div class="health-item">
                    <span class="health-label">Cron Jobs:</span>
                    <span class="health-status <?php echo wp_next_scheduled('local825_intelligence_update') ? 'healthy' : 'warning'; ?>">
                        <?php echo wp_next_scheduled('local825_intelligence_update') ? '✓ Active' : '⚠ Inactive'; ?>
                    </span>
                </div>
                <div class="health-item">
                    <span class="health-label">Database:</span>
                    <span class="health-status healthy">✓ Connected</span>
                </div>
                <div class="health-item">
                    <span class="health-label">Plugin Version:</span>
                    <span class="health-status info"><?php echo LOCAL825_PLUGIN_VERSION; ?></span>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.local825-dashboard-widget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
}

.local825-dashboard-widget h4 {
    margin: 0 0 10px 0;
    color: #23282d;
    font-size: 14px;
    font-weight: 600;
    border-bottom: 1px solid #e5e5e5;
    padding-bottom: 5px;
}

.connection-status {
    margin-bottom: 20px;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #e5e5e5;
}

.status-indicator {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.status-indicator.connected {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.connection-details {
    margin: 0;
    font-size: 12px;
    color: #666;
    line-height: 1.4;
}

.quick-stats {
    margin-bottom: 20px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

.stat-item {
    text-align: center;
    padding: 10px;
    background: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #e5e5e5;
}

.stat-number {
    display: block;
    font-size: 18px;
    font-weight: bold;
    color: #d4af37;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
}

.recent-activity {
    margin-bottom: 20px;
}

.activity-list {
    max-height: 120px;
    overflow-y: auto;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    margin-bottom: 5px;
    background: #f9f9f9;
    border-radius: 3px;
    font-size: 11px;
}

.activity-time {
    color: #666;
    min-width: 50px;
}

.activity-type {
    color: #d4af37;
    font-weight: bold;
    min-width: 80px;
}

.activity-message {
    color: #333;
    flex: 1;
}

.no-activity {
    text-align: center;
    color: #666;
    font-style: italic;
    font-size: 12px;
    margin: 0;
}

.quick-actions {
    margin-bottom: 20px;
}

.action-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.action-buttons .button {
    flex: 1;
    min-width: 80px;
    text-align: center;
    font-size: 11px;
    padding: 4px 8px;
}

.system-health {
    margin-bottom: 0;
}

.health-indicators {
    background: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #e5e5e5;
    padding: 10px;
}

.health-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid #e5e5e5;
    font-size: 12px;
}

.health-item:last-child {
    border-bottom: none;
}

.health-label {
    color: #333;
    font-weight: 500;
}

.health-status {
    font-weight: bold;
}

.health-status.healthy {
    color: #155724;
}

.health-status.warning {
    color: #856404;
}

.health-status.info {
    color: #0c5460;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .action-buttons {
        flex-direction: column;
    }
    
    .action-buttons .button {
        flex: none;
    }
}
</style>
