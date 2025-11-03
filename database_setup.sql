-- GoBarberly Database Setup Script
-- This script creates all necessary tables for the authentication system
-- Run this script against your PostgreSQL database

-- Create the database (run this as superuser if database doesn't exist)
-- CREATE DATABASE gobarberly_db;

-- Connect to the database
-- \c gobarberly_db;

-- Enable UUID extension for token generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- DJANGO CORE TABLES
-- ============================================================================

-- Django migrations tracking
CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Django content types
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE (app_label, model)
);

-- Django permissions
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id),
    codename VARCHAR(100) NOT NULL,
    UNIQUE (content_type_id, codename)
);

-- Django groups
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- Django group permissions
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES auth_group(id),
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id),
    UNIQUE (group_id, permission_id)
);

-- Django sessions
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create index on session expiry
CREATE INDEX IF NOT EXISTS django_session_expire_date_idx ON django_session(expire_date);

-- Django admin log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id INTEGER REFERENCES django_content_type(id),
    user_id BIGINT NOT NULL
);

-- ============================================================================
-- CUSTOM USER TABLES
-- ============================================================================

-- Custom User table (extends Django AbstractUser)
CREATE TABLE IF NOT EXISTS accounts_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Custom fields
    email VARCHAR(254) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    profile_picture VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'barber', 'shop_owner', 'admin', 'super_admin')),
    
    -- Account status
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_profile_complete BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_ip INET,
    
    -- Address information
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS accounts_user_email_idx ON accounts_user(email);
CREATE INDEX IF NOT EXISTS accounts_user_username_idx ON accounts_user(username);
CREATE INDEX IF NOT EXISTS accounts_user_role_idx ON accounts_user(role);
CREATE INDEX IF NOT EXISTS accounts_user_created_at_idx ON accounts_user(created_at DESC);
CREATE INDEX IF NOT EXISTS accounts_user_is_active_idx ON accounts_user(is_active);

-- User groups relationship
CREATE TABLE IF NOT EXISTS accounts_user_groups (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_user(id),
    group_id INTEGER NOT NULL REFERENCES auth_group(id),
    UNIQUE (user_id, group_id)
);

-- User permissions relationship
CREATE TABLE IF NOT EXISTS accounts_user_user_permissions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_user(id),
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id),
    UNIQUE (user_id, permission_id)
);

-- ============================================================================
-- AUTHENTICATION TOKENS TABLES
-- ============================================================================

-- Email verification tokens
CREATE TABLE IF NOT EXISTS accounts_email_verification_token (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    token UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    is_used BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create indexes for email verification tokens
CREATE UNIQUE INDEX IF NOT EXISTS accounts_email_verification_token_token_idx ON accounts_email_verification_token(token);
CREATE INDEX IF NOT EXISTS accounts_email_verification_token_user_id_idx ON accounts_email_verification_token(user_id);
CREATE INDEX IF NOT EXISTS accounts_email_verification_token_created_at_idx ON accounts_email_verification_token(created_at DESC);

-- Password reset tokens
CREATE TABLE IF NOT EXISTS accounts_password_reset_token (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    token UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour'),
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    ip_address INET,
    user_agent TEXT
);

-- Create indexes for password reset tokens
CREATE UNIQUE INDEX IF NOT EXISTS accounts_password_reset_token_token_idx ON accounts_password_reset_token(token);
CREATE INDEX IF NOT EXISTS accounts_password_reset_token_user_id_idx ON accounts_password_reset_token(user_id);
CREATE INDEX IF NOT EXISTS accounts_password_reset_token_created_at_idx ON accounts_password_reset_token(created_at DESC);

-- ============================================================================
-- USER SESSION TRACKING TABLES
-- ============================================================================

-- User sessions for security tracking
CREATE TABLE IF NOT EXISTS accounts_user_session (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    session_key VARCHAR(40) UNIQUE NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    device_info JSONB,
    login_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create indexes for user sessions
CREATE INDEX IF NOT EXISTS accounts_user_session_user_id_idx ON accounts_user_session(user_id);
CREATE INDEX IF NOT EXISTS accounts_user_session_session_key_idx ON accounts_user_session(session_key);
CREATE INDEX IF NOT EXISTS accounts_user_session_login_time_idx ON accounts_user_session(login_time DESC);

-- User login history for security and analytics
CREATE TABLE IF NOT EXISTS accounts_user_login_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES accounts_user(id) ON DELETE CASCADE,
    email VARCHAR(254) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'blocked')),
    failure_reason VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for login history
CREATE INDEX IF NOT EXISTS accounts_user_login_history_email_timestamp_idx ON accounts_user_login_history(email, timestamp DESC);
CREATE INDEX IF NOT EXISTS accounts_user_login_history_ip_timestamp_idx ON accounts_user_login_history(ip_address, timestamp DESC);
CREATE INDEX IF NOT EXISTS accounts_user_login_history_user_id_idx ON accounts_user_login_history(user_id);
CREATE INDEX IF NOT EXISTS accounts_user_login_history_timestamp_idx ON accounts_user_login_history(timestamp DESC);

-- ============================================================================
-- JWT TOKEN BLACKLIST TABLES (for djangorestframework-simplejwt)
-- ============================================================================

