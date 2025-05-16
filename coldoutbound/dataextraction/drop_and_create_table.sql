-- Drop the existing table
DROP TABLE IF EXISTS public.contact_bot_brain;

-- Create the table with the correct schema
CREATE TABLE public.contact_bot_brain (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT,
    field_attributes JSONB,
    field_type TEXT,
    source TEXT,
    success BOOLEAN DEFAULT true,
    model_data TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.contact_bot_brain ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users" ON public.contact_bot_brain
    FOR SELECT USING (true);
    
CREATE POLICY "Enable insert for authenticated users only" ON public.contact_bot_brain
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');
    
CREATE POLICY "Enable update for authenticated users only" ON public.contact_bot_brain
    FOR UPDATE USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');
