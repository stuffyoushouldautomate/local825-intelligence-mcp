<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$intelligence_data = $plugin->get_intelligence_data();
$last_update = $plugin->get_last_update();

// Get recent AI-generated posts
$recent_ai_posts = get_posts(array(
    'post_type' => 'local825_intelligence',
    'meta_query' => array(
        array(
            'key' => 'local825_insight_type',
            'value' => 'ai_generated',
            'compare' => '='
        )
    ),
    'posts_per_page' => 10,
    'orderby' => 'date',
    'order' => 'DESC'
));
?>

<div class="wrap local825-admin">
    <h1 class="wp-heading-inline">
        <span class="dashicons dashicons-admin-generic" style="color: #d4af37;"></span>
        AI Insights & Automation
    </h1>
    
    <div class="local825-header-actions">
        <button id="generate-ai-insight" class="button button-primary">
            <span class="dashicons dashicons-admin-generic"></span>
            Generate AI Insight Now
        </button>
        <button id="run-company-analysis" class="button button-secondary">
            <span class="dashicons dashicons-building"></span>
            Run Company Analysis
        </button>
        <span class="last-update">
            Last Updated: <?php echo $last_update ? date('M j, Y g:i A', strtotime($last_update)) : 'Never'; ?>
        </span>
    </div>

    <!-- AI Automation Status -->
    <div class="local825-section">
        <h2>🤖 AI Automation Status</h2>
        
        <div class="automation-status-grid">
            <div class="status-card">
                <h3>Intelligence Updates</h3>
                <div class="status-indicator active">
                    <span class="dashicons dashicons-yes-alt"></span>
                    Active
                </div>
                <p>Runs every 5 minutes</p>
                <p><strong>Next Run:</strong> <?php echo wp_next_scheduled('local825_intelligence_update') ? date('M j, Y g:i A', wp_next_scheduled('local825_intelligence_update')) : 'Not scheduled'; ?></p>
            </div>
            
            <div class="status-card">
                <h3>AI Insights Generation</h3>
                <div class="status-indicator active">
                    <span class="dashicons dashicons-yes-alt"></span>
                    Active
                </div>
                <p>Runs every 10 minutes</p>
                <p><strong>Next Run:</strong> <?php echo wp_next_scheduled('local825_ai_insights_generation') ? date('M j, Y g:i A', wp_next_scheduled('local825_ai_insights_generation')) : 'Not scheduled'; ?></p>
            </div>
            
            <div class="status-card">
                <h3>Company Profiles</h3>
                <div class="status-indicator active">
                    <span class="dashicons dashicons-yes-alt"></span>
                    Active
                </div>
                <p>Runs daily</p>
                <p><strong>Next Run:</strong> <?php echo wp_next_scheduled('local825_company_profiles_daily') ? date('M j, Y g:i A', wp_next_scheduled('local825_company_profiles_daily')) : 'Not scheduled'; ?></p>
            </div>
            
            <div class="status-card">
                <h3>Company Tracking</h3>
                <div class="status-indicator active">
                    <span class="dashicons dashicons-yes-alt"></span>
                    Active
                </div>
                <p>Runs daily</p>
                <p><strong>Next Run:</strong> <?php echo wp_next_scheduled('local825_company_tracking_update') ? date('M j, Y g:i A', wp_next_scheduled('local825_company_tracking_update')) : 'Not scheduled'; ?></p>
            </div>
        </div>
    </div>

    <!-- Recent AI-Generated Posts -->
    <div class="local825-section">
        <h2>📝 Recent AI-Generated Insights</h2>
        
        <?php if (!empty($recent_ai_posts)): ?>
            <div class="ai-posts-grid">
                <?php foreach ($recent_ai_posts as $post): ?>
                    <div class="ai-post-card">
                        <div class="post-header">
                            <h3><?php echo esc_html($post->post_title); ?></h3>
                            <span class="post-date"><?php echo get_the_date('M j, Y g:i A', $post->ID); ?></span>
                        </div>
                        
                        <div class="post-meta">
                            <?php 
                            $articles_analyzed = get_post_meta($post->ID, 'local825_articles_analyzed', true);
                            $generated_at = get_post_meta($post->ID, 'local825_generated_at', true);
                            ?>
                            <span class="meta-item">
                                <strong>Articles Analyzed:</strong> <?php echo esc_html($articles_analyzed); ?>
                            </span>
                            <span class="meta-item">
                                <strong>Generated:</strong> <?php echo esc_html($generated_at); ?>
                            </span>
                        </div>
                        
                        <div class="post-excerpt">
                            <?php echo wp_trim_words($post->post_content, 30); ?>
                        </div>
                        
                        <div class="post-actions">
                            <a href="<?php echo get_permalink($post->ID); ?>" class="button button-small" target="_blank">
                                <span class="dashicons dashicons-external"></span>
                                View Post
                            </a>
                            <a href="<?php echo get_edit_post_link($post->ID); ?>" class="button button-small">
                                <span class="dashicons dashicons-edit"></span>
                                Edit
                            </a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="no-data">
                <p>No AI-generated insights yet. Click "Generate AI Insight Now" to create your first automated intelligence post.</p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Manual AI Generation -->
    <div class="local825-section">
        <h2>🎯 Manual AI Generation</h2>
        
        <div class="manual-generation-grid">
            <div class="generation-card">
                <h3>Generate AI Insight Post</h3>
                <p>Analyze current intelligence data and generate a comprehensive insight post for Local 825 members.</p>
                <button id="manual-generate-insight" class="button button-primary">
                    <span class="dashicons dashicons-admin-generic"></span>
                    Generate Insight Post
                </button>
                <div id="insight-generation-status" class="generation-status"></div>
            </div>
            
            <div class="generation-card">
                <h3>Generate Company Profiles</h3>
                <p>Analyze company data and create/update company profile posts with comprehensive insights.</p>
                <button id="manual-generate-profiles" class="button button-secondary">
                    <span class="dashicons dashicons-building"></span>
                    Generate Company Profiles
                </button>
                <div id="profile-generation-status" class="generation-status"></div>
            </div>
        </div>
    </div>

    <!-- AI Configuration -->
    <div class="local825-section">
        <h2>⚙️ AI Configuration</h2>
        
        <div class="ai-config-grid">
            <div class="config-card">
                <h3>Relevance Threshold</h3>
                <p>Minimum relevance score for articles to be included in AI insights.</p>
                <input type="number" id="relevance-threshold" value="80" min="0" max="100" class="regular-text">
                <p class="description">Articles with scores below this threshold will be filtered out.</p>
            </div>
            
            <div class="config-card">
                <h3>Insight Frequency</h3>
                <p>How often AI insights should be automatically generated.</p>
                <select id="insight-frequency" class="regular-text">
                    <option value="300">Every 5 minutes</option>
                    <option value="600">Every 10 minutes</option>
                    <option value="1800">Every 30 minutes</option>
                    <option value="3600">Every hour</option>
                </select>
                <p class="description">More frequent updates provide real-time insights but may generate more content.</p>
            </div>
            
            <div class="config-card">
                <h3>Content Quality</h3>
                <p>Target quality level for generated content.</p>
                <select id="content-quality" class="regular-text">
                    <option value="basic">Basic - Quick summaries</option>
                    <option value="standard" selected>Standard - Balanced insights</option>
                    <option value="comprehensive">Comprehensive - Detailed analysis</option>
                </select>
                <p class="description">Higher quality content takes longer to generate but provides more value.</p>
            </div>
        </div>
        
        <div class="config-actions">
            <button id="save-ai-config" class="button button-primary">
                <span class="dashicons dashicons-saved"></span>
                Save Configuration
            </button>
            <button id="reset-ai-config" class="button button-secondary">
                <span class="dashicons dashicons-rest-api"></span>
                Reset to Defaults
            </button>
        </div>
    </div>
</div>
