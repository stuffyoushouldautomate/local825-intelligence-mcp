<?php
/**
 * Local 825 Intelligence Plugin - Installation Script
 * Handles plugin activation, deactivation, and database setup
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Plugin activation hook
 */
function local825_intelligence_activate() {
    global $wpdb;
    
    // Create default options
    $default_settings = array(
        'local825_auto_update' => '1',
        'local825_intelligence_data' => array(),
        'local825_company_data' => array(),
        'local825_last_update' => '',
        'local825_system_logs' => array(),
        'local825_ai_config' => array(
            'relevance_threshold' => 80,
            'insight_frequency' => 600, // 10 minutes
            'content_quality' => 'standard'
        )
    );
    
    foreach ($default_settings as $option_name => $default_value) {
        if (get_option($option_name) === false) {
            add_option($option_name, $default_value);
        }
    }
    
    // Set up cron jobs
    if (!wp_next_scheduled('local825_intelligence_update')) {
        wp_schedule_event(time(), 'every_5_minutes', 'local825_intelligence_update');
    }
    
    if (!wp_next_scheduled('local825_company_tracking_update')) {
        wp_schedule_event(time(), 'daily', 'local825_company_tracking_update');
    }
    
    if (!wp_next_scheduled('local825_ai_insights_generation')) {
        wp_schedule_event(time(), 'every_10_minutes', 'local825_ai_insights_generation');
    }
    
    if (!wp_next_scheduled('local825_company_profiles_daily')) {
        wp_schedule_event(time(), 'daily', 'local825_company_profiles_daily');
    }
    
    // Flush rewrite rules for custom post types
    flush_rewrite_rules();
    
    // Create initial system log entry
    $initial_logs = array(
        array(
            'timestamp' => current_time('mysql'),
            'event_type' => 'plugin_activated',
            'message' => 'Local 825 Intelligence Plugin activated successfully',
            'data' => array(
                'version' => LOCAL825_PLUGIN_VERSION,
                'wordpress_version' => get_bloginfo('version'),
                'php_version' => PHP_VERSION
            ),
            'user_id' => get_current_user_id()
        )
    );
    
    update_option('local825_system_logs', $initial_logs);
    
    // Create sample company data if none exists
    $existing_company_data = get_option('local825_company_data', array());
    if (empty($existing_company_data)) {
        $sample_companies = array(
            'skanska' => array(
                'name' => 'Skanska USA',
                'industry' => 'Construction',
                'status' => 'active',
                'last_updated' => current_time('mysql'),
                'notes' => 'Major construction company in Local 825 jurisdiction - monitored by DataPilotPlus'
            ),
            'turner' => array(
                'name' => 'Turner Construction',
                'industry' => 'Construction',
                'status' => 'active',
                'last_updated' => current_time('mysql'),
                'notes' => 'Leading construction management company - tracked for Local 825 opportunities'
            ),
            'bechtel' => array(
                'name' => 'Bechtel Corporation',
                'industry' => 'Construction & Engineering',
                'status' => 'active',
                'last_updated' => current_time('mysql'),
                'notes' => 'Global engineering and construction company - Local 825 jurisdiction monitoring'
            )
        );
        
        update_option('local825_company_data', $sample_companies);
    }
    
    // Create initial intelligence data structure
    $initial_intelligence = array(
        'articles' => array(
            array(
                'title' => 'DataPilotPlus Local 825 Intelligence System Launch',
                'source' => 'DataPilotPlus Intelligence',
                'published' => current_time('mysql'),
                'summary' => 'DataPilotPlus has successfully launched the Local 825 Intelligence System, providing real-time monitoring and strategic insights for Local 825 Operating Engineers.',
                'jurisdiction' => 'Local 825 Specific',
                'relevance_score' => 95,
                'category' => 'System Launch',
                'url' => 'https://datapilotplus.com'
            )
        ),
        'metadata' => array(
            'total_articles' => 1,
            'last_updated' => current_time('mysql'),
            'data_source' => 'DataPilotPlus System'
        )
    );
    
    update_option('local825_intelligence_data', $initial_intelligence);
    update_option('local825_last_update', current_time('mysql'));
    
    // Create custom post types and taxonomies
    local825_create_custom_post_types();
    
    // Create sample intelligence post
    local825_create_sample_intelligence_post();
    
    // Create sample company posts
    local825_create_sample_company_posts();
}

