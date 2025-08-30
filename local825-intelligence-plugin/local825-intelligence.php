<?php
/**
 * Plugin Name: Local 825 Intelligence System
 * Plugin URI: https://datapilotplus.com
 * Description: Comprehensive intelligence dashboard for Local 825 Operating Engineers with real-time monitoring, company tracking, AI-powered insights, and automated blog post generation.
 * Version: 1.23.0
 * Author: DataPilotPlus Intelligence Division
 * Author URI: https://datapilotplus.com
 * License: GPL v2 or later
 * Text Domain: local825-intelligence
 * Domain Path: /languages
 */

if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('LOCAL825_PLUGIN_VERSION', '1.23.0');
define('LOCAL825_PLUGIN_URL', plugin_dir_url(__FILE__));
define('LOCAL825_PLUGIN_PATH', plugin_dir_path(__FILE__));

class Local825IntelligencePlugin {
    
    private $mcp_server_url;
    private $api_key;
    private $last_update;
    private $intelligence_data;
    private $logger;
    private $usage_stats;
    
    public function __construct() {
        // Auto-connect to Railway MCP server - no configuration needed!
        $this->mcp_server_url = 'https://trustworthy-solace-production.up.railway.app';
        $this->api_key = ''; // No API key needed for now
        $this->last_update = get_option('local825_last_update', '');
        $this->intelligence_data = get_option('local825_intelligence_data', array());
        
        $this->init();
    }
    
    public function init() {
        // Initialize plugin
        add_action('init', array($this, 'init_plugin'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('wp_ajax_local825_refresh_intelligence', array($this, 'ajax_refresh_intelligence'));
        add_action('wp_ajax_local825_get_company_data', array($this, 'ajax_get_company_data'));
        add_action('wp_ajax_local825_update_company_status', array($this, 'ajax_update_company_status'));
        add_action('wp_ajax_local825_export_report', array($this, 'ajax_export_report'));
        add_action('wp_ajax_local825_generate_ai_post', array($this, 'ajax_generate_ai_post'));
        add_action('wp_ajax_local825_run_company_analysis', array($this, 'ajax_run_company_analysis'));
        
        // Dashboard widget
        add_action('wp_dashboard_setup', array($this, 'add_dashboard_widget'));
        
        // Cron jobs for automatic updates
        add_action('local825_intelligence_update', array($this, 'cron_update_intelligence'));
        add_action('local825_company_tracking_update', array($this, 'cron_update_company_tracking'));
        add_action('local825_ai_insights_generation', array($this, 'cron_generate_ai_insights'));
        add_action('local825_company_profiles_daily', array($this, 'cron_generate_company_profiles'));
        
        // Custom post types
        add_action('init', array($this, 'register_custom_post_types'));
        
        // Register activation/deactivation hooks
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
        
        // Load text domain
        load_plugin_textdomain('local825-intelligence', false, dirname(plugin_basename(__FILE__)) . '/languages');
    }
    
    public function init_plugin() {
        // Set up cron schedules
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
    }
    
    public function register_custom_post_types() {
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
    }
    
    public function add_admin_menu() {
        // Main menu
        add_menu_page(
            'Local 825 Intelligence',
            'Local 825 Intel',
            'manage_options',
            'local825-intelligence',
            array($this, 'admin_page'),
            'dashicons-chart-area',
            30
        );
        
        // Submenus
        add_submenu_page(
            'local825-intelligence',
            'Dashboard',
            'Dashboard',
            'manage_options',
            'local825-intelligence',
            array($this, 'admin_page')
        );
        
        add_submenu_page(
            'local825-intelligence',
            'Company Tracking',
            'Company Tracking',
            'manage_options',
            'local825-company-tracking',
            array($this, 'company_tracking_page')
        );
        
        add_submenu_page(
            'local825-intelligence',
            'AI Insights',
            'AI Insights',
            'manage_options',
            'local825-ai-insights',
            array($this, 'ai_insights_page')
        );
        
        add_submenu_page(
            'local825-intelligence',
            'Reports',
            'Reports',
            'manage_options',
            'local825-reports',
            array($this, 'reports_page')
        );
        
        add_submenu_page(
            'local825-intelligence',
            'System Logs',
            'System Logs',
            'manage_options',
            'local825-logs',
            array($this, 'system_logs_page')
        );
    }
    
    public function admin_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/dashboard.php';
    }
    
    public function company_tracking_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/company-tracking.php';
    }
    
