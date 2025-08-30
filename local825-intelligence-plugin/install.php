<?php
/**
 * Local 825 Intelligence Plugin Installation Script
 * 
 * This script helps set up the plugin with default data and configurations.
 * Run this after activating the plugin to populate initial data.
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    // If not in WordPress, check if we're in the plugin directory
    if (!file_exists('../../../wp-config.php')) {
        die('This script must be run from within WordPress or the plugin directory.');
    }
}

// Include WordPress if not already loaded
if (!function_exists('wp_loaded')) {
    require_once('../../../wp-config.php');
}

// Check if user can manage options
if (!current_user_can('manage_options')) {
    die('You do not have sufficient permissions to run this script.');
}

// Plugin installation class
class Local825PluginInstaller {
    
    private $default_settings = [
        'local825_mcp_server_url' => 'https://your-railway-app.railway.app',
        'local825_api_key' => '',
        'local825_auto_update' => '1',
        'local825_notification_email' => '',
        'local825_update_frequency' => '60',
        'local825_data_retention' => '30',
        'local825_debug_mode' => '0'
    ];
    
    private $local825_target_companies = [
        'Skanska USA',
        'Tutor Perini Corporation',
        'Kiewit Infrastructure',
        'Walsh Construction',
        'Granite Construction',
        'Dragados USA',
        'Flatiron Construction',
        'Bechtel Corporation',
        'Fluor Corporation',
        'AECOM',
        'Jacobs Engineering',
        'Parsons Corporation',
        'Balfour Beatty',
        'Laing O\'Rourke',
        'Bouygues Construction',
        'Vinci Construction',
        'Royal BAM Group',
        'Strabag SE',
        'Webuild Group',
        'Salini Impregilo',
        'Ferrovial Construction',
        'Acciona Construction',
        'OHL Group',
        'FCC Construction',
        'ACS Group',
        'Sacyr',
        'Isolux Corsan',
        'Abengoa',
        'Elecnor',
        'Técnicas Reunidas',
        'Cobra Group',
        'IDOM',
        'Sener Group'
    ];
    
    private $general_construction_companies = [
        'Turner Construction',
        'Gilbane Building Company',
        'Whiting-Turner Contracting',
        'Clark Construction Group',
        'Brasfield & Gorrie',
        'JE Dunn Construction',
        'McCarthy Building Companies',
        'DPR Construction',
        'Suffolk Construction',
        'Hensel Phelps',
        'Mortenson Construction',
        'PCL Construction',
        'EllisDon',
        'Ledcor Group',
        'Bird Construction'
    ];
    
    public function install() {
        echo "<h1>Local 825 Intelligence Plugin Installation</h1>\n";
        echo "<p>Setting up the plugin with default configurations...</p>\n";
        
        try {
            // Install default companies
            $this->install_default_companies();
            
            // Install default settings
            $this->install_default_settings();
            
            // Create sample intelligence data
            $this->create_sample_data();
            
            // Set up cron jobs
            $this->setup_cron_jobs();
            
            echo "<div style='color: green; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; margin: 10px 0;'>\n";
            echo "<strong>Installation Complete!</strong><br>\n";
            echo "The Local 825 Intelligence Plugin has been successfully installed.\n";
            echo "</div>\n";
            
            echo "<h2>Next Steps:</h2>\n";
            echo "<ol>\n";
            echo "<li>Go to <strong>Local 825 Intel → Settings</strong> to configure your MCP server</li>\n";
            echo "<li>Enter your Railway-hosted MCP server URL</li>\n";
            echo "<li>Set your API key</li>\n";
            echo "<li>Test the MCP connection</li>\n";
            echo "<li>Configure notification settings</li>\n";
            echo "</ol>\n";
            
            echo "<h2>Default Data Installed:</h2>\n";
            echo "<ul>\n";
            echo "<li><strong>" . count($this->default_companies) . " companies</strong> for tracking</li>\n";
            echo "<li><strong>Default settings</strong> for optimal performance</li>\n";
            echo "<li><strong>Sample intelligence data</strong> for testing</li>\n";
            echo "<li><strong>Cron jobs</strong> for automated updates</li>\n";
            echo "</ul>\n";
            
        } catch (Exception $e) {
            echo "<div style='color: #721c24; padding: 10px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; margin: 10px 0;'>\n";
            echo "<strong>Installation Error:</strong> " . $e->getMessage() . "\n";
            echo "</div>\n";
        }
    }
    
    private function install_default_companies() {
        echo "<p>Installing default companies...</p>\n";
        
        $company_list = implode("\n", $this->default_companies);
        update_option('local825_company_list', $company_list);
        
        // Create company tracking data
        $company_data = [];
        foreach ($this->default_companies as $company) {
            $company_id = sanitize_title($company);
            $company_data[$company_id] = [
                'name' => $company,
                'status' => 'Signatory',
                'location' => 'NJ/NY Region',
                'last_update' => current_time('mysql'),
                'notes' => 'Default company data - update with actual information'
            ];
        }
        
        update_option('local825_company_data', $company_data);
        echo "<p>✓ Installed " . count($this->default_companies) . " companies</p>\n";
    }
    
    private function install_default_settings() {
        echo "<p>Installing default settings...</p>\n";
        
        foreach ($this->default_settings as $option => $value) {
            if (empty(get_option($option))) {
                update_option($option, $value);
            }
        }
        
        // Set notification email to admin email if not set
        if (empty(get_option('local825_notification_email'))) {
            update_option('local825_notification_email', get_option('admin_email'));
        }
        
        echo "<p>✓ Installed default settings</p>\n";
    }
    
    private function create_sample_data() {
        echo "<p>Creating sample intelligence data...</p>\n";
        
        $sample_data = [
            'articles' => [
                [
                    'title' => 'Sample: New Jersey Infrastructure Projects Announced',
                    'url' => 'https://example.com/sample-article',
                    'source' => 'Sample Source',
                    'published' => current_time('mysql'),
                    'summary' => 'This is sample data to demonstrate the plugin functionality. Replace with real intelligence data from your MCP server.',
                    'jurisdiction' => 'New Jersey',
                    'relevance_score' => 10,
                    'category' => 'Construction Projects'
                ],
                [
                    'title' => 'Sample: Local 825 Operating Engineers Update',
                    'url' => 'https://example.com/sample-article-2',
                    'source' => 'Sample Source',
                    'published' => current_time('mysql'),
                    'summary' => 'Sample article showing Local 825 specific content. This will be replaced with real data.',
                    'jurisdiction' => 'Local 825 Specific',
                    'relevance_score' => 12,
                    'category' => 'Local 825 Specific'
                ]
            ],
            'metadata' => [
                'total_articles' => 2,
                'last_updated' => current_time('mysql')
            ]
        ];
        
        update_option('local825_intelligence_data', $sample_data);
        update_option('local825_last_update', current_time('mysql'));
        
        echo "<p>✓ Created sample intelligence data</p>\n";
    }
    
    private function setup_cron_jobs() {
        echo "<p>Setting up cron jobs...</p>\n";
        
        // Clear existing cron jobs
        wp_clear_scheduled_hook('local825_intelligence_update');
        wp_clear_scheduled_hook('local825_company_tracking_update');
        
        // Schedule new cron jobs
        if (!wp_next_scheduled('local825_intelligence_update')) {
            wp_schedule_event(time(), 'hourly', 'local825_intelligence_update');
        }
        
        if (!wp_next_scheduled('local825_company_tracking_update')) {
            wp_schedule_event(time(), 'daily', 'local825_company_tracking_update');
        }
        
        echo "<p>✓ Scheduled cron jobs for automated updates</p>\n";
    }
    
    public function uninstall() {
        echo "<h1>Local 825 Intelligence Plugin Uninstallation</h1>\n";
        echo "<p>Removing plugin data and settings...</p>\n";
        
        try {
            // Remove all plugin options
            $options_to_remove = [
                'local825_mcp_server_url',
                'local825_api_key',
                'local825_auto_update',
                'local825_notification_email',
                'local825_company_list',
                'local825_company_data',
                'local825_intelligence_data',
                'local825_last_update',
                'local825_update_frequency',
                'local825_data_retention',
                'local825_debug_mode'
            ];
            
            foreach ($options_to_remove as $option) {
                delete_option($option);
            }
            
            // Clear cron jobs
            wp_clear_scheduled_hook('local825_intelligence_update');
            wp_clear_scheduled_hook('local825_company_tracking_update');
            
            echo "<div style='color: green; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; margin: 10px 0;'>\n";
            echo "<strong>Uninstallation Complete!</strong><br>\n";
            echo "All plugin data and settings have been removed.\n";
            echo "</div>\n";
            
        } catch (Exception $e) {
            echo "<div style='color: #721c24; padding: 10px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; margin: 10px 0;'>\n";
            echo "<strong>Uninstallation Error:</strong> " . $e->getMessage() . "\n";
            echo "</div>\n";
        }
    }
}

// Run installation if accessed directly
if (basename($_SERVER['SCRIPT_NAME']) === 'install.php') {
    $installer = new Local825PluginInstaller();
    
    if (isset($_GET['action']) && $_GET['action'] === 'uninstall') {
        $installer->uninstall();
    } else {
        $installer->install();
    }
    
    echo "<hr>\n";
    echo "<p><small>Installation script completed. You can now delete this file for security.</small></p>\n";
}
?>
