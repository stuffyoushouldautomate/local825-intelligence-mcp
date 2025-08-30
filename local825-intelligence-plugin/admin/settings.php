<?php
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap local825-admin">
    <h1 class="wp-heading-inline">
        <span class="dashicons dashicons-admin-settings" style="color: #d4af37;"></span>
        Local 825 Intelligence Settings
    </h1>
    
    <div class="local825-settings-container">
        <form method="post" action="options.php">
            <?php
            settings_fields('local825_settings');
            do_settings_sections('local825-settings');
            ?>
            
            <div class="local825-settings-actions">
                <?php submit_button('Save Settings', 'primary', 'submit', false); ?>
                <button type="button" id="test-mcp-connection" class="button button-secondary">
                    Test MCP Connection
                </button>
                <button type="button" id="reset-settings" class="button button-secondary">
                    Reset to Defaults
                </button>
            </div>
        </form>
        
        <!-- MCP Server Status -->
        <div class="local825-mcp-status">
            <h3>MCP Server Status</h3>
            <div class="status-grid">
                <div class="status-item">
                    <span class="status-label">Server URL:</span>
                    <span class="status-value"><?php echo esc_html(get_option('local825_mcp_server_url', 'Not configured')); ?></span>
                </div>
                <div class="status-item">
                    <span class="status-label">API Key:</span>
                    <span class="status-value"><?php echo get_option('local825_api_key') ? 'Configured' : 'Missing'; ?></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Connection:</span>
                    <span class="status-value" id="connection-status">Testing...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Last Test:</span>
                    <span class="status-value" id="last-test">Never</span>
                </div>
            </div>
        </div>
        
        <!-- Company Management -->
        <div class="local825-company-management">
            <h3>Company Tracking Management</h3>
            <p>Manage the list of companies to track for Local 825 intelligence gathering.</p>
            
            <div class="company-categories">
                <div class="category-section">
                    <h4>Local 825 Target Companies (Primary Tracking)</h4>
                    <p>These are the specific companies Local 825 is actively monitoring and tracking.</p>
                    <div class="company-list-editor">
                        <textarea id="local825-companies" rows="10" cols="80" placeholder="Enter Local 825 target company names, one per line..."><?php echo esc_textarea(get_option('local825_local825_companies', '')); ?></textarea>
                        <div class="company-actions">
                            <button type="button" id="save-local825-companies" class="button button-primary">Save Local 825 Companies</button>
                            <button type="button" id="load-local825-target-companies" class="button button-secondary">Load Local 825 Target Companies</button>
                        </div>
                    </div>
                </div>
                
                <div class="category-section">
                    <h4>General Construction Companies (Secondary Tracking)</h4>
                    <p>These companies provide industry context and may be of interest for broader market intelligence.</p>
                    <div class="company-list-editor">
                        <textarea id="general-companies" rows="10" cols="80" placeholder="Enter general construction company names, one per line..."><?php echo esc_textarea(get_option('local825_general_companies', '')); ?></textarea>
                        <div class="company-actions">
                            <button type="button" id="save-general-companies" class="button button-primary">Save General Companies</button>
                            <button type="button" id="load-general-companies" class="button button-secondary">Load General Construction Companies</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="company-preview">
                <h4>Current Companies</h4>
                <div class="company-preview-grid">
                    <div class="preview-category">
                        <h5>Local 825 Target Companies (<?php echo count(explode("\n", get_option('local825_local825_companies', ''))); ?>)</h5>
                        <div id="local825-companies-preview">
                            <?php
                            $local825_companies = explode("\n", get_option('local825_local825_companies', ''));
                            $local825_companies = array_filter(array_map('trim', $local825_companies));
                            if (!empty($local825_companies)) {
                                echo '<ul>';
                                foreach ($local825_companies as $company) {
                                    echo '<li>' . esc_html($company) . '</li>';
                                }
                                echo '</ul>';
                            } else {
                                echo '<p>No Local 825 target companies configured</p>';
                            }
                            ?>
                        </div>
                    </div>
                    
                    <div class="preview-category">
                        <h5>General Construction Companies (<?php echo count(explode("\n", get_option('local825_general_companies', ''))); ?>)</h5>
                        <div id="general-companies-preview">
                            <?php
                            $general_companies = explode("\n", get_option('local825_general_companies', ''));
                            $general_companies = array_filter(array_map('trim', $general_companies));
                            if (!empty($general_companies)) {
                                echo '<ul>';
                                foreach ($general_companies as $company) {
                                    echo '<li>' . esc_html($company) . '</li>';
                                }
                                echo '</ul>';
                            } else {
                                echo '<p>No general companies configured</p>';
                            }
                            ?>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Advanced Settings -->
        <div class="local825-advanced-settings">
            <h3>Advanced Settings</h3>
            
            <table class="form-table">
                <tr>
                    <th scope="row">Update Frequency</th>
                    <td>
                        <select name="local825_update_frequency">
                            <option value="15" <?php selected(get_option('local825_update_frequency', '60'), '15'); ?>>Every 15 minutes</option>
                            <option value="30" <?php selected(get_option('local825_update_frequency', '60'), '30'); ?>>Every 30 minutes</option>
                            <option value="60" <?php selected(get_option('local825_update_frequency', '60'), '60'); ?>>Every hour</option>
                            <option value="120" <?php selected(get_option('local825_update_frequency', '60'), '120'); ?>>Every 2 hours</option>
                            <option value="240" <?php selected(get_option('local825_update_frequency', '60'), '240'); ?>>Every 4 hours</option>
                        </select>
                        <p class="description">How often to automatically update intelligence data</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">Data Retention</th>
                    <td>
                        <select name="local825_data_retention">
                            <option value="7" <?php selected(get_option('local825_data_retention', '30'), '7'); ?>>7 days</option>
                            <option value="14" <?php selected(get_option('local825_data_retention', '30'), '14'); ?>>14 days</option>
                            <option value="30" <?php selected(get_option('local825_data_retention', '30'), '30'); ?>>30 days</option>
                            <option value="60" <?php selected(get_option('local825_data_retention', '30'), '60'); ?>>60 days</option>
                            <option value="90" <?php selected(get_option('local825_data_retention', '30'), '90'); ?>>90 days</option>
                        </select>
                        <p class="description">How long to keep intelligence data before cleanup</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">Debug Mode</th>
                    <td>
                        <label>
                            <input type="checkbox" name="local825_debug_mode" value="1" <?php checked(get_option('local825_debug_mode', '0'), '1'); ?> />
                            Enable debug logging
                        </label>
                        <p class="description">Log detailed information for troubleshooting</p>
                    </td>
                </tr>
            </table>
        </div>
        
        <!-- Import/Export -->
        <div class="local825-import-export">
            <h3>Import/Export Settings</h3>
            
            <div class="import-export-actions">
                <div class="export-section">
                    <h4>Export Settings</h4>
                    <p>Export your current plugin configuration</p>
                    <button type="button" id="export-settings" class="button button-secondary">Export Settings</button>
                </div>
                
                <div class="import-section">
                    <h4>Import Settings</h4>
                    <p>Import configuration from another installation</p>
                    <input type="file" id="import-file" accept=".json" />
                    <button type="button" id="import-settings" class="button button-secondary">Import Settings</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