    public function ai_insights_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/ai-insights.php';
    }
    
    public function reports_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/reports.php';
    }
    
    public function system_logs_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/system-logs.php';
    }
    
    public function add_dashboard_widget() {
        wp_add_dashboard_widget(
            'local825_intelligence_widget',
            'Local 825 Intelligence Dashboard',
            array($this, 'dashboard_widget_content')
        );
    }
    
    public function dashboard_widget_content() {
        include LOCAL825_PLUGIN_PATH . 'admin/dashboard-widget.php';
    }
    
    // AJAX handlers
    public function ajax_refresh_intelligence() {
        check_ajax_referer('local825_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die('Unauthorized');
        }
        
        $result = $this->update_intelligence_data();
        
        if ($result['success']) {
            wp_send_json_success($result['data']);
        } else {
            wp_send_json_error($result['message']);
        }
    }
    
    public function ajax_get_company_data() {
        check_ajax_referer('local825_nonce', 'nonce');
        
        $company_data = $this->get_company_data();
        wp_send_json_success($company_data);
    }
    
    public function ajax_update_company_status() {
        check_ajax_referer('local825_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die('Unauthorized');
        }
        
        $company_id = sanitize_text_field($_POST['company_id']);
        $status = sanitize_text_field($_POST['status']);
        $notes = sanitize_textarea_field($_POST['notes']);
        
        $company_data = $this->get_company_data();
        
        if (isset($company_data[$company_id])) {
            $company_data[$company_id]['status'] = $status;
            $company_data[$company_id]['notes'] = $notes;
            $company_data[$company_id]['last_updated'] = current_time('mysql');
            
            update_option('local825_company_data', $company_data);
            wp_send_json_success('Company status updated');
        } else {
            wp_send_json_error('Company not found');
        }
    }
    
    public function ajax_export_report() {
        check_ajax_referer('local825_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die('Unauthorized');
        }
        
        $report_data = $this->generate_export_report();
        
        header('Content-Type: application/json');
        header('Content-Disposition: attachment; filename="local825_intelligence_report_' . date('Y-m-d') . '.json"');
        echo json_encode($report_data, JSON_PRETTY_PRINT);
        exit;
    }
    
    public function ajax_generate_ai_post() {
        check_ajax_referer('local825_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die('Unauthorized');
        }
        
        $result = $this->generate_ai_insight_post();
        
        if ($result['success']) {
            wp_send_json_success($result['data']);
        } else {
            wp_send_json_error($result['message']);
        }
    }
    
    public function ajax_run_company_analysis() {
        check_ajax_referer('local825_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die('Unauthorized');
        }
        
        $result = $this->generate_company_profile_post();
        
        if ($result['success']) {
            wp_send_json_success($result['data']);
        } else {
            wp_send_json_error($result['message']);
        }
    }
    
    // Core intelligence methods
    public function update_intelligence_data() {
        try {
            // Call MCP server for latest intelligence data
            $response = wp_remote_get($this->mcp_server_url . '/data', array(
                'headers' => array(
                    'User-Agent' => 'Local825-WordPress-Plugin/1.23.0'
                ),
                'timeout' => 30
            ));
            
            if (is_wp_error($response)) {
                return array(
                    'success' => false,
                    'message' => 'Failed to connect to MCP server: ' . $response->get_error_message()
                );
            }
            
            $status_code = wp_remote_retrieve_response_code($response);
            if ($status_code !== 200) {
                return array(
                    'success' => false,
                    'message' => 'MCP server returned status code: ' . $status_code
                );
            }
            
            $body = wp_remote_retrieve_body($response);
            $data = json_decode($body, true);
            
            if (!$data) {
                return array(
                    'success' => false,
                    'message' => 'Invalid response from MCP server'
                );
            }
            
            // Update local data
            $this->intelligence_data = $data;
            update_option('local825_intelligence_data', $data);
            update_option('local825_last_update', current_time('mysql'));
            
            // Log the update
            $this->log_system_event('intelligence_update', 'Intelligence data updated successfully', $data);
            
            return array(
                'success' => true,
                'data' => $data,
                'message' => 'Intelligence data updated successfully'
            );
            
        } catch (Exception $e) {
            $this->log_system_event('intelligence_update_error', 'Error updating intelligence data: ' . $e->getMessage());
            return array(
                'success' => false,
                'message' => 'Error updating intelligence data: ' . $e->getMessage()
            );
        }
    }
    
    public function generate_ai_insight_post() {
        try {
            // Get latest intelligence data
            $intelligence_data = $this->get_intelligence_data();
            
            if (empty($intelligence_data['articles'])) {
                return array(
                    'success' => false,
                    'message' => 'No intelligence data available for analysis'
                );
            }
            
            // Analyze articles for Local 825 relevance
            $relevant_articles = array_filter($intelligence_data['articles'], function($article) {
                return $article['relevance_score'] >= 80 || 
                       strpos($article['jurisdiction'], 'Local 825') !== false ||
                       strpos($article['category'], 'Construction') !== false;
            });
            
            if (empty($relevant_articles)) {
                return array(
                    'success' => false,
                    'message' => 'No relevant articles found for Local 825'
                );
            }
            
            // Generate AI-powered insight post
            $post_title = 'Local 825 Intelligence Update - ' . date('M j, Y');
            $post_content = $this->generate_insight_content($relevant_articles);
            
            // Create the post
            $post_data = array(
                'post_title' => $post_title,
                'post_content' => $post_content,
                'post_status' => 'publish',
                'post_type' => 'local825_intelligence',
                'post_author' => get_current_user_id(),
                'meta_input' => array(
                    'local825_insight_type' => 'ai_generated',
                    'local825_articles_analyzed' => count($relevant_articles),
                    'local825_generated_at' => current_time('mysql')
                )
            );
            
            $post_id = wp_insert_post($post_data);
            
            if (is_wp_error($post_id)) {
                throw new Exception('Failed to create post: ' . $post_id->get_error_message());
            }
            
            // Add jurisdiction taxonomy
            $jurisdictions = array_unique(array_column($relevant_articles, 'jurisdiction'));
            wp_set_object_terms($post_id, $jurisdictions, 'intelligence_jurisdiction');
            
            // Check for company mentions and add tags
            $company_mentions = $this->extract_company_mentions($post_content);
            if (!empty($company_mentions)) {
                wp_set_post_tags($post_id, $company_mentions);
            }
            
            $this->log_system_event('ai_insight_generated', 'AI insight post generated successfully', array(
                'post_id' => $post_id,
                'articles_analyzed' => count($relevant_articles)
            ));
            
            return array(
                'success' => true,
                'data' => array(
                    'post_id' => $post_id,
                    'post_title' => $post_title,
                    'post_url' => get_permalink($post_id)
                ),
                'message' => 'AI insight post generated successfully'
            );
            
        } catch (Exception $e) {
            $this->log_system_event('ai_insight_error', 'Error generating AI insight: ' . $e->getMessage());
            return array(
                'success' => false,
                'message' => 'Error generating AI insight: ' . $e->getMessage()
            );
        }
    }
    
    public function generate_company_profile_post() {
        try {
            // Get company data from MCP server
            $response = wp_remote_get($this->mcp_server_url . '/companies', array(
                'headers' => array(
                    'User-Agent' => 'Local825-WordPress-Plugin/1.23.0'
                ),
                'timeout' => 30
            ));
            
            if (is_wp_error($response)) {
                throw new Exception('Failed to connect to MCP server: ' . $response->get_error_message());
            }
            
            $companies_data = json_decode(wp_remote_retrieve_body($response), true);
            
            if (empty($companies_data)) {
                return array(
                    'success' => false,
                    'message' => 'No company data available'
                );
            }
            
            $generated_posts = array();
            
            foreach ($companies_data as $company_id => $company) {
                // Check if company post already exists
                $existing_post = get_posts(array(
                    'post_type' => 'local825_company',
                    'meta_query' => array(
                        array(
                            'key' => 'local825_company_id',
                            'value' => $company_id,
                            'compare' => '='
                        )
                    ),
                    'posts_per_page' => 1
                ));
                
                if (!empty($existing_post)) {
                    // Update existing post
                    $post_id = $existing_post[0]->ID;
                    $post_data = array(
                        'ID' => $post_id,
                        'post_title' => $company['name'],
                        'post_content' => $this->generate_company_profile_content($company),
                        'post_status' => 'publish'
                    );
                    
                    wp_update_post($post_data);
                } else {
                    // Create new post
                    $post_data = array(
                        'post_title' => $company['name'],
                        'post_content' => $this->generate_company_profile_content($company),
                        'post_status' => 'publish',
                        'post_type' => 'local825_company',
                        'post_author' => get_current_user_id(),
                        'meta_input' => array(
                            'local825_company_id' => $company_id,
                            'local825_industry' => $company['industry'],
                            'local825_status' => $company['status'],
                            'local825_last_updated' => $company['last_updated'],
                            'local825_notes' => $company['notes']
                        )
                    );
                    
                    $post_id = wp_insert_post($post_data);
                    
                    if (is_wp_error($post_id)) {
                        continue; // Skip this company if post creation fails
                    }
                }
                
                // Set industry taxonomy
                if (!empty($company['industry'])) {
                    wp_set_object_terms($post_id, $company['industry'], 'company_industry');
                }
                
                $generated_posts[] = array(
                    'post_id' => $post_id,
                    'company_name' => $company['name'],
                    'post_url' => get_permalink($post_id)
                );
            }
            
            $this->log_system_event('company_profiles_generated', 'Company profile posts generated successfully', array(
                'posts_generated' => count($generated_posts)
            ));
            
            return array(
                'success' => true,
                'data' => array(
                    'posts_generated' => $generated_posts
                ),
                'message' => 'Company profile posts generated successfully'
            );
            
        } catch (Exception $e) {
            $this->log_system_event('company_profile_error', 'Error generating company profiles: ' . $e->getMessage());
            return array(
                'success' => false,
                'message' => 'Error generating company profiles: ' . $e->getMessage()
            );
        }
    }
    
    private function generate_insight_content($articles) {
        $content = '<div class="local825-intelligence-insight">';
        $content .= '<h2>🔍 Local 825 Intelligence Analysis</h2>';
        $content .= '<p><strong>Generated:</strong> ' . date('F j, Y \a\t g:i A') . '</p>';
        $content .= '<p><strong>Articles Analyzed:</strong> ' . count($articles) . '</p>';
        
        $content .= '<h3>📊 Executive Summary</h3>';
        $content .= '<p>This intelligence update provides key insights relevant to Local 825 Operating Engineers, construction industry trends, and strategic opportunities.</p>';
        
        // Group articles by jurisdiction
        $jurisdictions = array();
        foreach ($articles as $article) {
            $jurisdiction = $article['jurisdiction'];
            if (!isset($jurisdictions[$jurisdiction])) {
                $jurisdictions[$jurisdiction] = array();
            }
            $jurisdictions[$jurisdiction][] = $article;
        }
        
        foreach ($jurisdictions as $jurisdiction => $jurisdiction_articles) {
            $content .= '<h3>📍 ' . esc_html($jurisdiction) . ' Focus</h3>';
            $content .= '<p><strong>Key Articles:</strong> ' . count($jurisdiction_articles) . '</p>';
            
            foreach ($jurisdiction_articles as $article) {
                $content .= '<div class="article-insight">';
                $content .= '<h4>' . esc_html($article['title']) . '</h4>';
                $content .= '<p><strong>Source:</strong> ' . esc_html($article['source']) . ' | <strong>Relevance:</strong> ' . $article['relevance_score'] . '/100</p>';
                $content .= '<p>' . esc_html($article['summary']) . '</p>';
                if (!empty($article['url'])) {
                    $content .= '<p><a href="' . esc_url($article['url']) . '" target="_blank">Read Full Article →</a></p>';
                }
                $content .= '</div>';
            }
        }
        
        $content .= '<h3>🎯 Strategic Implications</h3>';
        $content .= '<p>Based on this analysis, Local 825 members should focus on:</p>';
        $content .= '<ul>';
        $content .= '<li>Monitoring construction projects in key jurisdictions</li>';
        $content .= '<li>Identifying partnership opportunities with mentioned companies</li>';
        $content .= '<li>Staying informed about industry trends and regulations</li>';
        $content .= '</ul>';
        
        $content .= '<h3>📈 Next Steps</h3>';
        $content .= '<p>Continue monitoring these sources for updates and consider reaching out to relevant companies for potential collaboration opportunities.</p>';
        
        $content .= '</div>';
        
        return $content;
    }
    
    private function generate_company_profile_content($company) {
        $content = '<div class="local825-company-profile">';
        $content .= '<h2>🏢 ' . esc_html($company['name']) . ' - Company Profile</h2>';
        $content .= '<p><strong>Last Updated:</strong> ' . esc_html($company['last_updated']) . '</p>';
        
        $content .= '<div class="company-overview">';
        $content .= '<h3>Company Overview</h3>';
        $content .= '<table class="company-details">';
        $content .= '<tr><td><strong>Industry:</strong></td><td>' . esc_html($company['industry']) . '</td></tr>';
        $content .= '<tr><td><strong>Status:</strong></td><td>' . esc_html($company['status']) . '</td></tr>';
        $content .= '<tr><td><strong>Source:</strong></td><td>' . esc_html($company['source']) . '</td></tr>';
        $content .= '</table>';
        $content .= '</div>';
        
        if (!empty($company['notes'])) {
            $content .= '<div class="company-notes">';
            $content .= '<h3>Notes & Analysis</h3>';
            $content .= '<p>' . esc_html($company['notes']) . '</p>';
            $content .= '</div>';
        }
        
        $content .= '<div class="local825-relevance">';
        $content .= '<h3>Local 825 Relevance</h3>';
        $content .= '<p>This company has been identified as relevant to Local 825 Operating Engineers based on:</p>';
        $content .= '<ul>';
        $content .= '<li>Industry alignment with construction and engineering</li>';
        $content .= '<li>Geographic presence in Local 825 jurisdictions</li>';
        $content .= '<li>Potential for partnership or employment opportunities</li>';
        $content .= '</ul>';
        $content .= '</div>';
        
        $content .= '<div class="monitoring-status">';
        $content .= '<h3>Monitoring Status</h3>';
        $content .= '<p><strong>Current Status:</strong> <span class="status-' . esc_attr($company['status']) . '">' . esc_html(ucfirst($company['status'])) . '</span></p>';
        $content .= '<p>This company is actively monitored by the DataPilotPlus Local 825 Intelligence System for updates and opportunities.</p>';
        $content .= '</div>';
        
        $content .= '</div>';
        
        return $content;
    }
    
    private function extract_company_mentions($content) {
        // Get tracked companies
        $companies = $this->get_company_data();
        $mentions = array();
        
        foreach ($companies as $company) {
            if (stripos($content, $company['name']) !== false) {
                $mentions[] = $company['name'];
            }
        }
        
        return $mentions;
    }
    
    public function get_intelligence_data() {
        return $this->intelligence_data;
    }
    
    public function get_company_data() {
        return get_option('local825_company_data', array());
    }
    
    public function get_last_update() {
        return $this->last_update ?: get_option('local825_last_update', '');
    }
    
    public function log_system_event($event_type, $message, $data = array()) {
        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'event_type' => $event_type,
            'message' => $message,
            'data' => $data,
            'user_id' => get_current_user_id()
        );
        
        $logs = get_option('local825_system_logs', array());
        $logs[] = $log_entry;
        
        // Keep only last 1000 log entries
        if (count($logs) > 1000) {
            $logs = array_slice($logs, -1000);
        }
        
        update_option('local825_system_logs', $logs);
    }
    
    public function get_system_logs($limit = 100) {
        $logs = get_option('local825_system_logs', array());
        return array_slice(array_reverse($logs), 0, $limit);
    }
    
    // Cron job handlers
    public function cron_update_intelligence() {
        $this->update_intelligence_data();
    }
    
    public function cron_update_company_tracking() {
        $this->update_company_data();
    }
    
    public function cron_generate_ai_insights() {
        $this->generate_ai_insight_post();
    }
    
    public function cron_generate_company_profiles() {
        $this->generate_company_profile_post();
    }
    
    public function update_company_data() {
        // This would update company data from MCP server
        // Implementation similar to update_intelligence_data()
    }
    
    public function generate_export_report() {
        $intelligence_data = $this->get_intelligence_data();
        $company_data = $this->get_company_data();
        $system_logs = $this->get_system_logs(100);
        
        return array(
            'export_date' => current_time('mysql'),
            'intelligence_data' => $intelligence_data,
            'company_data' => $company_data,
            'system_logs' => $system_logs,
            'plugin_version' => LOCAL825_PLUGIN_VERSION,
            'wordpress_version' => get_bloginfo('version')
        );
    }
    
    // Plugin activation/deactivation
    public function activate() {
        // Create default options
        add_option('local825_auto_update', '1');
        add_option('local825_intelligence_data', array());
        add_option('local825_company_data', array());
        add_option('local825_last_update', '');
        add_option('local825_system_logs', array());
        
        // Set up cron jobs
        wp_schedule_event(time(), 'every_5_minutes', 'local825_intelligence_update');
        wp_schedule_event(time(), 'daily', 'local825_company_tracking_update');
        wp_schedule_event(time(), 'every_10_minutes', 'local825_ai_insights_generation');
        wp_schedule_event(time(), 'daily', 'local825_company_profiles_daily');
        
        // Flush rewrite rules for custom post types
        flush_rewrite_rules();
    }
    
    public function deactivate() {
        // Clear cron jobs
        wp_clear_scheduled_hook('local825_intelligence_update');
        wp_clear_scheduled_hook('local825_company_tracking_update');
        wp_clear_scheduled_hook('local825_ai_insights_generation');
        wp_clear_scheduled_hook('local825_company_profiles_daily');
        
        // Flush rewrite rules
        flush_rewrite_rules();
    }
}

