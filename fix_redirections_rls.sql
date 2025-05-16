-- Drop existing RLS policies for tctc_quiz_redirections
DROP POLICY IF EXISTS tctc_quiz_redirections_insert_policy ON public.tctc_quiz_redirections;
DROP POLICY IF EXISTS tctc_quiz_redirections_select_policy ON public.tctc_quiz_redirections;
DROP POLICY IF EXISTS tctc_quiz_redirections_anon_insert_policy ON public.tctc_quiz_redirections;
DROP POLICY IF EXISTS tctc_quiz_redirections_anon_select_policy ON public.tctc_quiz_redirections;

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
