-- Initialize SonarQube database
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create SonarQube database
CREATE DATABASE sonarqube;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO postgres;
