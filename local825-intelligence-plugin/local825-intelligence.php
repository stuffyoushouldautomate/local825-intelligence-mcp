<?php
/**
 * Plugin Name: Local 825 Intelligence System
 * Plugin URI: https://local825.org
 * Description: Comprehensive intelligence dashboard for Local 825 Operating Engineers with real-time monitoring, company tracking, and strategic insights.
 * Version: 1.0.0
 * Author: Local 825 Intelligence Division
 * Author URI: https://local825.org
 * License: GPL v2 or later
 * Text Domain: local825-intelligence
 * Domain Path: /languages
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('LOCAL825_PLUGIN_VERSION', '1.0.0');
define('LOCAL825_PLUGIN_URL', plugin_dir_url(__FILE__));
define('LOCAL825_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('LOCAL825_PLUGIN_BASENAME', plugin_basename(__FILE__));

// Main plugin class
class Local825IntelligencePlugin {
    
    private $mcp_server_url;
    private $api_key;
    private $last_update;
    private $intelligence_data;
    
    public function __construct() {
        $this->mcp_server_url = get_option('local825_mcp_server_url', 'https://your-railway-app.railway.app');
        $this->api_key = get_option('local825_api_key', '');
        $this->last_update = get_option('local825_last_update', '');
        $this->intelligence_data = get_option('local825_intelligence_data', array());
        
        $this->init();
    }
    
    public function init() {
        // Initialize plugin
        add_action('init', array($this, 'init_plugin'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'admin_init'));
        add_action('wp_ajax_local825_refresh_intelligence', array($this, 'ajax_refresh_intelligence'));
        add_action('wp_ajax_local825_get_company_data', array($this, 'ajax_get_company_data'));
        add_action('wp_ajax_local825_update_company_status', array($this, 'ajax_update_company_status'));
        add_action('wp_ajax_local825_export_report', array($this, 'ajax_export_report'));
        add_action('wp_ajax_local825_save_local825_companies', array($this, 'ajax_save_local825_companies'));
        add_action('wp_ajax_local825_save_general_companies', array($this, 'ajax_save_general_companies'));
        add_action('wp_ajax_local825_test_mcp_connection', array($this, 'ajax_test_mcp_connection'));
        add_action('wp_ajax_local825_export_settings', array($this, 'ajax_export_settings'));
        add_action('wp_ajax_local825_import_settings', array($this, 'ajax_import_settings'));
        add_action('wp_ajax_local825_reset_settings', array($this, 'ajax_reset_settings'));
        
        // Dashboard widget
        add_action('wp_dashboard_setup', array($this, 'add_dashboard_widget'));
        
        // Cron jobs for automatic updates
        add_action('local825_intelligence_update', array($this, 'cron_update_intelligence'));
        add_action('local825_company_tracking_update', array($this, 'cron_update_company_tracking'));
        
        // Register activation/deactivation hooks
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
        
        // Load text domain
        load_plugin_textdomain('local825-intelligence', false, dirname(plugin_basename(__FILE__)) . '/languages');
    }
    
    public function init_plugin() {
        // Set up cron schedules
        if (!wp_next_scheduled('local825_intelligence_update')) {
            wp_schedule_event(time(), 'hourly', 'local825_intelligence_update');
        }
        
        if (!wp_next_scheduled('local825_company_tracking_update')) {
            wp_schedule_event(time(), 'daily', 'local825_company_tracking_update');
        }
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
            'Settings',
            'Settings',
            'manage_options',
            'local825-settings',
            array($this, 'settings_page')
        );
        
        add_submenu_page(
            'local825-intelligence',
            'Reports',
            'Reports',
            'manage_options',
            'local825-reports',
            array($this, 'reports_page')
        );
    }
    
    public function admin_init() {
        // Register settings
        register_setting('local825_settings', 'local825_mcp_server_url');
        register_setting('local825_settings', 'local825_api_key');
        register_setting('local825_settings', 'local825_auto_update');
        register_setting('local825_settings', 'local825_notification_email');
        register_setting('local825_settings', 'local825_company_list');
        
        // Add settings sections
        add_settings_section(
            'local825_general_settings',
            'General Settings',
            array($this, 'general_settings_section'),
            'local825-settings'
        );
        
        add_settings_section(
            'local825_mcp_settings',
            'MCP Server Settings',
            array($this, 'mcp_settings_section'),
            'local825-settings'
        );
        
        add_settings_section(
            'local825_company_settings',
            'Company Tracking Settings',
            array($this, 'company_settings_section'),
            'local825-settings'
        );
        
        // Add settings fields
        add_settings_field(
            'local825_mcp_server_url',
            'MCP Server URL',
            array($this, 'mcp_server_url_field'),
            'local825-settings',
            'local825_mcp_settings'
        );
        
        add_settings_field(
            'local825_api_key',
            'API Key',
            array($this, 'api_key_field'),
            'local825-settings',
            'local825_mcp_settings'
        );
        
        add_settings_field(
            'local825_auto_update',
            'Auto Update',
            array($this, 'auto_update_field'),
            'local825-settings',
            'local825_general_settings'
        );
        
        add_settings_field(
            'local825_notification_email',
            'Notification Email',
            array($this, 'notification_email_field'),
            'local825-settings',
            'local825_general_settings'
        );
    }
    
    public function admin_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/dashboard.php';
    }
    
    public function company_tracking_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/company-tracking.php';
    }
    
    public function settings_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/settings.php';
    }
    
    public function reports_page() {
        include LOCAL825_PLUGIN_PATH . 'admin/reports.php';
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
        
        $company_data = get_option('local825_company_data', array());
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
        
        $company_data = get_option('local825_company_data', array());
        
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
    
    // Core intelligence methods
    public function update_intelligence_data() {
        try {
            // Call MCP server for latest intelligence
            $response = wp_remote_get($this->mcp_server_url . '/intelligence', array(
                'headers' => array(
                    'Authorization' => 'Bearer ' . $this->api_key,
                    'User-Agent' => 'Local825-WordPress-Plugin/1.0'
                ),
                'timeout' => 30
            ));
            
            if (is_wp_error($response)) {
                return array(
                    'success' => false,
                    'message' => 'Failed to connect to MCP server: ' . $response->get_error_message()
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
            
            // Send notification if enabled
            if (get_option('local825_notification_email')) {
                $this->send_intelligence_notification($data);
            }
            
            return array(
                'success' => true,
                'data' => $data,
                'message' => 'Intelligence data updated successfully'
            );
            
        } catch (Exception $e) {
            return array(
                'success' => false,
                'message' => 'Error updating intelligence data: ' . $e->getMessage()
            );
        }
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
    
    /**
     * Manual method to test logging and get usage statistics
     * Can be called from CLI or admin interface
     */
    public function test_logging() {
        $this->logger->log('info', '=== LOGGING TEST START ===');
        
        // Simulate some API calls
        $this->logger->log_api_call('test_service', '/test', ['response_code' => 200]);
        $this->logger->log_api_call('test_service', '/status', ['response_code' => 200]);
        
        // Simulate token usage (OpenAI, etc.)
        $this->logger->log_token_usage('openai_gpt4', 1500, 0.03); // $0.03 per 1K tokens
        $this->logger->log_token_usage('openai_gpt35', 800, 0.002); // $0.002 per 1K tokens
        
        // Simulate service usage
        $this->logger->log_service_usage('google_news_api', [
            'queries' => 5,
            'articles_found' => 25,
            'filtered_results' => 18
        ]);
        
        $this->logger->log_service_usage('rss_scraper', [
            'feeds_processed' => 8,
            'articles_scraped' => 42,
            'processing_time' => '2.3s'
        ]);
        
        // Log final stats
        $this->logger->log_final_usage_stats();
        
        return $this->logger->get_usage_stats();
    }
    
    /**
     * Get current usage statistics
     */
    public function get_usage_statistics() {
        return $this->logger->get_usage_stats();
    }
    
    /**
     * Reset usage statistics
     */
    public function reset_usage_statistics() {
        $this->logger->reset_usage_stats();
        $this->logger->log('info', 'Usage statistics reset');
    }
    
    public function update_company_tracking() {
        // Update company tracking data from MCP server
        try {
            $response = wp_remote_get($this->mcp_server_url . '/companies', array(
                'headers' => array(
                    'Authorization' => 'Bearer ' . $this->api_key,
                    'User-Agent' => 'Local825-WordPress-Plugin/1.0'
                ),
                'timeout' => 30
            ));
            
            if (!is_wp_error($response)) {
                $body = wp_remote_retrieve_body($response);
                $company_data = json_decode($body, true);
                
                if ($company_data) {
                    update_option('local825_company_data', $company_data);
                }
            }
        } catch (Exception $e) {
            error_log('Local 825: Failed to update company tracking: ' . $e->getMessage());
        }
    }
    
    public function generate_export_report() {
        $intelligence_data = $this->get_intelligence_data();
        $company_data = $this->get_company_data();
        
        return array(
            'export_date' => current_time('mysql'),
            'intelligence_data' => $intelligence_data,
            'company_data' => $company_data,
            'plugin_version' => LOCAL825_PLUGIN_VERSION,
            'wordpress_version' => get_bloginfo('version')
        );
    }
    
    public function send_intelligence_notification($data) {
        $to = get_option('local825_notification_email');
        $subject = 'Local 825 Intelligence Update - ' . date('Y-m-d H:i:s');
        
        $message = "Local 825 Intelligence Update\n\n";
        $message .= "New intelligence data has been received:\n";
        $message .= "- Total Articles: " . count($data['articles'] ?? array()) . "\n";
        $message .= "- NJ Focus: " . count(array_filter($data['articles'] ?? array(), function($a) { return $a['jurisdiction'] === 'New Jersey'; })) . "\n";
        $message .= "- NY Focus: " . count(array_filter($data['articles'] ?? array(), function($a) { return $a['jurisdiction'] === 'New York'; })) . "\n";
        $message .= "- Local 825 Specific: " . count(array_filter($data['articles'] ?? array(), function($a) { return $a['jurisdiction'] === 'Local 825 Specific'; })) . "\n\n";
        $message .= "View full report at: " . admin_url('admin.php?page=local825-intelligence') . "\n\n";
        $message .= "Generated by Local 825 Intelligence Plugin";
        
        wp_mail($to, $subject, $message);
    }
    
    // Cron job handlers
    public function cron_update_intelligence() {
        $this->update_intelligence_data();
    }
    
    public function cron_update_company_tracking() {
        $this->update_company_tracking();
    }
    
    // Settings field renderers
    public function mcp_server_url_field() {
        $value = get_option('local825_mcp_server_url', '');
        echo '<input type="url" name="local825_mcp_server_url" value="' . esc_attr($value) . '" class="regular-text" placeholder="https://your-railway-app.railway.app" />';
        echo '<p class="description">Enter your Railway-hosted MCP server URL</p>';
    }
    
    public function api_key_field() {
        $value = get_option('local825_api_key', '');
        echo '<input type="password" name="local825_api_key" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">Enter your MCP server API key</p>';
    }
    
    public function auto_update_field() {
        $value = get_option('local825_auto_update', '1');
        echo '<input type="checkbox" name="local825_auto_update" value="1" ' . checked('1', $value, false) . ' />';
        echo '<span class="description">Enable automatic intelligence updates</span>';
    }
    
    public function notification_email_field() {
        $value = get_option('local825_notification_email', '');
        echo '<input type="email" name="local825_notification_email" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">Email address for intelligence notifications</p>';
    }
    
    public function company_settings_section() {
        echo '<p>Configure company tracking settings and manage the list of companies to monitor.</p>';
    }
    
    public function general_settings_section() {
        echo '<p>Configure general plugin settings and notifications.</p>';
    }
    
    public function mcp_settings_section() {
        echo '<p>Configure connection to your Railway-hosted MCP server.</p>';
    }
    
    // Plugin activation/deactivation
    public function activate() {
        // Create default options
        add_option('local825_mcp_server_url', 'https://your-railway-app.railway.app');
        add_option('local825_api_key', '');
        add_option('local825_auto_update', '1');
        add_option('local825_notification_email', get_option('admin_email'));
        add_option('local825_intelligence_data', array());
        add_option('local825_company_data', array());
        add_option('local825_last_update', '');
        
        // Set up cron jobs
        wp_schedule_event(time(), 'hourly', 'local825_intelligence_update');
        wp_schedule_event(time(), 'daily', 'local825_company_tracking_update');
        
        // Flush rewrite rules
        flush_rewrite_rules();
    }
    
    public function deactivate() {
        // Clear cron jobs
        wp_clear_scheduled_hook('local825_intelligence_update');
        wp_clear_scheduled_hook('local825_company_tracking_update');
        
        // Flush rewrite rules
        flush_rewrite_rules();
    }
}

