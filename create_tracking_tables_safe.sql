-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the tctc_user_behavior table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.tctc_user_behavior (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    event_type TEXT NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
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
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    user_agent TEXT,
    screen_width INTEGER,
    screen_height INTEGER
);

-- Create the tctc_quiz_submission table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.tctc_quiz_submission (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    first_name TEXT,
    last_name TEXT,
    business_name TEXT,
    email TEXT,
    phone TEXT,
    growth_stifler_response TEXT,
    quiz_answers JSONB DEFAULT '[]'::jsonb,
    total_score INTEGER,
    niche TEXT,
    primary_outcome_hint TEXT,
    source TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    traffic_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    landing_page TEXT,
    entry_point TEXT,
    referrer TEXT
);

-- Create the tctc_quiz_redirections table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.tctc_quiz_redirections (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    user_first_name TEXT,
    user_last_name TEXT,
    user_business_name TEXT,
    quiz_score INTEGER,
    outcome_bucket TEXT,
    awareness_variant TEXT,
    redirect_url TEXT,
    source TEXT,
    redirected_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    traffic_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    landing_page TEXT,
    entry_point TEXT,
    flow_hash TEXT
);

-- Create indexes for better query performance if they don't exist
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_event_type ON public.tctc_user_behavior(event_type);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_user_id ON public.tctc_user_behavior(user_id);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_session_id ON public.tctc_user_behavior(session_id);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_timestamp ON public.tctc_user_behavior(timestamp);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_niche ON public.tctc_user_behavior(niche);
CREATE INDEX IF NOT EXISTS idx_tctc_user_behavior_traffic_source ON public.tctc_user_behavior(traffic_source);

CREATE INDEX IF NOT EXISTS idx_tctc_quiz_submission_niche ON public.tctc_quiz_submission(niche);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_submission_source ON public.tctc_quiz_submission(source);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_submission_submitted_at ON public.tctc_quiz_submission(submitted_at);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_submission_primary_outcome_hint ON public.tctc_quiz_submission(primary_outcome_hint);

CREATE INDEX IF NOT EXISTS idx_tctc_quiz_redirections_outcome_bucket ON public.tctc_quiz_redirections(outcome_bucket);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_redirections_awareness_variant ON public.tctc_quiz_redirections(awareness_variant);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_redirections_source ON public.tctc_quiz_redirections(source);
CREATE INDEX IF NOT EXISTS idx_tctc_quiz_redirections_redirected_at ON public.tctc_quiz_redirections(redirected_at);

-- Enable Row Level Security on all tables
ALTER TABLE public.tctc_user_behavior ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_quiz_submission ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_quiz_redirections ENABLE ROW LEVEL SECURITY;

-- Check if policies exist before creating them
DO $$
BEGIN
    -- Policies for tctc_user_behavior
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_user_behavior' AND policyname = 'tctc_user_behavior_insert_policy') THEN
        CREATE POLICY tctc_user_behavior_insert_policy
            ON public.tctc_user_behavior
            FOR INSERT
            TO authenticated
            WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_user_behavior' AND policyname = 'tctc_user_behavior_select_policy') THEN
        CREATE POLICY tctc_user_behavior_select_policy
            ON public.tctc_user_behavior
            FOR SELECT
            TO authenticated
            USING (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_user_behavior' AND policyname = 'tctc_user_behavior_anon_insert_policy') THEN
        CREATE POLICY tctc_user_behavior_anon_insert_policy
            ON public.tctc_user_behavior
            FOR INSERT
            TO anon
            WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_user_behavior' AND policyname = 'tctc_user_behavior_anon_select_policy') THEN
        CREATE POLICY tctc_user_behavior_anon_select_policy
            ON public.tctc_user_behavior
            FOR SELECT
            TO anon
            USING (true);
    END IF;
    
    -- Policies for tctc_quiz_submission
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_submission' AND policyname = 'tctc_quiz_submission_insert_policy') THEN
        CREATE POLICY tctc_quiz_submission_insert_policy
            ON public.tctc_quiz_submission
            FOR INSERT
            TO authenticated
            WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_submission' AND policyname = 'tctc_quiz_submission_select_policy') THEN
        CREATE POLICY tctc_quiz_submission_select_policy
            ON public.tctc_quiz_submission
            FOR SELECT
            TO authenticated
            USING (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_submission' AND policyname = 'tctc_quiz_submission_anon_insert_policy') THEN
        CREATE POLICY tctc_quiz_submission_anon_insert_policy
            ON public.tctc_quiz_submission
            FOR INSERT
            TO anon
            WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_submission' AND policyname = 'tctc_quiz_submission_anon_select_policy') THEN
        CREATE POLICY tctc_quiz_submission_anon_select_policy
            ON public.tctc_quiz_submission
            FOR SELECT
            TO anon
            USING (true);
    END IF;
    
    -- Policies for tctc_quiz_redirections
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_redirections' AND policyname = 'tctc_quiz_redirections_insert_policy') THEN
        CREATE POLICY tctc_quiz_redirections_insert_policy
            ON public.tctc_quiz_redirections
            FOR INSERT
            TO authenticated
            WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_redirections' AND policyname = 'tctc_quiz_redirections_select_policy') THEN
        CREATE POLICY tctc_quiz_redirections_select_policy
            ON public.tctc_quiz_redirections
            FOR SELECT
            TO authenticated
            USING (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_redirections' AND policyname = 'tctc_quiz_redirections_anon_insert_policy') THEN
        CREATE POLICY tctc_quiz_redirections_anon_insert_policy
            ON public.tctc_quiz_redirections
            FOR INSERT
            TO anon
            WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tctc_quiz_redirections' AND policyname = 'tctc_quiz_redirections_anon_select_policy') THEN
        CREATE POLICY tctc_quiz_redirections_anon_select_policy
            ON public.tctc_quiz_redirections
            FOR SELECT
            TO anon
            USING (true);
    END IF;
END
$$;

-- Create a function to update the updated_at timestamp if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update the updated_at column if it doesn't exist
DROP TRIGGER IF EXISTS update_tctc_quiz_redirections_updated_at ON public.tctc_quiz_redirections;
CREATE TRIGGER update_tctc_quiz_redirections_updated_at
BEFORE UPDATE ON public.tctc_quiz_redirections
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Verify the policies
SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename IN ('tctc_user_behavior', 'tctc_quiz_submission', 'tctc_quiz_redirections')
ORDER BY tablename, policyname;
