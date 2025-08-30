<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$intelligence_data = $plugin->get_intelligence_data();
$last_update = get_option('local825_last_update', '');
$company_data = $plugin->get_company_data();
?>

<div class="wrap local825-admin">
    <h1 class="wp-heading-inline">
        <span class="dashicons dashicons-chart-area" style="color: #d4af37;"></span>
        Local 825 Intelligence Dashboard
    </h1>
    
    <div class="local825-header-actions">
        <button id="refresh-intelligence" class="button button-primary">
            <span class="dashicons dashicons-update"></span>
            Refresh Intelligence
        </button>
        <button id="export-report" class="button button-secondary">
            <span class="dashicons dashicons-download"></span>
            Export Report
        </button>
        <span class="last-update">
            Last Updated: <?php echo $last_update ? date('M j, Y g:i A', strtotime($last_update)) : 'Never'; ?>
        </span>
    </div>
    
    <!-- Auto-Connection Status -->
    <div class="local825-section">
        <div class="notice notice-info">
            <p>
                <strong>✅ Auto-Connected to MCP Server:</strong> 
                This plugin automatically connects to your Railway MCP server at 
                <code>https://trustworthy-solace-production.up.railway.app</code>. 
                No configuration needed!
            </p>
        </div>
    </div>

    <!-- Intelligence Overview -->
    <div class="local825-section">
        <h2>Intelligence Overview</h2>
        
        <?php if (!empty($intelligence_data)): ?>
            <div class="intelligence-stats">
                <div class="stat-card">
                    <div class="stat-number"><?php echo count($intelligence_data['articles'] ?? array()); ?></div>
                    <div class="stat-label">Total Articles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number"><?php echo count(array_filter($intelligence_data['articles'] ?? array(), function($a) { return $a['jurisdiction'] === 'New Jersey'; })); ?></div>
                    <div class="stat-label">NJ Focus</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number"><?php echo count(array_filter($intelligence_data['articles'] ?? array(), function($a) { return $a['jurisdiction'] === 'New York'; })); ?></div>
                    <div class="stat-label">NY Focus</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number"><?php echo count(array_filter($intelligence_data['articles'] ?? array(), function($a) { return $a['jurisdiction'] === 'Local 825 Specific'; })); ?></div>
                    <div class="stat-label">Local 825 Specific</div>
                </div>
            </div>

            <!-- Top Articles -->
            <div class="intelligence-articles">
                <h3>Top Intelligence Stories</h3>
                <?php 
                $articles = $intelligence_data['articles'] ?? array();
                usort($articles, function($a, $b) {
                    return ($b['relevance_score'] ?? 0) - ($a['relevance_score'] ?? 0);
                });
                $top_articles = array_slice($articles, 0, 10);
                ?>
                
                <?php foreach ($top_articles as $article): ?>
                    <div class="article-card">
                        <div class="article-header">
                            <h4 class="article-title"><?php echo esc_html($article['title']); ?></h4>
                            <div class="article-meta">
                                <span class="article-source"><?php echo esc_html($article['source']); ?></span>
                                <span class="article-score">Score: <?php echo esc_html($article['relevance_score'] ?? 'N/A'); ?></span>
                                <span class="article-category"><?php echo esc_html($article['category'] ?? 'General'); ?></span>
                            </div>
                        </div>
                        <div class="article-details">
                            <span class="article-jurisdiction"><?php echo esc_html($article['jurisdiction']); ?></span>
                            <span class="article-date"><?php echo esc_html($article['published']); ?></span>
                            <?php if (!empty($article['url'])): ?>
                                <a href="<?php echo esc_url($article['url']); ?>" target="_blank" class="article-link">
                                    <span class="dashicons dashicons-external"></span>
                                    View Article
                                </a>
                            <?php endif; ?>
                        </div>
                        <?php if (!empty($article['summary'])): ?>
                            <div class="article-summary">
                                <?php echo esc_html(wp_trim_words($article['summary'], 30)); ?>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endforeach; ?>
            </div>

        <?php else: ?>
            <div class="no-data">
                <p>No intelligence data available. Click "Refresh Intelligence" to fetch the latest data.</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Company Tracking Overview -->
    <div class="local825-section">
        <h2>Company Tracking Overview</h2>
        
        <?php 
        $local825_companies = explode("\n", get_option('local825_local825_companies', ''));
        $local825_companies = array_filter(array_map('trim', $local825_companies));
        $general_companies = explode("\n", get_option('local825_general_companies', ''));
        $general_companies = array_filter(array_map('trim', $general_companies));
        $total_companies = count($local825_companies) + count($general_companies);
        ?>
        
        <?php if ($total_companies > 0): ?>
            <div class="company-stats">
                <div class="stat-card">
                    <div class="stat-number"><?php echo $total_companies; ?></div>
                    <div class="stat-label">Total Companies</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number"><?php echo count($local825_companies); ?></div>
                    <div class="stat-label">Local 825 Targets</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number"><?php echo count($general_companies); ?></div>
                    <div class="stat-label">General Companies</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number"><?php echo count(array_filter($company_data, function($c) { return $c['status'] === 'Signatory'; })); ?></div>
                    <div class="stat-label">Signatory</div>
                </div>
            </div>

            <!-- Local 825 Target Companies -->
            <?php if (!empty($local825_companies)): ?>
                <div class="company-category-section">
                    <h3>🏗️ Local 825 Target Companies (Primary Tracking)</h3>
                    <p>These are the specific companies Local 825 is actively monitoring and tracking for organizing efforts.</p>
                    
                    <div class="company-grid">
                        <?php foreach (array_slice($local825_companies, 0, 12) as $company): ?>
                            <div class="company-card target-company">
                                <div class="company-header">
                                    <h4 class="company-name"><?php echo esc_html($company); ?></h4>
                                    <span class="company-category">Primary Target</span>
                                </div>
                                <div class="company-location">
                                    <span class="dashicons dashicons-location"></span>
                                    NJ/NY Region
                                </div>
                                <div class="company-status-info">
                                    <strong>Status:</strong> 
                                    <span class="status-pending">Status Pending</span>
                                </div>
                                <div class="company-actions">
                                    <a href="<?php echo admin_url('admin.php?page=local825-company-tracking&company=' . sanitize_title($company)); ?>" class="button button-small">
                                        Update Status
                                    </a>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                    
                    <?php if (count($local825_companies) > 12): ?>
                        <div class="view-all-companies">
                            <a href="<?php echo admin_url('admin.php?page=local825-company-tracking'); ?>" class="button button-primary">
                                View All Local 825 Target Companies
                            </a>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <!-- General Construction Companies -->
            <?php if (!empty($general_companies)): ?>
                <div class="company-category-section">
                    <h3>🏢 General Construction Companies (Secondary Tracking)</h3>
                    <p>These companies provide industry context and may be of interest for broader market intelligence.</p>
                    
                    <div class="company-grid">
                        <?php foreach (array_slice($general_companies, 0, 12) as $company): ?>
                            <div class="company-card general-company">
                                <div class="company-header">
                                    <h4 class="company-name"><?php echo esc_html($company); ?></h4>
                                    <span class="company-category">Industry Context</span>
                                </div>
                                <div class="company-location">
                                    <span class="dashicons dashicons-location"></span>
                                    National/Regional
                                </div>
                                <div class="company-status-info">
                                    <strong>Focus:</strong> Market Intelligence
                                </div>
                                <div class="company-actions">
                                    <a href="<?php echo admin_url('admin.php?page=local825-company-tracking&company=' . sanitize_title($company)); ?>" class="button button-small">
                                        View Details
                                    </a>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                    
                    <?php if (count($general_companies) > 12): ?>
                        <div class="view-all-companies">
                            <a href="<?php echo admin_url('admin.php?page=local825-company-tracking'); ?>" class="button button-secondary">
                                View All General Companies
                            </a>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

        <?php else: ?>
            <div class="no-data">
                <p>No companies configured. Go to <strong>Local 825 Intel → Settings</strong> to set up company tracking.</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Quick Actions -->
    <div class="local825-section">
        <h2>Quick Actions</h2>
        <div class="quick-actions">
            <a href="<?php echo admin_url('admin.php?page=local825-company-tracking'); ?>" class="quick-action-card">
                <span class="dashicons dashicons-building"></span>
                <h3>Manage Companies</h3>
                <p>Update company status, add notes, and track changes</p>
            </a>
            <a href="<?php echo admin_url('admin.php?page=local825-reports'); ?>" class="quick-action-card">
                <span class="dashicons dashicons-analytics"></span>
                <h3>View Reports</h3>
                <p>Generate detailed intelligence and company reports</p>
            </a>
            <a href="<?php echo admin_url('admin.php?page=local825-settings'); ?>" class="quick-action-card">
                <span class="dashicons dashicons-admin-settings"></span>
                <h3>Plugin Settings</h3>
                <p>Configure MCP server, notifications, and auto-updates</p>
            </a>
        </div>
    </div>

    <!-- System Status -->
    <div class="local825-section">
        <h2>System Status</h2>
        <div class="system-status">
            <div class="status-item">
                <span class="status-label">MCP Server:</span>
                <span class="status-value <?php echo !empty($this->mcp_server_url) ? 'status-ok' : 'status-error'; ?>">
                    <?php echo !empty($this->mcp_server_url) ? 'Connected' : 'Not Configured'; ?>
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">API Key:</span>
                <span class="status-value <?php echo !empty($this->api_key) ? 'status-ok' : 'status-warning'; ?>">
                    <?php echo !empty($this->api_key) ? 'Configured' : 'Missing'; ?>
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Auto Updates:</span>
                <span class="status-value <?php echo get_option('local825_auto_update', '1') ? 'status-ok' : 'status-warning'; ?>">
                    <?php echo get_option('local825_auto_update', '1') ? 'Enabled' : 'Disabled'; ?>
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Notifications:</span>
                <span class="status-value <?php echo !empty(get_option('local825_notification_email')) ? 'status-ok' : 'status-warning'; ?>">
                    <?php echo !empty(get_option('local825_notification_email')) ? 'Configured' : 'Not Set'; ?>
                </span>
            </div>
        </div>
    </div>
</div>

<script>
jQuery(document).ready(function($) {
    // Refresh Intelligence
    $('#refresh-intelligence').on('click', function() {
        var $button = $(this);
        var originalText = $button.text();
        
        $button.prop('disabled', true).text('Refreshing...');
        
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_refresh_intelligence',
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Error: ' + response.data);
                }
            },
            error: function() {
                alert('Failed to refresh intelligence data');
            },
            complete: function() {
                $button.prop('disabled', false).text(originalText);
            }
        });
    });

    // Export Report
    $('#export-report').on('click', function() {
        var $button = $(this);
        var originalText = $button.text();
        
        $button.prop('disabled', true).text('Exporting...');
        
        $.ajax({
            url: local825_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'local825_export_report',
                nonce: local825_ajax.nonce
            },
            success: function(response) {
                // Create download link
                var blob = new Blob([JSON.stringify(response, null, 2)], {type: 'application/json'});
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'local825_intelligence_report_' + new Date().toISOString().split('T')[0] + '.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            },
            error: function() {
                alert('Failed to export report');
            },
            complete: function() {
                $button.prop('disabled', false).text(originalText);
            }
        });
    });
});
</script>
