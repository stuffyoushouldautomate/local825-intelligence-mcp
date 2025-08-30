<?php
/**
 * Local 825 Intelligence Logging Test Script
 * 
 * This script demonstrates the comprehensive logging system for tracking:
 * - API calls and responses
 * - Token usage and costs
 * - Service usage statistics
 * - Runtime performance metrics
 * 
 * Run this script to see the logging system in action
 */

// Simulate WordPress environment for testing
if (!function_exists('current_time')) {
    function current_time($type = 'mysql') {
        return date('Y-m-d H:i:s');
    }
}

if (!function_exists('wp_upload_dir')) {
    function wp_upload_dir() {
        return ['basedir' => __DIR__ . '/logs'];
    }
}

if (!function_exists('error_log')) {
    function error_log($message) {
        echo "[ERROR_LOG] {$message}\n";
    }
}

// Create logs directory if it doesn't exist
$logs_dir = __DIR__ . '/logs';
if (!is_dir($logs_dir)) {
    mkdir($logs_dir, 0755, true);
}

/**
 * Local 825 Logger Class (Standalone Version)
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
        
        // Also output to console
        echo $log_entry;
    }
    
    public function log_api_call($service, $endpoint, $response) {
        $call_data = [
            'service' => $service,
            'endpoint' => $endpoint,
            'timestamp' => current_time('mysql'),
            'response_code' => $response['response_code'] ?? 'unknown',
            'response_time' => $response['response_time'] ?? 'unknown'
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
        $console_output = "\n";
        $console_output .= "🚀 LOCAL 825 INTELLIGENCE RUN COMPLETE\n";
        $console_output .= "=====================================\n";
        foreach ($summary as $key => $value) {
            $console_output .= "📊 {$key}: {$value}\n";
        }
        $console_output .= "=====================================\n\n";
        
        echo $console_output;
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

// Test the logging system
echo "🧪 Testing Local 825 Intelligence Logging System\n";
echo "================================================\n\n";

$logger = new Local825Logger();

// Simulate a typical intelligence gathering run
$logger->log('info', '=== STARTING LOCAL 825 INTELLIGENCE GATHERING ===');

// Simulate API calls
$logger->log_api_call('google_news_api', '/search', ['response_code' => 200, 'response_time' => '1.2s']);
$logger->log_api_call('google_news_api', '/search', ['response_code' => 200, 'response_time' => '0.8s']);
$logger->log_api_call('google_news_api', '/search', ['response_code' => 200, 'response_time' => '1.1s']);

$logger->log_api_call('rss_scraper', '/feed/nj_business', ['response_code' => 200, 'response_time' => '0.5s']);
$logger->log_api_call('rss_scraper', '/feed/ny_construction', ['response_code' => 200, 'response_time' => '0.6s']);
$logger->log_api_call('rss_scraper', '/feed/construction_dive', ['response_code' => 200, 'response_time' => '0.4s']);

$logger->log_api_call('mcp_server', '/intelligence', ['response_code' => 200, 'response_time' => '2.1s']);

// Simulate token usage for AI services
$logger->log_token_usage('openai_gpt4', 2500, 0.03); // $0.03 per 1K tokens
$logger->log_token_usage('openai_gpt35', 1200, 0.002); // $0.002 per 1K tokens
$logger->log_token_usage('anthropic_claude', 1800, 0.015); // $0.015 per 1K tokens

// Simulate service usage
$logger->log_service_usage('google_news_api', [
    'queries' => 3,
    'articles_found' => 45,
    'filtered_results' => 32,
    'processing_time' => '3.1s'
]);

$logger->log_service_usage('rss_scraper', [
    'feeds_processed' => 3,
    'articles_scraped' => 67,
    'processing_time' => '1.5s'
]);

$logger->log_service_usage('content_analyzer', [
    'articles_analyzed' => 32,
    'keywords_extracted' => 156,
    'sentiment_analysis' => 'completed',
    'processing_time' => '4.2s'
]);

$logger->log_service_usage('company_tracker', [
    'companies_updated' => 15,
    'new_projects_found' => 8,
    'status_changes' => 3,
    'processing_time' => '2.8s'
]);

// Log final statistics
$logger->log_final_usage_stats();

echo "\n✅ Logging test completed!\n";
echo "📁 Log file created at: " . $logger->get_usage_stats()['log_file'] ?? 'logs/local825-intelligence.log' . "\n";
echo "📊 Check the log file for detailed usage statistics.\n\n";
