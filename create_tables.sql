-- Create the tctc_user_behavior table
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
    traffic_source TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    user_agent TEXT,
    screen_width INTEGER,
    screen_height INTEGER
);

-- Create the tctc_quiz_submission table
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

-- Create the tctc_quiz_redirections table
CREATE TABLE IF NOT EXISTS public.tctc_quiz_redirections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    user_first_name TEXT,
    user_last_name TEXT,
    user_business_name TEXT,
    quiz_score INTEGER,
    outcome_bucket TEXT,
    awareness_variant TEXT,
    redirect_url TEXT,
    source TEXT,
    redirected_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create RLS policies for tctc_user_behavior
ALTER TABLE public.tctc_user_behavior ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all authenticated users to insert into tctc_user_behavior
CREATE POLICY tctc_user_behavior_insert_policy
    ON public.tctc_user_behavior
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Create a policy that allows all authenticated users to select from tctc_user_behavior
CREATE POLICY tctc_user_behavior_select_policy
    ON public.tctc_user_behavior
    FOR SELECT
    TO authenticated
    USING (true);

-- Create a policy that allows anonymous users to insert into tctc_user_behavior
CREATE POLICY tctc_user_behavior_anon_insert_policy
    ON public.tctc_user_behavior
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create a policy that allows anonymous users to select from tctc_user_behavior
CREATE POLICY tctc_user_behavior_anon_select_policy
    ON public.tctc_user_behavior
    FOR SELECT
    TO anon
    USING (true);

-- Create RLS policies for tctc_quiz_submission
ALTER TABLE public.tctc_quiz_submission ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all authenticated users to insert into tctc_quiz_submission
CREATE POLICY tctc_quiz_submission_insert_policy
    ON public.tctc_quiz_submission
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Create a policy that allows all authenticated users to select from tctc_quiz_submission
CREATE POLICY tctc_quiz_submission_select_policy
    ON public.tctc_quiz_submission
    FOR SELECT
    TO authenticated
    USING (true);

-- Create a policy that allows anonymous users to insert into tctc_quiz_submission
CREATE POLICY tctc_quiz_submission_anon_insert_policy
    ON public.tctc_quiz_submission
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create a policy that allows anonymous users to select from tctc_quiz_submission
CREATE POLICY tctc_quiz_submission_anon_select_policy
    ON public.tctc_quiz_submission
    FOR SELECT
    TO anon
    USING (true);

-- Create RLS policies for tctc_quiz_redirections
ALTER TABLE public.tctc_quiz_redirections ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all authenticated users to insert into tctc_quiz_redirections
CREATE POLICY tctc_quiz_redirections_insert_policy
    ON public.tctc_quiz_redirections
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Create a policy that allows all authenticated users to select from tctc_quiz_redirections
CREATE POLICY tctc_quiz_redirections_select_policy
    ON public.tctc_quiz_redirections
    FOR SELECT
    TO authenticated
    USING (true);

-- Create a policy that allows anonymous users to insert into tctc_quiz_redirections
CREATE POLICY tctc_quiz_redirections_anon_insert_policy
    ON public.tctc_quiz_redirections
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create a policy that allows anonymous users to select from tctc_quiz_redirections
CREATE POLICY tctc_quiz_redirections_anon_select_policy
    ON public.tctc_quiz_redirections
    FOR SELECT
    TO anon
    USING (true);