-- Outstanding tokens
CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES accounts_user(id) ON DELETE CASCADE,
    jti VARCHAR(255) UNIQUE NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Blacklisted tokens
CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
    id BIGSERIAL PRIMARY KEY,
    token_id BIGINT UNIQUE NOT NULL REFERENCES token_blacklist_outstandingtoken(id) ON DELETE CASCADE,
    blacklisted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for JWT tokens
CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id_idx ON token_blacklist_outstandingtoken(user_id);
CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_jti_idx ON token_blacklist_outstandingtoken(jti);
CREATE INDEX IF NOT EXISTS token_blacklist_blacklistedtoken_token_id_idx ON token_blacklist_blacklistedtoken(token_id);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at for users
DROP TRIGGER IF EXISTS update_accounts_user_updated_at ON accounts_user;
CREATE TRIGGER update_accounts_user_updated_at
    BEFORE UPDATE ON accounts_user
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to clean expired tokens
CREATE OR REPLACE FUNCTION clean_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Clean expired email verification tokens
    DELETE FROM accounts_email_verification_token 
    WHERE expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Clean expired password reset tokens
    DELETE FROM accounts_password_reset_token 
    WHERE expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
    
    -- Clean old login history (keep last 6 months)
    DELETE FROM accounts_user_login_history 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '6 months';
    
    GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA INSERTION
-- ============================================================================

-- Insert Django content types
INSERT INTO django_content_type (app_label, model) VALUES 
    ('accounts', 'user'),
    ('accounts', 'emailverificationtoken'),
    ('accounts', 'passwordresettoken'),
    ('accounts', 'usersession'),
    ('accounts', 'userloginhistory'),
    ('auth', 'permission'),
    ('auth', 'group'),
    ('contenttypes', 'contenttype'),
    ('sessions', 'session'),
    ('admin', 'logentry'),
    ('token_blacklist', 'outstandingtoken'),
    ('token_blacklist', 'blacklistedtoken')
ON CONFLICT (app_label, model) DO NOTHING;

-- Insert basic permissions
INSERT INTO auth_permission (name, content_type_id, codename) VALUES 
    ('Can add user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'add_user'),
    ('Can change user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'change_user'),
    ('Can delete user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'delete_user'),
    ('Can view user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'view_user')
ON CONFLICT (content_type_id, codename) DO NOTHING;

-- Insert initial groups
INSERT INTO auth_group (name) VALUES 
    ('Customers'),
    ('Barbers'),
    ('Shop Owners'),
    ('Administrators')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- VIEWS FOR REPORTING AND ANALYTICS
-- ============================================================================

-- View for user statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    role,
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_email_verified THEN 1 END) as verified_users,
    COUNT(CASE WHEN is_active THEN 1 END) as active_users,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as new_users_last_30_days
FROM accounts_user
GROUP BY role;

-- View for login statistics
CREATE OR REPLACE VIEW login_stats AS
SELECT 
    DATE(timestamp) as login_date,
    status,
    COUNT(*) as attempt_count,
    COUNT(DISTINCT email) as unique_users
FROM accounts_user_login_history
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp), status
ORDER BY login_date DESC;

-- ============================================================================
-- SAMPLE SUPER USER (REMOVE IN PRODUCTION)
-- ============================================================================

-- Create a sample superuser (change password before production!)
-- Password: 'admin123' (hashed with PBKDF2)
INSERT INTO accounts_user (
    username, email, first_name, last_name, is_superuser, is_staff, 
    is_active, password, role, is_email_verified, created_at
) VALUES (
    'admin',
    'admin@gobarberly.com',
    'Super',
    'Admin',
    TRUE,
    TRUE,
    TRUE,
    'pbkdf2_sha256$600000$dummy$hash',  -- Change this to actual hash
    'super_admin',
    TRUE,
    CURRENT_TIMESTAMP
) ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- MAINTENANCE PROCEDURES
-- ============================================================================

-- Schedule token cleanup (run daily)
-- You can set this up as a cron job or scheduled task
-- Example: SELECT clean_expired_tokens();

COMMENT ON FUNCTION clean_expired_tokens() IS 'Cleans expired tokens and old login history. Should be run daily.';

-- ============================================================================
-- PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE accounts_user;
ANALYZE accounts_email_verification_token;
ANALYZE accounts_password_reset_token;
ANALYZE accounts_user_login_history;

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================

/*
SECURITY CHECKLIST:
1. Change the default superuser password immediately
2. Set up SSL/TLS for database connections
3. Configure proper firewall rules
4. Enable PostgreSQL logging for security monitoring
5. Set up regular backups
6. Consider database encryption at rest
7. Implement connection pooling
8. Monitor for unusual login patterns
9. Set up alerts for failed login attempts
10. Regular security updates for PostgreSQL

PERFORMANCE TIPS:
1. Monitor query performance with EXPLAIN ANALYZE
2. Consider partitioning login_history table by date
3. Set up connection pooling (PgBouncer)
4. Configure appropriate PostgreSQL settings for your hardware
5. Monitor and optimize slow queries
6. Consider read replicas for analytics queries

BACKUP STRATEGY:
1. Set up automated daily backups
2. Test backup restoration procedures
3. Consider point-in-time recovery setup
4. Store backups in secure, offsite location
*/

-- End of setup script
SELECT 'Database setup completed successfully!' as status;