/**
 * Plugin deactivation hook
 */
function local825_intelligence_deactivate() {
    // Clear cron jobs
    wp_clear_scheduled_hook('local825_intelligence_update');
    wp_clear_scheduled_hook('local825_company_tracking_update');
    wp_clear_scheduled_hook('local825_ai_insights_generation');
    wp_clear_scheduled_hook('local825_company_profiles_daily');
    
    // Flush rewrite rules
    flush_rewrite_rules();
    
    // Log deactivation
    $logs = get_option('local825_system_logs', array());
    $logs[] = array(
        'timestamp' => current_time('mysql'),
        'event_type' => 'plugin_deactivated',
        'message' => 'Local 825 Intelligence Plugin deactivated',
        'data' => array(),
        'user_id' => get_current_user_id()
    );
    
    update_option('local825_system_logs', $logs);
}

/**
 * Plugin uninstall hook
 */
function local825_intelligence_uninstall() {
    // Remove all plugin options
    $options_to_remove = array(
        'local825_auto_update',
        'local825_intelligence_data',
        'local825_company_data',
        'local825_last_update',
        'local825_system_logs',
        'local825_ai_config'
    );
    
    foreach ($options_to_remove as $option) {
        delete_option($option);
    }
    
    // Remove all custom post types and their content
    local825_remove_custom_post_types();
    
    // Clear any remaining cron jobs
    wp_clear_scheduled_hook('local825_intelligence_update');
    wp_clear_scheduled_hook('local825_company_tracking_update');
    wp_clear_scheduled_hook('local825_ai_insights_generation');
    wp_clear_scheduled_hook('local825_company_profiles_daily');
}

/**
 * Create custom post types and taxonomies
 */
