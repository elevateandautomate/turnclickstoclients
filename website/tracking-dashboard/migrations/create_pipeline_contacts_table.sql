-- Create pipeline_contacts table for sales pipeline
CREATE TABLE IF NOT EXISTS pipeline_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    business TEXT,
    email TEXT,
    phone TEXT,
    niche TEXT,
    score INTEGER,
    result TEXT,
    stage TEXT NOT NULL,
    lastContact TEXT,
    next_action TEXT,
    due_date TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on stage for faster queries
CREATE INDEX IF NOT EXISTS idx_pipeline_contacts_stage ON pipeline_contacts(stage);

-- Create index on niche for filtering
CREATE INDEX IF NOT EXISTS idx_pipeline_contacts_niche ON pipeline_contacts(niche);

-- Add comment to table
COMMENT ON TABLE pipeline_contacts IS 'Stores contact information for the sales pipeline';
