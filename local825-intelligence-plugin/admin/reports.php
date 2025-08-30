<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$intelligence_data = $plugin->get_intelligence_data();
$last_update = $plugin->get_last_update();
?>

<div class="wrap local825-admin">
    <h1 class="wp-heading-inline">
        <span class="dashicons dashicons-chart-line" style="color: #d4af37;"></span>
        Intelligence Reports
    </h1>
    
    <div class="local825-header-actions">
        <button id="refresh-intelligence" class="button button-primary">
            <span class="dashicons dashicons-update"></span>
            Refresh Intelligence Data
        </button>
        <button id="export-report" class="button button-secondary">
            <span class="dashicons dashicons-download"></span>
            Export Report
        </button>
        <span class="last-update">
            Last Updated: <?php echo $last_update ? date('M j, Y g:i A', strtotime($last_update)) : 'Never'; ?>
        </span>
    </div>

    <!-- Report Overview -->
    <div class="local825-section">
        <h2>Report Overview</h2>
        
        <?php if (!empty($intelligence_data)): ?>
            <div class="report-stats">
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
        <?php else: ?>
            <div class="no-data">
                <p>No intelligence data available. Click "Refresh Intelligence Data" to fetch the latest data from your MCP server.</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Intelligence Articles -->
    <?php if (!empty($intelligence_data) && !empty($intelligence_data['articles'])): ?>
        <div class="local825-section">
            <h2>Intelligence Articles</h2>
            
            <div class="intelligence-articles">
                <?php 
                $articles = $intelligence_data['articles'];
                usort($articles, function($a, $b) {
                    return ($b['relevance_score'] ?? 0) - ($a['relevance_score'] ?? 0);
                });
                ?>
                
                <?php foreach ($articles as $article): ?>
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
        </div>
    <?php endif; ?>

    <!-- Export Options -->
    <div class="local825-section">
        <h2>Export Options</h2>
        
        <div class="export-options">
            <div class="export-option">
                <h4>JSON Export</h4>
                <p>Export all intelligence data in JSON format for external analysis.</p>
                <button id="export-json" class="button button-secondary">
                    <span class="dashicons dashicons-download"></span>
                    Export JSON
                </button>
            </div>
            
            <div class="export-option">
                <h4>CSV Export</h4>
                <p>Export intelligence data in CSV format for spreadsheet analysis.</p>
                <button id="export-csv" class="button button-secondary">
                    <span class="dashicons dashicons-download"></span>
                    Export CSV
                </button>
            </div>
        </div>
    </div>
</div>
