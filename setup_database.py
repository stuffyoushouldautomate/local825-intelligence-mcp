#!/usr/bin/env python3
"""
Database Setup Script for DataPilotPlus Scraper
Creates the MySQL database and tables needed for the scraper
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            database_name = os.getenv('MYSQL_DATABASE', 'datapilotplus_scraper')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            logging.info(f"Database '{database_name}' created successfully")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        logging.error(f"Error creating database: {e}")
        return False

def create_tables():
    """Create all necessary tables"""
    try:
        # Connect to the specific database
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            database=os.getenv('MYSQL_DATABASE', 'datapilotplus_scraper'),
            user=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD'),
            charset=os.getenv('MYSQL_CHARSET', 'utf8mb4')
        )
        
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
            
            # Execute table creation
            tables = [
                ('scraped_data', create_data_table),
                ('reports', create_reports_table),
                ('api_configs', create_config_table),
                ('scraping_jobs', create_jobs_table),
                ('data_quality', create_quality_table)
            ]
            
            for table_name, create_sql in tables:
                cursor.execute(create_sql)
                logging.info(f"Table '{table_name}' created successfully")
            
            # Insert sample API configurations
            sample_apis = [
                ('sec_edgar', 'https://www.sec.gov/edgar/sec-api-documentation'),
                ('opencorporates', 'https://api.opencorporates.com/documentation/API-Reference'),
                ('yahoo_finance', 'https://finance.yahoo.com/apis'),
                ('usaspending', 'https://api.usaspending.gov/docs/endpoints'),
                ('osha_api', 'https://www.osha.gov/data'),
                ('nlrb_api', 'https://www.nlrb.gov/reports-guidance'),
                ('fec_api', 'https://api.open.fec.gov/developers/'),
                ('opensecrets', 'https://www.opensecrets.org/api/')
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
            cursor.close()
            connection.close()
            
            logging.info("All tables created successfully with sample data")
            return True
            
    except Error as e:
        logging.error(f"Error creating tables: {e}")
        return False

def test_connection():
    """Test the database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            database=os.getenv('MYSQL_DATABASE', 'datapilotplus_scraper'),
            user=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD'),
            charset=os.getenv('MYSQL_CHARSET', 'utf8mb4')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logging.info(f"Database connection successful. MySQL version: {version[0]}")
            
            # Test table access
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logging.info(f"Available tables: {[table[0] for table in tables]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        logging.error(f"Database connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    logging.info("🚀 Starting DataPilotPlus database setup...")
    
    # Check environment variables
    required_vars = ['MYSQL_HOST', 'MYSQL_USERNAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {missing_vars}")
        logging.error("Please update your .env file with MySQL credentials")
        return False
    
    # Create database
    if not create_database():
        logging.error("Failed to create database")
        return False
    
    # Create tables
    if not create_tables():
        logging.error("Failed to create tables")
        return False
    
    # Test connection
    if not test_connection():
        logging.error("Database connection test failed")
        return False
    
    logging.info("✅ Database setup completed successfully!")
    logging.info("You can now run the DataPilotPlus scraper")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
