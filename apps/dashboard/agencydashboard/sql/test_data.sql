-- First, clear existing data
DELETE FROM client_metrics_live;

-- Insert random data for 10 brands over the past 7 days
WITH brands AS (
  SELECT unnest(ARRAY[
    'BeautyHub',
    'SpaConnect',
    'StyleMaster',
    'GlamTech',
    'WellnessOne',
    'BeautyPro',
    'LuxSalon',
    'ElegancePlus',
    'ChicStyle',
    'VogueVibe'
  ]) AS brand_name
),
dates AS (
  SELECT generate_series(
    current_date - interval '7 days',
    current_date,
    interval '1 day'
  )::date AS created_date
)
INSERT INTO client_metrics_live (
  brand,
  subaccount_id,
  leads,
  confirmed,
  unconfirmed,
  shows,
  no_shows,
  response_time,
  created_at
)
SELECT 
  brand_name,
  lower(brand_name) || '_' || to_char(created_date, 'YYYYMMDD') AS subaccount_id,
  -- Random leads between 50 and 200
  floor(random() * (200-50+1) + 50)::int AS leads,
  -- Random confirmed appointments (30-70% of leads)
  floor(random() * (0.7-0.3+1) + 0.3 * floor(random() * (200-50+1) + 50))::int AS confirmed,
  -- Random unconfirmed (10-30% of leads)
  floor(random() * (0.3-0.1+1) + 0.1 * floor(random() * (200-50+1) + 50))::int AS unconfirmed,
  -- Random show rate between 40% and 90%
  floor(random() * (90-40+1) + 40)::int AS shows,
  -- Random no-shows between 5% and 20%
  floor(random() * (20-5+1) + 5)::int AS no_shows,
  -- Random response time between 1 and 5 minutes
  (random() * (5-1) + 1)::numeric(3,1) AS response_time,
  created_date AS created_at
FROM brands
CROSS JOIN dates
ORDER BY created_date DESC;

-- Add some interesting patterns:

-- Make BeautyHub consistently high performer
UPDATE client_metrics_live 
SET leads = leads + 100
WHERE brand = 'BeautyHub';

-- Make GlamTech show rapid growth
UPDATE client_metrics_live 
SET leads = leads + (
  EXTRACT(DAY FROM (current_date - created_at)) * 20
)
WHERE brand = 'GlamTech';

-- Make WellnessOne show declining trend
UPDATE client_metrics_live 
SET leads = leads - (
  EXTRACT(DAY FROM (current_date - created_at)) * 15
)
WHERE brand = 'WellnessOne';

-- Add some randomness to response times
UPDATE client_metrics_live 
SET response_time = 
  CASE 
    WHEN random() < 0.1 THEN response_time::numeric + 3.0 -- Occasional spikes
    WHEN random() < 0.2 THEN response_time::numeric - 0.5 -- Some improvements
    ELSE response_time::numeric
  END::numeric(3,1);

-- Ensure show rates make sense
UPDATE client_metrics_live 
SET 
  shows = LEAST(shows, confirmed),
  no_shows = LEAST(no_shows, confirmed);

-- Add some weekend variation
UPDATE client_metrics_live 
SET leads = leads * 0.7
WHERE EXTRACT(DOW FROM created_at) IN (0, 6); -- Weekend days

-- Ensure all metrics are positive
UPDATE client_metrics_live 
SET 
  leads = GREATEST(leads, 10),
  confirmed = GREATEST(confirmed, 5),
  unconfirmed = GREATEST(unconfirmed, 2),
  shows = GREATEST(shows, 3),
  no_shows = GREATEST(no_shows, 1),
  response_time = GREATEST(response_time::numeric, 0.5)::numeric(3,1); 