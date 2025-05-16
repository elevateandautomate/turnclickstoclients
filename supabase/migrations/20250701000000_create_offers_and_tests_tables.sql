-- Create tables for Offers & Split Tests functionality
-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the tctc_offers table
CREATE TABLE IF NOT EXISTS public.tctc_offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    name TEXT NOT NULL,
    niche TEXT NOT NULL,
    headline TEXT NOT NULL,
    description TEXT,
    cta_text TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by TEXT,
    is_auto_generated BOOLEAN DEFAULT false,
    ml_confidence_score FLOAT,
    ml_generation_params JSONB
);

-- Create the tctc_split_tests table
CREATE TABLE IF NOT EXISTS public.tctc_split_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    name TEXT NOT NULL,
    niche TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active', -- active, paused, completed
    start_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    end_date TIMESTAMP WITH TIME ZONE,
    duration_days INTEGER NOT NULL DEFAULT 14,
    is_auto_generated BOOLEAN DEFAULT false,
    ml_confidence_score FLOAT,
    ml_generation_params JSONB,
    winner_variant_id UUID,
    created_by TEXT
);

-- Create the tctc_test_variants table
CREATE TABLE IF NOT EXISTS public.tctc_test_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    test_id UUID NOT NULL REFERENCES public.tctc_split_tests(id) ON DELETE CASCADE,
    offer_id UUID NOT NULL REFERENCES public.tctc_offers(id),
    variant_name TEXT NOT NULL,
    traffic_weight INTEGER NOT NULL DEFAULT 50, -- percentage
    is_control BOOLEAN DEFAULT false
);

-- Create the tctc_test_results table
CREATE TABLE IF NOT EXISTS public.tctc_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    test_id UUID NOT NULL REFERENCES public.tctc_split_tests(id) ON DELETE CASCADE,
    variant_id UUID NOT NULL REFERENCES public.tctc_test_variants(id) ON DELETE CASCADE,
    impressions INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    date_recorded DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Create the tctc_ml_insights table for storing machine learning insights
CREATE TABLE IF NOT EXISTS public.tctc_ml_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    niche TEXT NOT NULL,
    insight_type TEXT NOT NULL, -- 'audience_segment', 'offer_recommendation', 'test_recommendation'
    insight_data JSONB NOT NULL,
    confidence_score FLOAT,
    is_applied BOOLEAN DEFAULT false,
    applied_to_id UUID, -- ID of offer or test where this insight was applied
    source_data_hash TEXT -- Hash of the source data used to generate this insight
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tctc_offers_niche ON public.tctc_offers(niche);
CREATE INDEX IF NOT EXISTS idx_tctc_offers_target_audience ON public.tctc_offers(target_audience);
CREATE INDEX IF NOT EXISTS idx_tctc_offers_is_active ON public.tctc_offers(is_active);

CREATE INDEX IF NOT EXISTS idx_tctc_split_tests_niche ON public.tctc_split_tests(niche);
CREATE INDEX IF NOT EXISTS idx_tctc_split_tests_status ON public.tctc_split_tests(status);
CREATE INDEX IF NOT EXISTS idx_tctc_split_tests_start_date ON public.tctc_split_tests(start_date);

CREATE INDEX IF NOT EXISTS idx_tctc_test_variants_test_id ON public.tctc_test_variants(test_id);
CREATE INDEX IF NOT EXISTS idx_tctc_test_variants_offer_id ON public.tctc_test_variants(offer_id);

CREATE INDEX IF NOT EXISTS idx_tctc_test_results_test_id ON public.tctc_test_results(test_id);
CREATE INDEX IF NOT EXISTS idx_tctc_test_results_variant_id ON public.tctc_test_results(variant_id);
CREATE INDEX IF NOT EXISTS idx_tctc_test_results_date_recorded ON public.tctc_test_results(date_recorded);

CREATE INDEX IF NOT EXISTS idx_tctc_ml_insights_niche ON public.tctc_ml_insights(niche);
CREATE INDEX IF NOT EXISTS idx_tctc_ml_insights_insight_type ON public.tctc_ml_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_tctc_ml_insights_is_applied ON public.tctc_ml_insights(is_applied);

-- Create RLS policies
ALTER TABLE public.tctc_offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_split_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_test_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tctc_ml_insights ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Allow authenticated users to select tctc_offers"
    ON public.tctc_offers FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert tctc_offers"
    ON public.tctc_offers FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update tctc_offers"
    ON public.tctc_offers FOR UPDATE
    TO authenticated
    USING (true);

-- Similar policies for other tables
CREATE POLICY "Allow authenticated users to select tctc_split_tests"
    ON public.tctc_split_tests FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert tctc_split_tests"
    ON public.tctc_split_tests FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update tctc_split_tests"
    ON public.tctc_split_tests FOR UPDATE
    TO authenticated
    USING (true);

-- Test variants policies
CREATE POLICY "Allow authenticated users to select tctc_test_variants"
    ON public.tctc_test_variants FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert tctc_test_variants"
    ON public.tctc_test_variants FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update tctc_test_variants"
    ON public.tctc_test_variants FOR UPDATE
    TO authenticated
    USING (true);

-- Test results policies
CREATE POLICY "Allow authenticated users to select tctc_test_results"
    ON public.tctc_test_results FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert tctc_test_results"
    ON public.tctc_test_results FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update tctc_test_results"
    ON public.tctc_test_results FOR UPDATE
    TO authenticated
    USING (true);

-- ML insights policies
CREATE POLICY "Allow authenticated users to select tctc_ml_insights"
    ON public.tctc_ml_insights FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert tctc_ml_insights"
    ON public.tctc_ml_insights FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update tctc_ml_insights"
    ON public.tctc_ml_insights FOR UPDATE
    TO authenticated
    USING (true);