// Initialize plugin
new Local825IntelligencePlugin();

// Add custom cron intervals
add_filter('cron_schedules', function($schedules) {
    $schedules['every_30_minutes'] = array(
        'interval' => 1800,
        'display' => 'Every 30 Minutes'
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
                'confirm_delete' => 'Are you sure you want to delete this item?'
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

/**
 * Local 825 Logger Class
 * Handles comprehensive logging for API usage, token consumption, and costs
 */
class Local825Logger {
    private $log_file;
    private $usage_stats;
    
    public function __construct() {
        $upload_dir = wp_upload_dir();
        $this->log_file = $upload_dir['basedir'] . '/local825-intelligence.log';
        $this->usage_stats = [
            'start_time' => microtime(true),
            'api_calls' => [],
            'tokens_used' => [],
            'costs' => [],
            'services' => []
        ];
    }
    
    public function log($level, $message) {
        $timestamp = current_time('mysql');
        $log_entry = "[{$timestamp}] [{$level}] {$message}" . PHP_EOL;
        
        // Write to log file
        file_put_contents($this->log_file, $log_entry, FILE_APPEND | LOCK_EX);
        
        // Also output to WordPress debug log
        error_log("Local825: {$message}");
        
        // Output to console if in CLI
        if (php_sapi_name() === 'cli') {
            echo $log_entry;
        }
    }
    
    public function log_api_call($service, $endpoint, $response) {
        $call_data = [
            'service' => $service,
            'endpoint' => $endpoint,
            'timestamp' => current_time('mysql'),
            'response_code' => wp_remote_retrieve_response_code($response),
            'response_time' => wp_remote_retrieve_header($response, 'x-response-time') ?: 'unknown'
        ];
        
        $this->usage_stats['api_calls'][] = $call_data;
        $this->log('info', "API call to {$service}{$endpoint} - Status: {$call_data['response_code']}");
    }
    
    public function log_token_usage($service, $tokens_used, $cost_per_1k_tokens = null) {
        $token_data = [
            'service' => $service,
            'tokens_used' => $tokens_used,
            'timestamp' => current_time('mysql')
        ];
        
        if ($cost_per_1k_tokens) {
            $cost = ($tokens_used / 1000) * $cost_per_1k_tokens;
            $token_data['cost'] = $cost;
            $this->usage_stats['costs'][] = [
                'service' => $service,
                'cost' => $cost,
                'tokens' => $tokens_used
            ];
        }
        
        $this->usage_stats['tokens_used'][] = $token_data;
        $this->log('info', "Token usage for {$service}: {$tokens_used} tokens" . 
            ($cost_per_1k_tokens ? " (Cost: $" . number_format($cost, 4) . ")" : ""));
    }
    
    public function log_service_usage($service, $details) {
        $this->usage_stats['services'][] = [
            'service' => $service,
            'details' => $details,
            'timestamp' => current_time('mysql')
        ];
        
        $this->log('info', "Service usage for {$service}: " . json_encode($details));
    }
    
    public function log_final_usage_stats() {
        $end_time = microtime(true);
        $total_time = $end_time - $this->usage_stats['start_time'];
        
        $total_tokens = array_sum(array_column($this->usage_stats['tokens_used'], 'tokens_used'));
        $total_cost = array_sum(array_column($this->usage_stats['costs'], 'cost'));
        $total_api_calls = count($this->usage_stats['api_calls']);
        
        $summary = [
            'Total Runtime' => number_format($total_time, 2) . ' seconds',
            'Total API Calls' => $total_api_calls,
            'Total Tokens Used' => number_format($total_tokens),
            'Total Cost' => '$' . number_format($total_cost, 4),
            'Services Used' => array_unique(array_column($this->usage_stats['services'], 'service'))
        ];
        
        $this->log('info', '=== USAGE SUMMARY ===');
        foreach ($summary as $key => $value) {
            $this->log('info', "{$key}: {$value}");
        }
        $this->log('info', '====================');
        
        // Output to console for terminal visibility
        $this->output_console_summary($summary);
    }
    
    private function output_console_summary($summary) {
        // This will output to the WordPress debug log and console
        $console_output = "\n";
        $console_output .= "🚀 LOCAL 825 INTELLIGENCE RUN COMPLETE\n";
        $console_output .= "=====================================\n";
        foreach ($summary as $key => $value) {
            $console_output .= "📊 {$key}: {$value}\n";
        }
        $console_output .= "=====================================\n\n";
        
        // Output to WordPress debug log
        error_log($console_output);
        
        // Also output to browser console if in admin
        if (is_admin()) {
            echo "<script>console.log(" . json_encode($console_output) . ");</script>";
        }
        
        // Output to terminal if in CLI
        if (php_sapi_name() === 'cli') {
            echo $console_output;
        }
    }
    
    public function get_usage_stats() {
        return $this->usage_stats;
    }
    
    public function reset_usage_stats() {
        $this->usage_stats = [
            'start_time' => microtime(true),
            'api_calls' => [],
            'tokens_used' => [],
            'costs' => [],
            'services' => []
        ];
    }
}
