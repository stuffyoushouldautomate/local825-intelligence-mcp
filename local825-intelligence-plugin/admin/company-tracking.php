<?php
if (!defined('ABSPATH')) {
    exit;
}

$plugin = new Local825IntelligencePlugin();
$company_data = $plugin->get_company_data();
?>

<div class="wrap local825-admin">
    <h1 class="wp-heading-inline">
        <span class="dashicons dashicons-building" style="color: #d4af37;"></span>
        Company Tracking
    </h1>
    
    <div class="local825-header-actions">
        <button id="refresh-companies" class="button button-primary">
            <span class="dashicons dashicons-update"></span>
            Refresh Company Data
        </button>
    </div>

    <!-- Company Management -->
    <div class="local825-section">
        <h2>Target Companies</h2>
        
        <div class="company-lists">
            <!-- Local 825 Target Companies -->
            <div class="company-list">
                <h3>Local 825 Target Companies</h3>
                <p class="description">Companies specifically targeted for Local 825 intelligence gathering.</p>
                
                <div class="company-input">
                    <textarea id="local825-companies" rows="10" class="large-text" placeholder="Enter company names, one per line..."><?php echo esc_textarea(get_option('local825_local825_companies', '')); ?></textarea>
                    <div class="company-actions">
                        <button id="load-local825-target-companies" class="button button-secondary">
                            <span class="dashicons dashicons-download"></span>
                            Load Default Companies
                        </button>
                    </div>
                </div>
                
                <div class="company-preview">
                    <h4>Preview:</h4>
                    <div id="local825-companies-preview"></div>
                </div>
            </div>
            
            <!-- General Construction Companies -->
            <div class="company-list">
                <h3>General Construction Companies</h3>
                <p class="description">General construction companies to monitor for industry trends.</p>
                
                <div class="company-input">
                    <textarea id="general-companies" rows="10" class="large-text" placeholder="Enter company names, one per line..."><?php echo esc_textarea(get_option('local825_general_companies', '')); ?></textarea>
                    <div class="company-actions">
                        <button id="load-general-companies" class="button button-secondary">
                            <span class="dashicons dashicons-download"></span>
                            Load Default Companies
                        </button>
                    </div>
                </div>
                
                <div class="company-preview">
                    <h4>Preview:</h4>
                    <div id="general-companies-preview"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Company Status Tracking -->
    <div class="local825-section">
        <h2>Company Status Tracking</h2>
        
        <?php if (!empty($company_data)): ?>
            <div class="company-status-grid">
                <?php foreach ($company_data as $company_id => $company): ?>
                    <div class="company-status-card">
                        <div class="company-header">
                            <h4><?php echo esc_html($company['name']); ?></h4>
                            <span class="company-status status-<?php echo esc_attr($company['status'] ?? 'unknown'); ?>">
                                <?php echo esc_html(ucfirst($company['status'] ?? 'Unknown')); ?>
                            </span>
                        </div>
                        <div class="company-details">
                            <p><strong>Industry:</strong> <?php echo esc_html($company['industry'] ?? 'N/A'); ?></p>
                            <p><strong>Last Updated:</strong> <?php echo esc_html($company['last_updated'] ?? 'Never'); ?></p>
                            <?php if (!empty($company['notes'])): ?>
                                <p><strong>Notes:</strong> <?php echo esc_html($company['notes']); ?></p>
                            <?php endif; ?>
                        </div>
                        <div class="company-actions">
                            <button class="button button-small update-company-status" data-company-id="<?php echo esc_attr($company_id); ?>">
                                Update Status
                            </button>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="no-data">
                <p>No company data available. Companies will appear here once data is collected from the MCP server.</p>
            </div>
        <?php endif; ?>
    </div>
</div>
