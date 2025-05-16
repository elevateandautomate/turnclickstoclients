-- Create dashboard_metrics table
CREATE TABLE IF NOT EXISTS public.dashboard_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    leads_today INTEGER DEFAULT 0,
    appointments_today INTEGER DEFAULT 0,
    show_rate DECIMAL DEFAULT 0,
    cancellation_rate DECIMAL DEFAULT 0,
    leads_change DECIMAL DEFAULT 0,
    appointments_change DECIMAL DEFAULT 0,
    show_rate_change DECIMAL DEFAULT 0,
    cancellation_rate_change DECIMAL DEFAULT 0
);

-- Create client_tracking table
CREATE TABLE IF NOT EXISTS public.client_tracking (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    brand TEXT NOT NULL,
    leads INTEGER DEFAULT 0,
    confirmed INTEGER DEFAULT 0,
    showed INTEGER DEFAULT 0,
    no_show INTEGER DEFAULT 0
);

-- Create leads table
CREATE TABLE IF NOT EXISTS public.leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    brand TEXT,
    status TEXT DEFAULT 'pending'::text,
    source TEXT
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS public.appointments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    client_id UUID REFERENCES public.leads(id),
    status TEXT DEFAULT 'scheduled'::text,
    brand TEXT,
    notes TEXT
);

-- Drop existing tables if they exist
DROP TABLE IF EXISTS public.a2p_forms CASCADE;
DROP TABLE IF EXISTS public.client_onboarding CASCADE;

-- Create client_onboarding table with correct stage names from the start
CREATE TABLE IF NOT EXISTS public.client_onboarding (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    client_name TEXT NOT NULL,
    business_name TEXT,
    subaccount_name TEXT,
    subaccount_id TEXT,
    subaccount_api_key TEXT,
    subaccount_calendar_url TEXT,
    stage TEXT CHECK (stage IN (
        'Application Submitted',
        'Getting Started Guide Complete',
        'New Client',
        'Onboarding Started',
        'Info Verified + Agreement Complete',
        'Slack Support Group Joined',
        'Campaign Domain Selected',
        'Social Media Integrated',
        'A2P Form Submission',
        'A2P Pending',
        'A2P Approved',
        'A2P Declined',
        'Ad Launch',
        'Live'
    )) DEFAULT 'Application Submitted',
    status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'active')) DEFAULT 'pending',
    email TEXT,
    phone TEXT,
    notes TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_client_onboarding_stage 
    ON client_onboarding(stage);
CREATE INDEX IF NOT EXISTS idx_client_onboarding_status 
    ON client_onboarding(status);
CREATE INDEX IF NOT EXISTS idx_client_onboarding_subaccount 
    ON client_onboarding(subaccount_name);
CREATE INDEX IF NOT EXISTS idx_client_onboarding_last_updated 
    ON client_onboarding(last_updated);

-- Create a2p_forms table for tracking A2P form submissions
CREATE TABLE IF NOT EXISTS public.a2p_forms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    client_id UUID REFERENCES client_onboarding(id),
    status TEXT CHECK (status IN ('pending', 'approved', 'declined')) DEFAULT 'pending',
    submission_date TIMESTAMP WITH TIME ZONE,
    approval_date TIMESTAMP WITH TIME ZONE,
    declined_date TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Create indexes for a2p_forms
CREATE INDEX IF NOT EXISTS idx_a2p_forms_client_id 
    ON a2p_forms(client_id);
CREATE INDEX IF NOT EXISTS idx_a2p_forms_status 
    ON a2p_forms(status);

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON TABLE client_onboarding TO authenticated;
GRANT ALL PRIVILEGES ON TABLE client_onboarding TO service_role;
GRANT ALL PRIVILEGES ON TABLE a2p_forms TO authenticated;
GRANT ALL PRIVILEGES ON TABLE a2p_forms TO service_role;

-- Insert sample data into dashboard_metrics
INSERT INTO public.dashboard_metrics (
    leads_today,
    appointments_today,
    show_rate,
    cancellation_rate,
    leads_change,
    appointments_change,
    show_rate_change,
    cancellation_rate_change
) VALUES (
    25,
    15,
    80.0,
    20.0,
    5.0,
    10.0,
    2.0,
    -5.0
);

-- Insert sample data into client_tracking
INSERT INTO public.client_tracking (
    brand,
    leads,
    confirmed,
    showed,
    no_show
) VALUES 
('Brand A', 10, 8, 6, 2),
('Brand B', 15, 12, 10, 2),
('Brand C', 20, 15, 12, 3);

-- Insert sample data for testing
INSERT INTO public.leads (first_name, last_name, email, phone, brand, status, source)
VALUES 
    ('John', 'Doe', 'john@example.com', '1234567890', 'Brand A', 'pending', 'website'),
    ('Jane', 'Smith', 'jane@example.com', '0987654321', 'Brand B', 'contacted', 'referral');

INSERT INTO public.appointments (date, client_id, status, brand, notes)
VALUES 
    (NOW(), (SELECT id FROM public.leads WHERE email = 'john@example.com'), 'scheduled', 'Brand A', 'Initial consultation'),
    (NOW() + INTERVAL '1 day', (SELECT id FROM public.leads WHERE email = 'jane@example.com'), 'confirmed', 'Brand B', 'Follow-up meeting');