function local825_create_custom_post_types() {
    // Register Company custom post type
    register_post_type('local825_company', array(
        'labels' => array(
            'name' => 'Companies',
            'singular_name' => 'Company',
            'add_new' => 'Add New Company',
            'add_new_item' => 'Add New Company',
            'edit_item' => 'Edit Company',
            'new_item' => 'New Company',
            'view_item' => 'View Company',
            'search_items' => 'Search Companies',
            'not_found' => 'No companies found',
            'not_found_in_trash' => 'No companies found in trash'
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'menu_icon' => 'dashicons-building',
        'rewrite' => array('slug' => 'companies'),
        'show_in_rest' => true
    ));
    
    // Register Intelligence custom post type
    register_post_type('local825_intelligence', array(
        'labels' => array(
            'name' => 'Intelligence',
            'singular_name' => 'Intelligence',
            'add_new' => 'Add New Intelligence',
            'add_new_item' => 'Add New Intelligence',
            'edit_item' => 'Edit Intelligence',
            'new_item' => 'New Intelligence',
            'view_item' => 'View Intelligence',
            'search_items' => 'Search Intelligence',
            'not_found' => 'No intelligence found',
            'not_found_in_trash' => 'No intelligence found in trash'
        ),
        'public' => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'menu_icon' => 'dashicons-chart-area',
        'rewrite' => array('slug' => 'intelligence'),
        'show_in_rest' => true
    ));
    
    // Register custom taxonomies
    register_taxonomy('company_industry', 'local825_company', array(
        'labels' => array(
            'name' => 'Industries',
            'singular_name' => 'Industry',
            'search_items' => 'Search Industries',
            'all_items' => 'All Industries',
            'parent_item' => 'Parent Industry',
            'parent_item_colon' => 'Parent Industry:',
            'edit_item' => 'Edit Industry',
            'update_item' => 'Update Industry',
            'add_new_item' => 'Add New Industry',
            'new_item_name' => 'New Industry Name',
            'menu_name' => 'Industries'
        ),
        'hierarchical' => true,
        'show_ui' => true,
        'show_admin_column' => true,
        'query_var' => true,
        'rewrite' => array('slug' => 'industry')
    ));
    
    register_taxonomy('intelligence_jurisdiction', 'local825_intelligence', array(
        'labels' => array(
            'name' => 'Jurisdictions',
            'singular_name' => 'Jurisdiction',
            'search_items' => 'Search Jurisdictions',
            'all_items' => 'All Jurisdictions',
            'edit_item' => 'Edit Jurisdiction',
            'update_item' => 'Update Jurisdiction',
            'add_new_item' => 'Add New Jurisdiction',
            'new_item_name' => 'New Jurisdiction Name',
            'menu_name' => 'Jurisdictions'
        ),
        'hierarchical' => false,
        'show_ui' => true,
        'show_admin_column' => true,
        'query_var' => true,
        'rewrite' => array('slug' => 'jurisdiction')
    ));
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

/**
 * Create sample intelligence post
 */
function local825_create_sample_intelligence_post() {
    // Check if sample post already exists
    $existing_posts = get_posts(array(
        'post_type' => 'local825_intelligence',
        'meta_query' => array(
            array(
                'key' => 'local825_sample_post',
                'value' => '1',
                'compare' => '='
            )
        ),
        'posts_per_page' => 1
    ));
    
    if (empty($existing_posts)) {
        $post_data = array(
            'post_title' => 'Welcome to Local 825 Intelligence System',
            'post_content' => '<div class="local825-intelligence-insight">
                <h2>🔍 Welcome to Local 825 Intelligence</h2>
                <p>This is your new Local 825 Intelligence System powered by DataPilotPlus. The system will automatically:</p>
                <ul>
                    <li>Monitor construction industry news and developments</li>
                    <li>Track relevant companies and opportunities</li>
                    <li>Generate AI-powered insights and analysis</li>
                    <li>Create comprehensive reports for Local 825 members</li>
                </ul>
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Visit the AI Insights page to generate your first automated intelligence post</li>
                    <li>Check the Company Tracking page to manage target companies</li>
                    <li>Review the System Logs to monitor automation status</li>
                    <li>Customize settings in the AI Configuration section</li>
                </ol>
                <p>The system is now actively monitoring and will generate insights every 10 minutes based on relevant intelligence data.</p>
            </div>',
            'post_status' => 'publish',
            'post_type' => 'local825_intelligence',
            'post_author' => get_current_user_id(),
            'meta_input' => array(
                'local825_sample_post' => '1',
                'local825_insight_type' => 'welcome',
                'local825_generated_at' => current_time('mysql')
            )
        );
        
        $post_id = wp_insert_post($post_data);
        
        if (!is_wp_error($post_id)) {
            // Add jurisdiction taxonomy
            wp_set_object_terms($post_id, 'Local 825 Specific', 'intelligence_jurisdiction');
        }
    }
}

/**
 * Create sample company posts
 */
function local825_create_sample_company_posts() {
    $sample_companies = array(
        'Skanska USA' => array(
            'industry' => 'Construction',
            'notes' => 'Major construction company in Local 825 jurisdiction - monitored by DataPilotPlus'
        ),
        'Turner Construction' => array(
            'industry' => 'Construction',
            'notes' => 'Leading construction management company - tracked for Local 825 opportunities'
        ),
        'Bechtel Corporation' => array(
            'industry' => 'Construction & Engineering',
            'notes' => 'Global engineering and construction company - Local 825 jurisdiction monitoring'
        )
    );
    
    foreach ($sample_companies as $company_name => $company_data) {
        // Check if company post already exists
        $existing_posts = get_posts(array(
            'post_type' => 'local825_company',
            'title' => $company_name,
            'posts_per_page' => 1
        ));
        
        if (empty($existing_posts)) {
            $post_data = array(
                'post_title' => $company_name,
                'post_content' => '<div class="local825-company-profile">
                    <h2>🏢 ' . esc_html($company_name) . ' - Company Profile</h2>
                    <p><strong>Last Updated:</strong> ' . current_time('mysql') . '</p>
                    
                    <div class="company-overview">
                        <h3>Company Overview</h3>
                        <table class="company-details">
                            <tr><td><strong>Industry:</strong></td><td>' . esc_html($company_data['industry']) . '</td></tr>
                            <tr><td><strong>Status:</strong></td><td>Active</td></tr>
                            <tr><td><strong>Source:</strong></td><td>DataPilotPlus Intelligence</td></tr>
                        </table>
                    </div>
                    
                    <div class="company-notes">
                        <h3>Notes & Analysis</h3>
                        <p>' . esc_html($company_data['notes']) . '</p>
                    </div>
                    
                    <div class="local825-relevance">
                        <h3>Local 825 Relevance</h3>
                        <p>This company has been identified as relevant to Local 825 Operating Engineers based on:</p>
                        <ul>
                            <li>Industry alignment with construction and engineering</li>
                            <li>Geographic presence in Local 825 jurisdictions</li>
                            <li>Potential for partnership or employment opportunities</li>
                        </ul>
                    </div>
                    
                    <div class="monitoring-status">
                        <h3>Monitoring Status</h3>
                        <p><strong>Current Status:</strong> <span class="status-active">Active</span></p>
                        <p>This company is actively monitored by the DataPilotPlus Local 825 Intelligence System for updates and opportunities.</p>
                    </div>
                </div>',
                'post_status' => 'publish',
                'post_type' => 'local825_company',
                'post_author' => get_current_user_id(),
                'meta_input' => array(
                    'local825_sample_company' => '1',
                    'local825_industry' => $company_data['industry'],
                    'local825_status' => 'active',
                    'local825_last_updated' => current_time('mysql'),
                    'local825_notes' => $company_data['notes']
                )
            );
            
            $post_id = wp_insert_post($post_data);
            
            if (!is_wp_error($post_id)) {
                // Set industry taxonomy
                wp_set_object_terms($post_id, $company_data['industry'], 'company_industry');
            }
        }
    }
}

/**
 * Remove custom post types and their content
 */
function local825_remove_custom_post_types() {
    // Get all posts of custom post types
    $company_posts = get_posts(array(
        'post_type' => 'local825_company',
        'numberposts' => -1,
        'post_status' => 'any'
    ));
    
    $intelligence_posts = get_posts(array(
        'post_type' => 'local825_intelligence',
        'numberposts' => -1,
        'post_status' => 'any'
    ));
    
    // Delete all company posts
    foreach ($company_posts as $post) {
        wp_delete_post($post->ID, true);
    }
    
    // Delete all intelligence posts
    foreach ($intelligence_posts as $post) {
        wp_delete_post($post->ID, true);
    }
    
    // Remove taxonomies
    unregister_taxonomy('company_industry');
    unregister_taxonomy('intelligence_jurisdiction');
    
    // Remove post types
    unregister_post_type('local825_company');
    unregister_post_type('local825_intelligence');
}

/**
 * Add custom cron intervals
 */
function local825_add_cron_intervals($schedules) {
    $schedules['every_5_minutes'] = array(
        'interval' => 300,
        'display' => 'Every 5 Minutes'
    );
    $schedules['every_10_minutes'] = array(
        'interval' => 600,
        'display' => 'Every 10 Minutes'
    );
    return $schedules;
}

// Hook functions
add_action('init', 'local825_create_custom_post_types');
add_filter('cron_schedules', 'local825_add_cron_intervals');

// Register activation/deactivation hooks
register_activation_hook(__FILE__, 'local825_intelligence_activate');
register_deactivation_hook(__FILE__, 'local825_intelligence_deactivate');
register_uninstall_hook(__FILE__, 'local825_intelligence_uninstall');