jQuery(document).ready(function($) {
    // Test MCP Connection
    $('#test-mcp-connection').on('click', function() {
        var $btn = $(this);
        var originalText = $btn.text();
        
        $btn.prop('disabled', true).text('Testing...');
        $('#connection-status').text('Testing...').removeClass('status-ok status-error').addClass('status-testing');
        
        $.ajax({
            url: ajaxurl,
            type: 'POST',
            data: {
                action: 'local825_test_mcp_connection',
                nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>'
            },
            success: function(response) {
                if (response.success) {
                    $('#connection-status').text('Connected').removeClass('status-testing status-error').addClass('status-ok');
                    $('#last-test').text(new Date().toLocaleString());
                } else {
                    $('#connection-status').text('Failed').removeClass('status-testing status-ok').addClass('status-error');
                }
            },
            error: function() {
                $('#connection-status').text('Error').removeClass('status-testing status-ok').addClass('status-error');
            },
            complete: function() {
                $btn.prop('disabled', false).text(originalText);
            }
        });
    });
    
    // Save Local 825 Companies
    $('#save-local825-companies').on('click', function() {
        var companyList = $('#local825-companies').val();
        var $btn = $(this);
        var originalText = $btn.text();
        
        $btn.prop('disabled', true).text('Saving...');
        
        $.ajax({
            url: ajaxurl,
            type: 'POST',
            data: {
                action: 'local825_save_company_list',
                nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>',
                company_list: companyList,
                category: 'local825_local825_companies'
            },
            success: function(response) {
                if (response.success) {
                    updateCompanyPreview('local825-companies', 'local825-companies-preview');
                    alert('Local 825 target companies saved successfully!');
                } else {
                    alert('Error saving Local 825 companies: ' + response.data);
                }
            },
            error: function() {
                alert('Failed to save Local 825 companies');
            },
            complete: function() {
                $btn.prop('disabled', false).text(originalText);
            }
        });
    });
    
    // Load Local 825 Target Companies
    $('#load-local825-target-companies').on('click', function() {
        var defaultCompanies = [
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
        
        var companyList = defaultCompanies.join('\n');
        $('#local825-companies').val(companyList);
        updateCompanyPreview('local825-companies', 'local825-companies-preview');
    });
    
    // Save General Companies
    $('#save-general-companies').on('click', function() {
        var companyList = $('#general-companies').val();
        var $btn = $(this);
        var originalText = $btn.text();
        
        $btn.prop('disabled', true).text('Saving...');
        
        $.ajax({
            url: ajaxurl,
            type: 'POST',
            data: {
                action: 'local825_save_company_list',
                nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>',
                company_list: companyList,
                category: 'local825_general_companies'
            },
            success: function(response) {
                if (response.success) {
                    updateCompanyPreview('general-companies', 'general-companies-preview');
                    alert('General construction companies saved successfully!');
                } else {
                    alert('Error saving general companies: ' + response.data);
                }
            },
            error: function() {
                alert('Failed to save general companies');
            },
            complete: function() {
                $btn.prop('disabled', false).text(originalText);
            }
        });
    });
    
    // Load General Construction Companies
    $('#load-general-companies').on('click', function() {
        var defaultCompanies = [
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
        
        var companyList = defaultCompanies.join('\n');
        $('#general-companies').val(companyList);
        updateCompanyPreview('general-companies', 'general-companies-preview');
    });
    
    // Reset Settings
    $('#reset-settings').on('click', function() {
        if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
            $.ajax({
                url: ajaxurl,
                type: 'POST',
                data: {
                    action: 'local825_reset_settings',
                    nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>'
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert('Error resetting settings: ' + response.data);
                    }
                },
                error: function() {
                    alert('Failed to reset settings');
                }
            });
        }
    });
    
    // Export Settings
    $('#export-settings').on('click', function() {
        $.ajax({
            url: ajaxurl,
            type: 'POST',
            data: {
                action: 'local825_export_settings',
                nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>'
            },
            success: function(response) {
                if (response.success) {
                    var blob = new Blob([JSON.stringify(response.data, null, 2)], {type: 'application/json'});
                    var url = window.URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url;
                    a.download = 'local825_settings_' + new Date().toISOString().split('T')[0] + '.json';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    alert('Error exporting settings: ' + response.data);
                }
            },
            error: function() {
                alert('Failed to export settings');
            }
        });
    });
    
    // Import Settings
    $('#import-settings').on('click', function() {
        var fileInput = $('#import-file')[0];
        var file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a file to import');
            return;
        }
        
        var reader = new FileReader();
        reader.onload = function(e) {
            try {
                var settings = JSON.parse(e.target.result);
                
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'local825_import_settings',
                        nonce: '<?php echo wp_create_nonce('local825_nonce'); ?>',
                        settings: settings
                    },
                    success: function(response) {
                        if (response.success) {
                            alert('Settings imported successfully!');
                            location.reload();
                        } else {
                            alert('Error importing settings: ' + response.data);
                        }
                    },
                    error: function() {
                        alert('Failed to import settings');
                    }
                });
            } catch (error) {
                alert('Invalid settings file format');
            }
        };
        reader.readAsText(file);
    });
    
    function updateCompanyPreview(textareaId, previewId) {
        var companyList = $('#' + textareaId).val();
        var companies = companyList.split('\n').filter(function(company) {
            return company.trim() !== '';
        });
        
        var previewHtml = '<ul>';
        companies.forEach(function(company) {
            previewHtml += '<li>' + company.trim() + '</li>';
        });
        previewHtml += '</ul>';
        
        $('#' + previewId).html(previewHtml);
        $('.company-preview h4').text('Current Companies');
    }
    
    // Auto-test connection on page load
    $('#test-mcp-connection').click();
});
</script>

