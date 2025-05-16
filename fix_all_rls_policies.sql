-- Drop existing RLS policies for tctc_user_behavior
DROP POLICY IF EXISTS tctc_user_behavior_insert_policy ON public.tctc_user_behavior;
DROP POLICY IF EXISTS tctc_user_behavior_select_policy ON public.tctc_user_behavior;
DROP POLICY IF EXISTS tctc_user_behavior_anon_insert_policy ON public.tctc_user_behavior;
DROP POLICY IF EXISTS tctc_user_behavior_anon_select_policy ON public.tctc_user_behavior;

-- Drop existing RLS policies for tctc_quiz_submission
DROP POLICY IF EXISTS tctc_quiz_submission_insert_policy ON public.tctc_quiz_submission;
DROP POLICY IF EXISTS tctc_quiz_submission_select_policy ON public.tctc_quiz_submission;
DROP POLICY IF EXISTS tctc_quiz_submission_anon_insert_policy ON public.tctc_quiz_submission;
DROP POLICY IF EXISTS tctc_quiz_submission_anon_select_policy ON public.tctc_quiz_submission;

-- Drop existing RLS policies for tctc_quiz_redirections
DROP POLICY IF EXISTS tctc_quiz_redirections_insert_policy ON public.tctc_quiz_redirections;
DROP POLICY IF EXISTS tctc_quiz_redirections_select_policy ON public.tctc_quiz_redirections;
DROP POLICY IF EXISTS tctc_quiz_redirections_anon_insert_policy ON public.tctc_quiz_redirections;
DROP POLICY IF EXISTS tctc_quiz_redirections_anon_select_policy ON public.tctc_quiz_redirections;

-- Enable RLS on all tables
ALTER TABLE public.tctc_user_behavior ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_quiz_submission ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_quiz_redirections ENABLE ROW LEVEL SECURITY;

-- Create policies for tctc_user_behavior
CREATE POLICY tctc_user_behavior_insert_policy
    ON public.tctc_user_behavior
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY tctc_user_behavior_select_policy
    ON public.tctc_user_behavior
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY tctc_user_behavior_anon_insert_policy
    ON public.tctc_user_behavior
    FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY tctc_user_behavior_anon_select_policy
    ON public.tctc_user_behavior
    FOR SELECT
    TO anon
    USING (true);

-- Create policies for tctc_quiz_submission
CREATE POLICY tctc_quiz_submission_insert_policy
    ON public.tctc_quiz_submission
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY tctc_quiz_submission_select_policy
    ON public.tctc_quiz_submission
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY tctc_quiz_submission_anon_insert_policy
    ON public.tctc_quiz_submission
    FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY tctc_quiz_submission_anon_select_policy
    ON public.tctc_quiz_submission
    FOR SELECT
    TO anon
    USING (true);

-- Create policies for tctc_quiz_redirections
CREATE POLICY tctc_quiz_redirections_insert_policy
    ON public.tctc_quiz_redirections
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY tctc_quiz_redirections_select_policy
    ON public.tctc_quiz_redirections
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY tctc_quiz_redirections_anon_insert_policy
    ON public.tctc_quiz_redirections
    FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY tctc_quiz_redirections_anon_select_policy
    ON public.tctc_quiz_redirections
    FOR SELECT
    TO anon
    USING (true);

-- Verify the policies
SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename IN ('tctc_user_behavior', 'tctc_quiz_submission', 'tctc_quiz_redirections')
ORDER BY tablename, policyname;
