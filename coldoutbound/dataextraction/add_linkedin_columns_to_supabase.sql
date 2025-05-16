-- SQL file to add LinkedIn columns to the core_data table

-- Add linkedin_connected column (boolean)
ALTER TABLE core_data 
ADD COLUMN IF NOT EXISTS linkedin_connected BOOLEAN DEFAULT FALSE;

-- Add linkedin_connected_message column (text)
ALTER TABLE core_data 
ADD COLUMN IF NOT EXISTS linkedin_connected_message TEXT DEFAULT '';

-- Add linkedin_connected_timestamp column (timestamp with timezone)
ALTER TABLE core_data 
ADD COLUMN IF NOT EXISTS linkedin_connected_timestamp TIMESTAMPTZ;

-- Comment explaining the purpose of these columns
COMMENT ON COLUMN core_data.linkedin_connected IS 'Boolean flag indicating if a LinkedIn connection request was successfully sent';
COMMENT ON COLUMN core_data.linkedin_connected_message IS 'Message describing the result of the LinkedIn connection attempt';
COMMENT ON COLUMN core_data.linkedin_connected_timestamp IS 'Timestamp when the LinkedIn connection was attempted';