<style>
.local825-settings-container {
    max-width: 1200px;
}

.local825-settings-actions {
    margin: 20px 0;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 5px;
}

.local825-settings-actions .button {
    margin-right: 10px;
}

.local825-mcp-status,
.local825-company-management,
.local825-advanced-settings,
.local825-import-export {
    margin: 30px 0;
    padding: 20px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.status-item {
    padding: 10px;
    background: #f9f9f9;
    border-radius: 3px;
}

.status-label {
    font-weight: 500;
    color: #666;
}

.status-value {
    display: block;
    margin-top: 5px;
    font-weight: 600;
}

.status-ok { color: #46b450; }
.status-error { color: #dc3232; }
.status-warning { color: #ffb900; }
.status-testing { color: #0073aa; }

.company-list-editor {
    margin: 20px 0;
}

.company-list-editor textarea {
    width: 100%;
    font-family: monospace;
    margin-bottom: 15px;
}

.company-actions {
    margin-bottom: 20px;
}

.company-actions .button {
    margin-right: 10px;
}

.company-preview {
    background: #f9f9f9;
    padding: 15px;
    border-radius: 3px;
}

.company-preview ul {
    margin: 10px 0;
    padding-left: 20px;
}

.company-preview li {
    margin: 5px 0;
}

.company-preview-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.preview-category h5 {
    margin-top: 0;
    margin-bottom: 10px;
}

.import-export-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.import-section,
.export-section {
    padding: 15px;
    background: #f9f9f9;
    border-radius: 3px;
}

.import-section h4,
.export-section h4 {
    margin-top: 0;
}

.import-section input[type="file"] {
    margin: 10px 0;
}

.form-table th {
    width: 200px;
}
</style>
