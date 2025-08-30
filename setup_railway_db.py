#!/usr/bin/env python3
"""
Setup script for Railway MySQL database
"""

import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Railway MySQL connection details
RAILWAY_DB_CONFIG = {
    'host': 'turntable.proxy.rlwy.net',
    'port': 18378,
    'database': 'railway',
    'user': 'root',
    'password': 'SHcmvzhGBglIlMgpQccGRBBuMIrLABtW',
    'charset': 'utf8mb4'
}

def create_tables():
    """Create the necessary tables for the MCP server"""
    try:
        connection = mysql.connector.connect(**RAILWAY_DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Table for scraped data
            create_data_table = """
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source_name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                method_type VARCHAR(50) NOT NULL,
                url TEXT,
                data_points JSON,
                content TEXT,
                analysis JSON,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_source (source_name),
                INDEX idx_category (category),
                INDEX idx_scraped_at (scraped_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table for reports
            create_reports_table = """
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_type VARCHAR(100) NOT NULL,
                report_date DATE NOT NULL,
                content TEXT,
                summary JSON,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_report_type (report_type),
                INDEX idx_report_date (report_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table for API keys and configurations
            create_config_table = """
            CREATE TABLE IF NOT EXISTS api_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                api_name VARCHAR(100) NOT NULL,
                api_key TEXT,
                base_url TEXT,
                rate_limit INT DEFAULT 100,
                last_used TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_api (api_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table for scraping jobs and schedules
            create_jobs_table = """
            CREATE TABLE IF NOT EXISTS scraping_jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_name VARCHAR(255) NOT NULL,
                source_name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                schedule VARCHAR(100),
                last_run TIMESTAMP NULL,
                next_run TIMESTAMP NULL,
                status ENUM('active', 'paused', 'error') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_job_name (job_name),
                INDEX idx_status (status),
                INDEX idx_next_run (next_run)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table for data quality metrics
            create_quality_table = """
            CREATE TABLE IF NOT EXISTS data_quality (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source_name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                quality_score DECIMAL(3,2) DEFAULT 0.00,
                completeness_score DECIMAL(3,2) DEFAULT 0.00,
                accuracy_score DECIMAL(3,2) DEFAULT 0.00,
                freshness_score DECIMAL(3,2) DEFAULT 0.00,
                total_records INT DEFAULT 0,
                valid_records INT DEFAULT 0,
                last_assessment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_source_category (source_name, category),
                INDEX idx_quality_score (quality_score)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table for Local 825 intelligence data
            create_intelligence_table = """
            CREATE TABLE IF NOT EXISTS local825_intelligence (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                url TEXT,
                source VARCHAR(255),
                published_date DATETIME,
                summary TEXT,
                jurisdiction ENUM('New Jersey', 'New York', 'Local 825', 'General') DEFAULT 'General',
                relevance_score INT DEFAULT 0,
                category VARCHAR(100),
                content TEXT,
                analysis JSON,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_jurisdiction (jurisdiction),
                INDEX idx_relevance_score (relevance_score),
                INDEX idx_category (category),
                INDEX idx_published_date (published_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Table for company tracking
            create_companies_table = """
            CREATE TABLE IF NOT EXISTS companies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                jurisdiction ENUM('New Jersey', 'New York', 'Both', 'General') DEFAULT 'General',
                union_status ENUM('Union', 'Non-Union', 'Mixed', 'Unknown') DEFAULT 'Unknown',
                industry VARCHAR(100),
                projects JSON,
                contact_info JSON,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_company (company_name),
                INDEX idx_jurisdiction (jurisdiction),
                INDEX idx_union_status (union_status),
                INDEX idx_industry (industry)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Execute table creation
            tables = [
                ('scraped_data', create_data_table),
                ('reports', create_reports_table),
                ('api_configs', create_config_table),
                ('scraping_jobs', create_jobs_table),
                ('data_quality', create_quality_table),
                ('local825_intelligence', create_intelligence_table),
                ('companies', create_companies_table)
            ]
            
            for table_name, create_sql in tables:
                try:
                    cursor.execute(create_sql)
                    logging.info(f"✅ Table '{table_name}' created successfully")
                except Error as e:
                    if "already exists" in str(e).lower():
                        logging.info(f"ℹ️ Table '{table_name}' already exists")
                    else:
                        logging.error(f"❌ Error creating table '{table_name}': {e}")
            
            # Insert sample data
            try:
                # Insert sample API configs
                sample_apis = [
                    ('DataPilotPlus', 'https://datapilotplus.com'),
                    ('SEC EDGAR', 'https://www.sec.gov/edgar/searchedgar/companysearch'),
                    ('OpenCorporates', 'https://opencorporates.com'),
                    ('Yahoo Finance', 'https://finance.yahoo.com'),
                    ('USAspending', 'https://www.usaspending.gov')
                ]
                
                for api_name, base_url in sample_apis:
                    cursor.execute("""
                        INSERT IGNORE INTO api_configs (api_name, base_url)
                        VALUES (%s, %s)
                    """, (api_name, base_url))
                
                # Insert sample scraping jobs
                sample_jobs = [
                    ('DataPilotPlus Daily', 'datapilotplus.com', 'company_information', '0 0 * * *'),
                    ('SEC EDGAR Daily', 'sec_edgar', 'company_information', '0 6 * * *'),
                    ('OpenCorporates Weekly', 'opencorporates', 'company_information', '0 0 * * 0'),
                    ('Yahoo Finance Daily', 'yahoo_finance', 'financial', '0 8 * * *'),
                    ('USAspending Daily', 'usaspending', 'operations', '0 4 * * *')
                ]
                
                for job_name, source, category, schedule in sample_jobs:
                    cursor.execute("""
                        INSERT IGNORE INTO scraping_jobs (job_name, source_name, category, schedule)
                        VALUES (%s, %s, %s, %s)
                    """, (job_name, source, category, schedule))
                
                connection.commit()
                logging.info("✅ Sample data inserted successfully")
                
            except Error as e:
                logging.warning(f"⚠️ Warning inserting sample data: {e}")
            
            cursor.close()
            connection.close()
            
            logging.info("✅ All tables created successfully!")
            return True
            
    except Error as e:
        logging.error(f"❌ Error creating tables: {e}")
        return False

def test_connection():
    """Test the database connection"""
    try:
        connection = mysql.connector.connect(**RAILWAY_DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logging.info(f"✅ Database connection successful. MySQL version: {version[0]}")
            
            # Test table access
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logging.info(f"📋 Available tables: {[table[0] for table in tables]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        logging.error(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    logging.info("🚀 Starting Railway MySQL database setup...")
    
    # Test connection first
    if not test_connection():
        logging.error("❌ Database connection failed. Please check your Railway MySQL credentials.")
        return False
    
    # Create tables
    if not create_tables():
        logging.error("❌ Failed to create tables")
        return False
    
    logging.info("🎉 Railway MySQL database setup completed successfully!")
    logging.info("You can now deploy your MCP server to Railway!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
