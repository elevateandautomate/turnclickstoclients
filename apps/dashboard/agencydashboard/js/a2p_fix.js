// Fix for A2P Pipeline in clinehelpnowcursor.html
// Copy and paste these changes into the appropriate locations

// 1. Find the loadA2PPipeline function around line 3550
// Replace the status mapping line with:
const status = 'a2p_' + (entry.status || 'pending');

// 2. Update the Supabase query to only select fields we know exist:
const { data, error } = await supabaseClient
    .from('a2p_forms')
    .select('id, created_at, client_id, status, submission_date')
    .order('created_at', { ascending: false });

// 3. Update the card creation code:
// Create card HTML
const card = document.createElement('div');
card.className = 'bg-white border p-3 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200';

// Format the submission date
const submissionDate = new Date(entry.submission_date).toLocaleDateString();

card.innerHTML = `
    <strong class="text-lg block mb-2">Client ID: ${entry.client_id}</strong>
    <p class="text-gray-600">Submitted: ${submissionDate}</p>
    <p class="text-gray-600 mt-1">
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
            ${status === 'a2p_approved' ? 'bg-green-100 text-green-800' : 
              status === 'a2p_declined' ? 'bg-red-100 text-red-800' : 
              'bg-yellow-100 text-yellow-800'}">
            ${status.replace('a2p_', '').toUpperCase()}
        </span>
    </p>
`; 