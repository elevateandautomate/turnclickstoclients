/**
 * Supabase Configuration
 * 
 * This file contains configuration for connecting to Supabase.
 * Replace the placeholders with your actual Supabase URL and API key.
 */

// Supabase configuration
const SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDY4MzA0NzcsImV4cCI6MjAyMjQwNjQ3N30.Nh83ebqzf1iGHTaGywss6WIkkNlUUWlUKTDrCLOhkpY';

/**
 * Fetch data from Supabase
 * 
 * @param {string} table - The table to fetch from
 * @param {string} query - The query string (e.g., '?select=*&limit=10')
 * @returns {Promise<Array>} - The fetched data
 */
async function fetchFromSupabase(table, query = '') {
    console.log(`Fetching from ${table} with query ${query}...`);
    
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/${table}${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`Fetched ${data.length} items from ${table}`);
        return data;
    } catch (error) {
        console.error(`Error fetching from ${table}:`, error);
        return [];
    }
}

/**
 * Insert data into Supabase
 * 
 * @param {string} table - The table to insert into
 * @param {Object} data - The data to insert
 * @returns {Promise<Object>} - The inserted data
 */
async function insertIntoSupabase(table, data) {
    console.log(`Inserting into ${table}:`, data);
    
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`Successfully inserted into ${table}:`, result);
        return result;
    } catch (error) {
        console.error(`Error inserting into ${table}:`, error);
        throw error;
    }
}

/**
 * Update data in Supabase
 * 
 * @param {string} table - The table to update
 * @param {string} query - The query string (e.g., '?id=eq.123')
 * @param {Object} data - The data to update
 * @returns {Promise<Object>} - The updated data
 */
async function updateInSupabase(table, query, data) {
    console.log(`Updating ${table} with query ${query}:`, data);
    
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/${table}${query}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`Successfully updated ${table}:`, result);
        return result;
    } catch (error) {
        console.error(`Error updating ${table}:`, error);
        throw error;
    }
}
