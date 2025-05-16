-- Create enhanced tracking tables for TurnClicksToClients

-- User behavior tracking table
CREATE TABLE IF NOT EXISTS tctc_user_behavior (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    event_data JSONB,
    session_id TEXT,
    user_id TEXT,
    flow_hash TEXT,
    page_type TEXT,
    niche TEXT,
    bucket TEXT,
    variant TEXT,
    user_first_name TEXT,
    user_last_name TEXT,
    user_business_name TEXT,
    user_email TEXT,
    traffic_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_agent TEXT,
    screen_width INTEGER,
    screen_height INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_event_type ON tctc_user_behavior(event_type);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_user_id ON tctc_user_behavior(user_id);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_session_id ON tctc_user_behavior(session_id);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_timestamp ON tctc_user_behavior(timestamp);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_niche ON tctc_user_behavior(niche);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_page_type ON tctc_user_behavior(page_type);

-- Quiz interactions tracking table
CREATE TABLE IF NOT EXISTS tctc_quiz_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,
    session_id TEXT,
    quiz_id TEXT,
    question_id INTEGER,
    question_text TEXT,
    answer_text TEXT,
    answer_score INTEGER,
    time_spent_on_question INTEGER,
    niche TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_interactions_user_id ON tctc_quiz_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_interactions_session_id ON tctc_quiz_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_interactions_quiz_id ON tctc_quiz_interactions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_interactions_timestamp ON tctc_quiz_interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_interactions_niche ON tctc_quiz_interactions(niche);

-- User sessions table
CREATE TABLE IF NOT EXISTS tctc_user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    flow_hash TEXT,
    first_page_url TEXT,
    first_referrer TEXT,
    traffic_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    user_agent TEXT,
    device_type TEXT,
    browser TEXT,
    os TEXT,
    screen_width INTEGER,
    screen_height INTEGER,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tctc_user_sessions_user_id ON tctc_user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_tctc_user_sessions_started_at ON tctc_user_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_tctc_user_sessions_traffic_source ON tctc_user_sessions(traffic_source);

-- User profiles table
CREATE TABLE IF NOT EXISTS tctc_user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    business_name TEXT,
    email TEXT,
    phone TEXT,
    primary_niche TEXT,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    quiz_completions INTEGER DEFAULT 0,
    application_submissions INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tctc_user_profiles_email ON tctc_user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_tctc_user_profiles_primary_niche ON tctc_user_profiles(primary_niche);
CREATE INDEX IF NOT EXISTS idx_tctc_user_profiles_first_seen_at ON tctc_user_profiles(first_seen_at);

-- Create RLS policies
ALTER TABLE tctc_user_behavior ENABLE ROW LEVEL SECURITY;
ALTER TABLE tctc_quiz_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tctc_user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tctc_user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Allow authenticated users to select tctc_user_behavior"
    ON tctc_user_behavior FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to select tctc_quiz_interactions"
    ON tctc_quiz_interactions FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to select tctc_user_sessions"
    ON tctc_user_sessions FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to select tctc_user_profiles"
    ON tctc_user_profiles FOR SELECT
    TO authenticated
    USING (true);

-- Create policies for anonymous users to insert data
CREATE POLICY "Allow anonymous users to insert tctc_user_behavior"
    ON tctc_user_behavior FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY "Allow anonymous users to insert tctc_quiz_interactions"
    ON tctc_quiz_interactions FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY "Allow anonymous users to insert tctc_user_sessions"
    ON tctc_user_sessions FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY "Allow anonymous users to insert tctc_user_profiles"
    ON tctc_user_profiles FOR INSERT
    TO anon
    WITH CHECK (true);
