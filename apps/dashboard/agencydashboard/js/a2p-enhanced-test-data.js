// Script to add enhanced test data to a2p_forms table
async function updateA2PFormsTestData() {
  console.log('💾 Adding enhanced test data to a2p_forms table...');
  
  // Initialize Supabase client
  const supabaseUrl = 'https://ehveemvdrzmnernsuuxv.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVodmVlbXZkcnptbmVybnN1dXh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0NjA2NTEsImV4cCI6MjA2MDAzNjY1MX0.A43KWW3G0kE_NgptszpaqC2-wFDGVPzGfcS7LFskV1E';
  const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);

  // Enhanced test data for A2P forms with more detailed fields
  const enhancedTestData = [
    {
      client_id: '4a4a8de1-10bb-4979-bbec-7517efff4b58',
      business_name: 'Sunshine Lashes',
      first_name: 'Sarah',
      last_name: 'Johnson',
      email: 'sarah@sunshinelashes.com',
      phone: '555-123-4567',
      subaccount_name: 'Sunshine Lashes Main',
      subaccount_id: 'SL-001',
      status: 'pending',
      submission_date: new Date().toISOString(),
      notes: 'Awaiting approval',
      created_at: new Date().toISOString()
    },
    {
      client_id: '76a2913e-ab92-4183-a824-dab76ef175f2',
      business_name: 'Glam Eyes Salon',
      first_name: 'Michael',
      last_name: 'Rodriguez',
      email: 'michael@glameyessalon.com',
      phone: '555-987-6543',
      subaccount_name: 'Glam Eyes Downtown',
      subaccount_id: 'GE-002',
      status: 'declined',
      submission_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
      notes: 'Business name issue',
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() // 3 days ago
    },
    {
      client_id: 'cb17d6c5-3b3d-4e74-97fa-3540295f65a2',
      business_name: 'Beauty Lash Studio',
      first_name: 'Jessica',
      last_name: 'Wong',
      email: 'jessica@beautylashstudio.com',
      phone: '555-234-5678',
      subaccount_name: 'Beauty Lash North',
      subaccount_id: 'BL-003',
      status: 'approved',
      submission_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
      notes: 'Approved by carrier',
      created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString() // 6 days ago
    },
    {
      client_id: 'e8f621a5-7cc4-48b4-9c1d-83a2e5f8e901',
      business_name: 'Lash & Brow Experts',
      first_name: 'David',
      last_name: 'Miller',
      email: 'david@lashbrowexperts.com',
      phone: '555-345-6789',
      subaccount_name: 'Lash & Brow Westside',
      subaccount_id: 'LB-004',
      status: 'pending',
      submission_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
      notes: 'Documentation under review',
      created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() // 1 day ago
    },
    {
      client_id: 'f2d53b7e-9a18-47c6-b83f-1204e7d95c63',
      business_name: 'Elite Beauty Solutions',
      first_name: 'Amanda',
      last_name: 'Parker',
      email: 'amanda@elitebeauty.com',
      phone: '555-456-7890',
      subaccount_name: 'Elite Beauty Eastside',
      subaccount_id: 'EB-005',
      status: 'approved',
      submission_date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), // 10 days ago
      notes: 'Fully approved and registered',
      created_at: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString() // 12 days ago
    }
  ];

  try {
    // Insert enhanced test data
    const { data, error } = await supabaseClient
      .from('a2p_forms')
      .upsert(enhancedTestData, { onConflict: 'client_id' });

    if (error) {
      console.error('❌ Error inserting enhanced test data:', error);
      return false;
    }

    console.log('✅ Enhanced test data added successfully!');
    return true;
  } catch (err) {
    console.error('❌ Unexpected error adding enhanced test data:', err);
    return false;
  }
}