-- Insert sample data into client_onboarding
INSERT INTO public.client_onboarding (
    client_name,
    business_name,
    subaccount_name,
    subaccount_id,
    email,
    phone,
    stage,
    status,
    notes,
    last_updated
) VALUES 
    ('John Smith', 'Smith Dental', 'Smith Dental Main', 'SD001', 'john@smithdental.com', '+1 (555) 123-4567', 'Slack Support Group Joined', 'active', 'Ready for A2P submission', NOW()),
    ('Sarah Johnson', 'Johnson Law', 'Johnson Law Group', 'JL001', 'sarah@johnsonlaw.com', '+1 (555) 234-5678', 'Campaign Domain Selected', 'active', 'Domain selection in progress', NOW()),
    ('Mike Wilson', 'Wilson Medical', 'Wilson Med Group', 'WM001', 'mike@wilsonmedical.com', '+1 (555) 345-6789', 'Social Media Integrated', 'active', 'Social media setup in progress', NOW()),
    ('Lisa Brown', 'Brown Therapy', 'Brown Therapy Group', 'BT001', 'lisa@browntherapy.com', '+1 (555) 456-7890', 'Slack Support Group Joined', 'active', 'Joined Slack channel', NOW()),
    ('David Chen', 'Chen Accounting', 'Chen Financial', 'CF001', 'david@chenaccounting.com', '+1 (555) 567-8901', 'Campaign Domain Selected', 'active', 'Reviewing domain options', NOW()),
    ('Emily White', 'White Wellness', 'White Wellness Center', 'WW001', 'emily@whitewellness.com', '+1 (555) 678-9012', 'Social Media Integrated', 'active', 'Instagram integration pending', NOW()),
    ('Rachel Green', 'Green Marketing', 'Green Marketing Solutions', 'GM001', 'rachel@greenmarketing.com', '+1 (555) 789-0123', 'Getting Started Guide Complete', 'active', 'Initial consultation completed', NOW()),
    ('Tom Anderson', 'Anderson Fitness', 'Anderson Fitness Pro', 'AF001', 'tom@andersonfitness.com', '+1 (555) 890-1234', 'Getting Started Guide Complete', 'active', 'Setting up GHL account', NOW()),
    ('Karen Martinez', 'Martinez Real Estate', 'Martinez Properties', 'MP001', 'karen@martinezrealty.com', '+1 (555) 901-2345', 'Getting Started Guide Complete', 'active', 'Working through guide', NOW());

-- Insert sample data into a2p_forms
INSERT INTO public.a2p_forms (
    client_id,
    status,
    submission_date,
    notes
) VALUES 
    ((SELECT id FROM client_onboarding WHERE client_name = 'John Smith'), 'pending', NOW(), 'Initial submission under review'),
    ((SELECT id FROM client_onboarding WHERE client_name = 'Sarah Johnson'), 'declined', NOW() - INTERVAL '2 days', 'Missing business documentation'),
    ((SELECT id FROM client_onboarding WHERE client_name = 'Mike Wilson'), 'approved', NOW() - INTERVAL '5 days', 'All requirements met');

-- Check if tables exist and create them if they don't
DO $$
BEGIN
    -- Create leads table if it doesn't exist
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'leads') THEN
        CREATE TABLE public.leads (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            brand TEXT,
            status TEXT DEFAULT 'pending'::text,
            source TEXT
        );
        
        -- Insert sample data
        INSERT INTO public.leads (first_name, last_name, email, phone, brand, status, source)
        VALUES 
            ('John', 'Doe', 'john@example.com', '1234567890', 'Brand A', 'pending', 'website'),
            ('Jane', 'Smith', 'jane@example.com', '0987654321', 'Brand B', 'contacted', 'referral');
    END IF;

    -- Create appointments table if it doesn't exist
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'appointments') THEN
        CREATE TABLE public.appointments (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
            date TIMESTAMP WITH TIME ZONE NOT NULL,
            client_id UUID REFERENCES public.leads(id),
            status TEXT DEFAULT 'scheduled'::text,
            brand TEXT,
            notes TEXT
        );
        
        -- Insert sample data
        INSERT INTO public.appointments (date, client_id, status, brand, notes)
        VALUES 
            (NOW(), (SELECT id FROM public.leads WHERE email = 'john@example.com'), 'scheduled', 'Brand A', 'Initial consultation'),
            (NOW() + INTERVAL '1 day', (SELECT id FROM public.leads WHERE email = 'jane@example.com'), 'confirmed', 'Brand B', 'Follow-up meeting');
    END IF;

    -- Create client_onboarding table if it doesn't exist
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'client_onboarding') THEN
        CREATE TABLE public.client_onboarding (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
            client_name TEXT,
            business_name TEXT,
            stage TEXT CHECK (stage IN ('Application Submitted', 'Getting Started Guide Complete', 'New Client', 'Onboarding Started', 'Slack Support Group Joined', 'Campaign Domain Selected', 'Social Media Integrated', 'A2P Form Submission', 'A2P Pending', 'A2P Approved', 'A2P Declined', 'Ad Launch', 'Live')),
            status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked'))
        );
        
        -- Insert sample data
        INSERT INTO public.client_onboarding (client_name, business_name, stage, status)
        VALUES 
            ('John Doe', 'Doe Enterprises', 'Application Submitted', 'pending'),
            ('Jane Smith', 'Smith & Co', 'Getting Started Guide Complete', 'in_progress');
    END IF;
END $$; 

-- Update the CHECK constraint for the stage column to match UI stage names
ALTER TABLE public.client_onboarding DROP CONSTRAINT IF EXISTS client_onboarding_stage_check;
ALTER TABLE public.client_onboarding ADD CONSTRAINT client_onboarding_stage_check 
    CHECK (stage IN (
        'Application Submitted',
        'Getting Started Guide Complete',
        'New Client',
        'Onboarding Started',
        'Slack Support Group Joined',
        'Campaign Domain Selected',
        'Social Media Integrated',
        'A2P Form Submission',
        'A2P Pending',
        'A2P Approved',
        'A2P Declined',
        'Ad Launch',
        'Live'
    )); 