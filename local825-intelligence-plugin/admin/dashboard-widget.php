<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$intelligence_data = $plugin->get_intelligence_data();
$last_update = get_option('local825_last_update', '');
$company_data = $plugin->get_company_data();
?>

<div class="local825-dashboard-widget">
    <!-- Header -->
    <div class="widget-header">
        <h3>Local 825 Intelligence</h3>
        <div class="widget-actions">
            <button class="refresh-btn" onclick="refreshLocal825Intelligence()">
                <span class="dashicons dashicons-update"></span>
            </button>
        </div>
    </div>

    <!-- Quick Stats -->
    <div class="widget-stats">
        <?php if (!empty($intelligence_data)): ?>
            <div class="stat-row">
                <div class="stat-item">
                    <span class="stat-number"><?php echo count($intelligence_data['articles'] ?? array()); ?></span>
                    <span class="stat-label">Articles</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number"><?php echo count($company_data); ?></span>
                    <span class="stat-label">Companies</span>
                </div>
            </div>
        <?php else: ?>
            <div class="no-data">
                <p>No data available</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Top Story -->
    <?php if (!empty($intelligence_data['articles'])): ?>
        <?php 
        $articles = $intelligence_data['articles'];
        usort($articles, function($a, $b) {
            return ($b['relevance_score'] ?? 0) - ($a['relevance_score'] ?? 0);
        });
        $top_article = $articles[0];
        ?>
        <div class="top-story">
            <h4>Top Story</h4>
            <div class="story-title"><?php echo esc_html(wp_trim_words($top_article['title'], 10)); ?></div>
            <div class="story-meta">
                <span class="story-source"><?php echo esc_html($top_article['source']); ?></span>
                <span class="story-score">Score: <?php echo esc_html($top_article['relevance_score'] ?? 'N/A'); ?></span>
            </div>
        </div>
    <?php endif; ?>

    <!-- Quick Actions -->
    <div class="widget-actions">
        <a href="<?php echo admin_url('admin.php?page=local825-intelligence'); ?>" class="button button-primary button-small">
            View Full Dashboard
        </a>
        <a href="<?php echo admin_url('admin.php?page=local825-company-tracking'); ?>" class="button button-secondary button-small">
            Company Tracking
        </a>
    </div>

    <!-- Last Update -->
    <?php if ($last_update): ?>
        <div class="last-update">
            <small>Last updated: <?php echo date('M j, g:i A', strtotime($last_update)); ?></small>
        </div>
    <?php endif; ?>
</div>

<script>
function refreshLocal825Intelligence() {
    var $btn = jQuery('.local825-dashboard-widget .refresh-btn');
    var $icon = $btn.find('.dashicons');
    
    $btn.prop('disabled', true);
    $icon.addClass('spin');
    
    jQuery.ajax({
        url: ajaxurl,
        type: 'POST',
        data: {
            action: 'local825_refresh_intelligence',
            nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>'
        },
        success: function(response) {
            if (response.success) {
                location.reload();
            } else {
                alert('Error refreshing data: ' + response.data);
            }
        },
        error: function() {
            alert('Failed to refresh intelligence data');
        },
        complete: function() {
            $btn.prop('disabled', false);
            $icon.removeClass('spin');
        }
    });
}

// Auto-refresh every 30 minutes
setInterval(function() {
    refreshLocal825Intelligence();
}, 30 * 60 * 1000);
</script>

<style>
.local825-dashboard-widget {
    padding: 12px;
}

.widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ddd;
}

.widget-header h3 {
    margin: 0;
    color: #1e3c72;
    font-size: 16px;
}

.refresh-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px;
    border-radius: 3px;
    transition: background-color 0.2s;
}

.refresh-btn:hover {
    background-color: #f0f0f0;
}

.refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.dashicons.spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.widget-stats {
    margin-bottom: 15px;
}

.stat-row {
    display: flex;
    gap: 15px;
}

.stat-item {
    flex: 1;
    text-align: center;
    padding: 10px;
    background: #f9f9f9;
    border-radius: 5px;
}

.stat-number {
    display: block;
    font-size: 20px;
    font-weight: bold;
    color: #1e3c72;
}

.stat-label {
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
}

.top-story {
    margin-bottom: 15px;
    padding: 10px;
    background: #f0f7ff;
    border-left: 3px solid #1e3c72;
    border-radius: 3px;
}

.top-story h4 {
    margin: 0 0 8px 0;
    font-size: 12px;
    color: #1e3c72;
    text-transform: uppercase;
}

.story-title {
    font-weight: 500;
    margin-bottom: 5px;
    line-height: 1.3;
}

.story-meta {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #666;
}

.widget-actions {
    display: flex;
    gap: 8px;
    margin-bottom: 15px;
}

.widget-actions .button {
    flex: 1;
    text-align: center;
    font-size: 11px;
    padding: 5px 8px;
}

.last-update {
    text-align: center;
    color: #666;
    font-style: italic;
}

.no-data {
    text-align: center;
    color: #666;
    font-style: italic;
    padding: 20px;
}
</style>