// Function to enhance the A2P Pipeline display
async function enhanceA2PPipelineDisplay() {
  // Replace the existing loadA2PPipeline function
  window.loadA2PPipeline = async function() {
    console.log('🔄 Loading A2P Pipeline with enhanced data display...');
    
    try {
      // Clear existing cards
      const columns = ['a2p_pending_cards', 'a2p_approved_cards', 'a2p_declined_cards'];
      columns.forEach(columnId => {
        const column = document.getElementById(columnId);
        if (column) {
          console.log(`🧹 Clearing ${columnId}`);
          column.innerHTML = '';
        }
      });
      
      // Fetch A2P forms data from Supabase
      console.log('📊 Fetching A2P forms data...');
      const { data: entries, error } = await supabaseClient
        .from('a2p_forms')
        .select('*')
        .order('submission_date', { ascending: false });
      
      if (error) {
        console.error('❌ Error fetching A2P forms:', error);
        throw error;
      }
      
      console.log(`📋 Found ${entries?.length || 0} A2P entries:`, entries);
      
      // Process each entry
      if (entries && entries.length > 0) {
        entries.forEach(entry => {
          const status = entry.status || 'pending';
          let columnId;
          
          // Determine which column to add the card to
          if (status === 'approved' || status === 'a2p_approved') {
            columnId = 'a2p_approved_cards';
          } else if (status === 'declined' || status === 'a2p_declined') {
            columnId = 'a2p_declined_cards';
          } else {
            columnId = 'a2p_pending_cards';
          }
          
          const column = document.getElementById(columnId);
          if (!column) {
            console.warn(`⚠️ Column ${columnId} not found`);
            return;
          }
          
          // Create card element
          console.log(`🔷 Processing entry for ${entry.business_name || 'Unknown'}:`, entry);
          
          const card = document.createElement('div');
          card.className = 'bg-white border p-3 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer';
          
          // Format the submission date if it exists
          let formattedDate = 'No Date';
          if (entry.submission_date) {
            try {
              formattedDate = new Date(entry.submission_date).toLocaleDateString();
            } catch (err) {
              console.warn('⚠️ Error formatting date:', err);
            }
          }
          
          // Enhanced card content with more details
          card.innerHTML = `
            <div class="flex justify-between items-start">
              <strong class="text-lg block mb-2">${entry.business_name || 'Unknown Business'}</strong>
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                ${status === 'approved' || status === 'a2p_approved' ? 'bg-green-100 text-green-800' : 
                  status === 'declined' || status === 'a2p_declined' ? 'bg-red-100 text-red-800' : 
                  'bg-yellow-100 text-yellow-800'}">
                ${status.replace('a2p_', '').toUpperCase()}
              </span>
            </div>
            <p class="text-gray-700">${entry.first_name || ''} ${entry.last_name || ''}</p>
            <p class="text-gray-600 text-sm">${entry.subaccount_name || 'No subaccount'}</p>
            <div class="mt-2 pt-2 border-t border-gray-100">
              <p class="text-gray-600 text-sm">Submitted: ${formattedDate}</p>
              <p class="text-gray-500 text-xs mt-1">ID: ${entry.id ? entry.id.substring(0, 8) + '...' : 'N/A'}</p>
            </div>
          `;
          
          // Add click event listener for enhanced detail view
          card.addEventListener('click', function() {
            console.log('📝 Card clicked:', entry);
            
            // Create a modal dialog with enhanced details
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50';
            modal.setAttribute('id', 'a2p-detail-modal');
            
            modal.innerHTML = `
              <div class="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-lg font-medium">A2P Form Details</h3>
                  <button id="close-modal" class="text-gray-400 hover:text-gray-500">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Business Name</label>
                    <p class="mt-1">${entry.business_name || 'N/A'}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Subaccount</label>
                    <p class="mt-1">${entry.subaccount_name || 'N/A'}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">First Name</label>
                    <p class="mt-1">${entry.first_name || 'N/A'}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Last Name</label>
                    <p class="mt-1">${entry.last_name || 'N/A'}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Email</label>
                    <p class="mt-1">${entry.email || 'N/A'}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Phone</label>
                    <p class="mt-1">${entry.phone || 'N/A'}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Status</label>
                    <p class="mt-1">
                      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                        ${status === 'approved' || status === 'a2p_approved' ? 'bg-green-100 text-green-800' : 
                          status === 'declined' || status === 'a2p_declined' ? 'bg-red-100 text-red-800' : 
                          'bg-yellow-100 text-yellow-800'}">
                        ${status.replace('a2p_', '').toUpperCase()}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Submission Date</label>
                    <p class="mt-1">${formattedDate}</p>
                  </div>
                  <div class="col-span-2">
                    <label class="text-sm font-medium text-gray-500">Notes</label>
                    <p class="mt-1">${entry.notes || 'No notes'}</p>
                  </div>
                  <div class="col-span-2">
                    <label class="text-sm font-medium text-gray-500">ID</label>
                    <p class="mt-1 text-sm font-mono">${entry.id || 'N/A'}</p>
                  </div>
                </div>
                
                <div class="mt-6">
                  <button id="close-modal-btn" class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                    Close
                  </button>
                </div>
              </div>
            `;
            
            document.body.appendChild(modal);
            
            // Handle closing the modal
            document.getElementById('close-modal').addEventListener('click', function() {
              document.body.removeChild(modal);
            });
            
            document.getElementById('close-modal-btn').addEventListener('click', function() {
              document.body.removeChild(modal);
            });
            
            // Close modal when clicking outside
            modal.addEventListener('click', function(e) {
              if (e.target === modal) {
                document.body.removeChild(modal);
              }
            });
          });
          
          // Add card to appropriate column
          console.log(`📍 Adding card to ${columnId}`);
          column.appendChild(card);
        });
      } else {
        console.log('ℹ️ No A2P entries found');
        columns.forEach(columnId => {
          const column = document.getElementById(columnId);
          if (column) {
            column.innerHTML = `
              <div class="bg-gray-50 border border-gray-200 p-4 rounded-lg text-gray-700">
                <p class="font-medium">No entries found</p>
                <p class="text-sm mt-1">No A2P form submissions in this category.</p>
              </div>
            `;
          }
        });
      }
      
      console.log('✅ Enhanced A2P Pipeline loaded successfully');
      
    } catch (err) {
      console.error('❌ Error in loadA2PPipeline:', err);
      console.error('Stack trace:', err.stack);
      
      // Show error message in each column
      const columns = ['a2p_pending_cards', 'a2p_approved_cards', 'a2p_declined_cards'];
      columns.forEach(columnId => {
        const column = document.getElementById(columnId);
        if (column) {
          column.innerHTML = `
            <div class="bg-red-50 border border-red-200 p-4 rounded-lg text-red-700">
              <p class="font-medium">Failed to load A2P Pipeline</p>
              <p class="text-sm mt-1">Please try refreshing the page or check the console for details.</p>
            </div>
          `;
        }
      });
    }
  };
  
  // Reload the pipeline with enhanced display
  await window.loadA2PPipeline();
  
  console.log('✅ A2P Pipeline display enhanced successfully');
  return true;
}

// Usage instructions
console.log(`
Instructions for updating A2P forms test data with enhanced fields:

1. Open your browser console on the clinehelpnowcursor.html page
2. Copy and paste this entire file into the console
3. Run: await updateA2PFormsTestData()
4. To enhance the display with new fields, run: await enhanceA2PPipelineDisplay()
5. The pipeline should automatically refresh with the enhanced data and display

Note: This requires the a2p_forms table to exist in your Supabase database.
If you need to add new columns to your a2p_forms table, here are the recommended columns:
- first_name (text)
- last_name (text)
- email (text)
- phone (text)
- subaccount_name (text)
- subaccount_id (text)
- created_at (timestamp)
`); 