// Initialize plugin
new Local825IntelligencePlugin();

// Add custom cron intervals
add_filter('cron_schedules', function($schedules) {
    $schedules['every_5_minutes'] = array(
        'interval' => 300,
        'display' => 'Every 5 Minutes'
    );
    $schedules['every_10_minutes'] = array(
        'interval' => 600,
        'display' => 'Every 10 Minutes'
    );
    return $schedules;
});

// Enqueue admin scripts and styles
add_action('admin_enqueue_scripts', function($hook) {
    if (strpos($hook, 'local825') !== false) {
        wp_enqueue_script('local825-admin', LOCAL825_PLUGIN_URL . 'assets/js/admin.js', array('jquery'), LOCAL825_PLUGIN_VERSION, true);
        wp_enqueue_style('local825-admin', LOCAL825_PLUGIN_URL . 'assets/css/admin.css', array(), LOCAL825_PLUGIN_VERSION);

        wp_localize_script('local825-admin', 'local825_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('local825_nonce'),
            'strings' => array(
                'updating' => 'Updating intelligence data...',
                'success' => 'Intelligence data updated successfully!',
                'error' => 'Error updating intelligence data',
                'confirm_delete' => 'Are you sure you want to delete this item?',
                'generating_ai_post' => 'Generating AI insight post...',
                'generating_company_profile' => 'Generating company profile...'
            )
        ));
    }
});

// Enqueue dashboard widget scripts
add_action('admin_enqueue_scripts', function($hook) {
    if ($hook === 'index.php') {
        wp_enqueue_script('local825-dashboard', LOCAL825_PLUGIN_URL . 'assets/js/dashboard-widget.js', array('jquery'), LOCAL825_PLUGIN_VERSION, true);
        wp_enqueue_style('local825-dashboard', LOCAL825_PLUGIN_URL . 'assets/css/dashboard-widget.css', array(), LOCAL825_PLUGIN_VERSION);
    }
});
