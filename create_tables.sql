-- Création de la table utilisateur personnalisée
CREATE TABLE IF NOT EXISTS core_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN DEFAULT false,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_staff BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email VARCHAR(254) UNIQUE NOT NULL,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'fr',
    safe_search BOOLEAN DEFAULT true,
    results_per_page INTEGER DEFAULT 10,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

-- Table UserProfile
CREATE TABLE IF NOT EXISTS core_userprofile (
    id SERIAL PRIMARY KEY,
    bio TEXT,
    location VARCHAR(30),
    last_password_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER UNIQUE REFERENCES core_user(id) ON DELETE CASCADE
);

-- Table SearchHistory
CREATE TABLE IF NOT EXISTS core_searchhistory (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_count INTEGER DEFAULT 0,
    search_filters JSONB DEFAULT '{}',
    user_id INTEGER REFERENCES core_user(id) ON DELETE CASCADE
);

-- Créez les index
CREATE INDEX IF NOT EXISTS idx_search_history_user_timestamp ON core_searchhistory(user_id, timestamp);
