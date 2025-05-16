// Script to add test data to a2p_forms table
async function addTestA2PData() {
  console.log('💾 Adding test data to a2p_forms table...');
  
  // Initialize Supabase client
  const supabaseUrl = 'https://ehveemvdrzmnernsuuxv.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVodmVlbXZkcnptbmVybnN1dXh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0NjA2NTEsImV4cCI6MjA2MDAzNjY1MX0.A43KWW3G0kE_NgptszpaqC2-wFDGVPzGfcS7LFskV1E';
  const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);

  // Test data for A2P forms
  const testData = [
    {
      client_id: '4a4a8de1-10bb-4979-bbec-7517efff4b58',
      business_name: 'Sunshine Lashes',
      status: 'pending',
      submission_date: new Date().toISOString(),
      notes: 'Awaiting approval'
    },
    {
      client_id: '76a2913e-ab92-4183-a824-dab76ef175f2',
      business_name: 'Glam Eyes Salon',
      status: 'declined',
      submission_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
      notes: 'Business name issue'
    },
    {
      client_id: 'cb17d6c5-3b3d-4e74-97fa-3540295f65a2',
      business_name: 'Beauty Lash Studio',
      status: 'approved',
      submission_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
      notes: 'Approved by carrier'
    }
  ];

  try {
    // Insert test data
    const { data, error } = await supabaseClient
      .from('a2p_forms')
      .upsert(testData, { onConflict: 'client_id' });

    if (error) {
      console.error('❌ Error inserting test data:', error);
      return false;
    }

    console.log('✅ Test data added successfully!');
    return true;
  } catch (err) {
    console.error('❌ Unexpected error adding test data:', err);
    return false;
  }
}

// Function to check if the a2p_forms table exists
async function checkAndCreateA2PTable() {
  console.log('🔍 Checking a2p_forms table...');

  // Initialize Supabase client
  const supabaseUrl = 'https://ehveemvdrzmnernsuuxv.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVodmVlbXZkcnptbmVybnN1dXh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0NjA2NTEsImV4cCI6MjA2MDAzNjY1MX0.A43KWW3G0kE_NgptszpaqC2-wFDGVPzGfcS7LFskV1E';
  const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);

  try {
    // Check if table exists by trying to count rows
    const { error } = await supabaseClient
      .from('a2p_forms')
      .select('count', { count: 'exact', head: true });

    if (error) {
      // Table might not exist, create it
      console.log('⚠️ a2p_forms table not found, creating it...');
      
      // This requires admin privileges and might not work in browser context
      // You would typically do this on the server side or using migrations
      /* 
      const { error: createError } = await supabaseClient.rpc('create_a2p_forms_table');
      if (createError) {
        console.error('❌ Error creating table:', createError);
        return false;
      }
      */
      
      alert('The a2p_forms table does not exist. Please create it in the Supabase dashboard with the following columns: id (uuid), client_id (uuid), business_name (text), status (text), submission_date (timestamp), notes (text)');
      return false;
    }

    console.log('✅ a2p_forms table exists');
    return true;
  } catch (err) {
    console.error('❌ Error checking table:', err);
    return false;
  }
}

// Usage instructions
console.log(`
Instructions for adding test data to a2p_forms table:

1. Open your browser console on the clinehelpnowcursor.html page
2. Copy and paste this entire file into the console
3. Run: await checkAndCreateA2PTable()
4. If the table exists, run: await addTestA2PData()
5. Refresh the page and check the A2P pipeline

Note: This requires the a2p_forms table to exist in your Supabase database.
`); 