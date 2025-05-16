/**
 * Client Onboarding Pipeline - Complete Implementation
 * 
 * This script enhances the Client Onboarding Pipeline by:
 * 1. Adding a horizontal pipeline layout
 * 2. Adding comprehensive filtering options (brand, date, search, sort)
 * 3. Implementing responsive card design
 * 4. Adding detailed client information display
 * 
 * Usage:
 * 1. Open your browser console on the client portal page
 * 2. Run: enhanceClientOnboardingComplete()
 * 3. Or add this script to your site for permanent implementation
 */

// Main function to enhance the Client Onboarding Pipeline
async function enhanceClientOnboardingComplete() {
    console.log("Enhancing Client Onboarding Pipeline...");
    
    // Check if we're on the right page
    if (!document.querySelector('.client-pipeline') && 
        !document.querySelector('.onboarding-pipeline')) {
        console.error("Error: Not on the client onboarding page");
        return;
    }
    
    // Initialize Supabase client
    const supabaseUrl = 'https://jfypiuprdfbxmgznhynt.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmcXBpdXByZGZieG1nem5oeW50Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2Nzg3MjkyMzcsImV4cCI6MTk5NDMwNTIzN30.K5Z1A4XE_hbWCR7Y1QXJJAiGzh1HnAf9LYspH6oeQlU';
    const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);
    
    // Find the container element
    const pipelineContainer = document.querySelector('.client-pipeline') || 
                             document.querySelector('.onboarding-pipeline');
    
    if (!pipelineContainer) {
        console.error("Error: Could not find pipeline container");
        return;
    }
    
    // Create filter section
    const filterSection = document.createElement('div');
    filterSection.className = 'onboarding-filters my-3 p-3 bg-light rounded';
    filterSection.innerHTML = `
        <h5 class="mb-3">Filter Options</h5>
        <div class="row g-3">
            <div class="col-md-2">
                <label class="form-label">Brand</label>
                <select class="form-select" id="brandFilter">
                    <option value="all">All Brands</option>
                    <option value="cLineNow">cLineNow</option>
                    <option value="TextNow">TextNow</option>
                    <option value="RCSNow">RCSNow</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Date Range</label>
                <select class="form-select" id="dateFilter">
                    <option value="all">All Time</option>
                    <option value="today">Today</option>
                    <option value="yesterday">Yesterday</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                    <option value="custom">Custom Range</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Sort By</label>
                <select class="form-select" id="sortFilter">
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="name">Business Name</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">View Mode</label>
                <select class="form-select" id="viewModeFilter">
                    <option value="pipeline">Pipeline View</option>
                    <option value="list">List View</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Search</label>
                <input type="text" class="form-control" id="searchFilter" placeholder="Search clients...">
            </div>
        </div>
    `;
    
    // Insert filter section before the pipeline container
    pipelineContainer.parentNode.insertBefore(filterSection, pipelineContainer);
    
    // Create horizontal pipeline structure
    const stages = [
        { id: 'intake', name: 'Intake', icon: 'clipboard-check' },
        { id: 'verification', name: 'Verification', icon: 'shield-check' },
        { id: 'submission', name: 'Submission', icon: 'send' },
        { id: 'approval', name: 'Approval', icon: 'check-circle' },
        { id: 'implementation', name: 'Implementation', icon: 'gear' },
        { id: 'live', name: 'Live', icon: 'broadcast-tower' }
    ];
    
    // Clear existing content
    pipelineContainer.innerHTML = '';
    pipelineContainer.className = 'client-pipeline horizontal-pipeline my-4';
    
    // Create pipeline container
    const pipelineRow = document.createElement('div');
    pipelineRow.className = 'row g-3 pipeline-row';
    pipelineContainer.appendChild(pipelineRow);
    
    // Create columns for each stage
    stages.forEach(stage => {
        const column = document.createElement('div');
        column.className = 'col-md-2 pipeline-column';
        column.innerHTML = `
            <div class="stage-header bg-primary text-white p-2 rounded-top d-flex justify-content-between align-items-center">
                <span><i class="fas fa-${stage.icon}"></i> ${stage.name}</span>
                <span class="badge bg-light text-dark stage-count" id="count-${stage.id}">0</span>
            </div>
            <div class="stage-body bg-white rounded-bottom shadow-sm p-2 mb-3" id="stage-${stage.id}" style="min-height: 200px;">
                <!-- Cards will be inserted here -->
            </div>
        `;
        pipelineRow.appendChild(column);
    });
    
    // Add event listeners for filter controls
    const brandFilter = document.getElementById('brandFilter');
    const dateFilter = document.getElementById('dateFilter');
    const sortFilter = document.getElementById('sortFilter');
    const viewModeFilter = document.getElementById('viewModeFilter');
    const searchFilter = document.getElementById('searchFilter');
    
    // Debounce function for search input
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    // Load client data function
    async function loadClientData() {
        console.log("Loading client data with filters...");
        
        // Get filter values
        const brand = brandFilter.value;
        const dateRange = dateFilter.value;
        const sortBy = sortFilter.value;
        const viewMode = viewModeFilter.value;
        const searchTerm = searchFilter.value.toLowerCase();
        
        // Clear existing cards
        stages.forEach(stage => {
            document.getElementById(`stage-${stage.id}`).innerHTML = '';
            document.getElementById(`count-${stage.id}`).textContent = '0';
        });
        
        try {
            // Fetch client data from Supabase or your data source
            let { data, error } = await supabaseClient
                .from('clients')
                .select('*');
                
            if (error) {
                console.error("Error fetching client data:", error);
                return;
            }
            
            if (!data || data.length === 0) {
                console.log("No client data found, using sample data");
                // Sample data for demonstration
                data = getSampleClientData();
            }
            
            console.log("Raw client data:", data);
            
            // Apply filters
            let filteredData = data;
            
            // Brand filter
            if (brand !== 'all') {
                filteredData = filteredData.filter(client => client.brand === brand);
            }
            
            // Date filter
            if (dateRange !== 'all') {
                const now = new Date();
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                
                switch(dateRange) {
                    case 'today':
                        filteredData = filteredData.filter(client => {
                            const createdDate = new Date(client.created_at);
                            return createdDate >= today;
                        });
                        break;
                    case 'yesterday':
                        const yesterday = new Date(today);
                        yesterday.setDate(yesterday.getDate() - 1);
                        filteredData = filteredData.filter(client => {
                            const createdDate = new Date(client.created_at);
                            return createdDate >= yesterday && createdDate < today;
                        });
                        break;
                    case 'week':
                        const weekStart = new Date(today);
                        weekStart.setDate(today.getDate() - today.getDay());
                        filteredData = filteredData.filter(client => {
                            const createdDate = new Date(client.created_at);
                            return createdDate >= weekStart;
                        });
                        break;
                    case 'month':
                        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
                        filteredData = filteredData.filter(client => {
                            const createdDate = new Date(client.created_at);
                            return createdDate >= monthStart;
                        });
                        break;
                }
            }
            
            // Search filter
            if (searchTerm) {
                filteredData = filteredData.filter(client => 
                    (client.business_name && client.business_name.toLowerCase().includes(searchTerm)) ||
                    (client.client_name && client.client_name.toLowerCase().includes(searchTerm)) ||
                    (client.email && client.email.toLowerCase().includes(searchTerm))
                );
            }
            
            // Sort data
            switch(sortBy) {
                case 'newest':
                    filteredData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                    break;
                case 'oldest':
                    filteredData.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
                    break;
                case 'name':
                    filteredData.sort((a, b) => {
                        if (!a.business_name) return 1;
                        if (!b.business_name) return -1;
                        return a.business_name.localeCompare(b.business_name);
                    });
                    break;
            }
            
            console.log("Filtered client data:", filteredData);
            
            // Group by stage
            const stageGroups = {};
            stages.forEach(stage => {
                stageGroups[stage.id] = [];
            });
            
            filteredData.forEach(client => {
                if (client.stage && stageGroups[client.stage]) {
                    stageGroups[client.stage].push(client);
                } else if (client.status === 'pending') {
                    stageGroups['intake'].push(client);
                } else if (client.status === 'approved') {
                    stageGroups['approval'].push(client);
                } else if (client.status === 'declined') {
                    // Handle declined differently if needed
                    stageGroups['verification'].push(client);
                }
            });
            
            // Update count badges and render cards
            Object.keys(stageGroups).forEach(stageId => {
                const count = stageGroups[stageId].length;
                document.getElementById(`count-${stageId}`).textContent = count;
                
                const stageBody = document.getElementById(`stage-${stageId}`);
                
                if (count === 0) {
                    stageBody.innerHTML = '<div class="text-center text-muted p-3">No clients</div>';
                } else {
                    stageGroups[stageId].forEach(client => {
                        const card = renderClientCard(client, stageId);
                        stageBody.appendChild(card);
                    });
                }
            });
            
            // Toggle view mode
            if (viewMode === 'list') {
                pipelineContainer.classList.add('list-view');
                pipelineRow.className = 'pipeline-row list-mode';
            } else {
                pipelineContainer.classList.remove('list-view');
                pipelineRow.className = 'row g-3 pipeline-row';
            }
            
            // Update progress
            updateOnboardingProgress(filteredData);
            
        } catch (err) {
            console.error("Error processing client data:", err);
        }
    }
    
    // Render client card
    function renderClientCard(client, stageId) {
        const card = document.createElement('div');
        card.className = 'client-card mb-2 p-2 bg-white rounded shadow-sm border-start border-3';
        
        // Set border color based on stage
        switch(stageId) {
            case 'intake': card.classList.add('border-primary'); break;
            case 'verification': card.classList.add('border-info'); break;
            case 'submission': card.classList.add('border-warning'); break;
            case 'approval': card.classList.add('border-success'); break;
            case 'implementation': card.classList.add('border-secondary'); break;
            case 'live': card.classList.add('border-dark'); break;
        }
        
        // Format date
        const createdDate = client.created_at ? new Date(client.created_at) : new Date();
        const formattedDate = createdDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        
        // Calculate days in current stage
        const daysInStage = Math.floor((new Date() - createdDate) / (1000 * 60 * 60 * 24));
        
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <h6 class="mb-1 text-truncate" style="max-width: 150px;" title="${client.business_name || 'Unnamed Business'}">${client.business_name || 'Unnamed Business'}</h6>
                <span class="badge ${client.status === 'approved' ? 'bg-success' : client.status === 'declined' ? 'bg-danger' : 'bg-warning'}">${client.status || 'pending'}</span>
            </div>
            <p class="mb-1 small text-muted">${client.client_name || 'No client name'}</p>
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">${formattedDate}</small>
                <small class="text-${daysInStage > 7 ? 'danger' : 'muted'}">${daysInStage}d</small>
            </div>
        `;
        
        // Add click event to show client details modal
        card.addEventListener('click', () => {
            showClientDetailsModal(client);
        });
        
        return card;
    }
    
    // Show client details modal
    function showClientDetailsModal(client) {
        let modal = document.getElementById('clientDetailsModal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'clientDetailsModal';
            modal.setAttribute('tabindex', '-1');
            modal.setAttribute('aria-hidden', 'true');
            
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Client Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" id="clientDetailsBody">
                            <!-- Client details will be inserted here -->
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" id="updateStageBtn">Update Stage</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        const modalBody = document.getElementById('clientDetailsBody');
        const updateStageBtn = document.getElementById('updateStageBtn');
        
        // Format date
        const createdDate = client.created_at ? new Date(client.created_at) : new Date();
        const formattedDate = createdDate.toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric',
            year: 'numeric'
        });
        
        // Populate modal with client details
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h4>${client.business_name || 'Unnamed Business'}</h4>
                    <p class="text-muted mb-0">${client.client_name || 'No client name'}</p>
                    <p><strong>Email:</strong> ${client.email || 'No email'}</p>
                    <p><strong>Phone:</strong> ${client.phone || 'No phone'}</p>
                    <p><strong>Created:</strong> ${formattedDate}</p>
                    <p><strong>Status:</strong> <span class="badge ${client.status === 'approved' ? 'bg-success' : client.status === 'declined' ? 'bg-danger' : 'bg-warning'}">${client.status || 'pending'}</span></p>
                </div>
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">Current Stage</div>
                        <div class="card-body">
                            <h5 class="card-title">${stages.find(s => s.id === client.stage)?.name || 'Intake'}</h5>
                            <p class="card-text">Change the client's stage using the update button below.</p>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">Notes</div>
                        <div class="card-body">
                            <p class="card-text">${client.notes || 'No notes available'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Initialize Bootstrap modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Update stage button click handler
        updateStageBtn.onclick = async () => {
            const stageUpdateModal = new bootstrap.Modal(document.getElementById('stageUpdateModal') || createStageUpdateModal());
            stageUpdateModal.show();
            
            // Set client ID for stage update
            document.getElementById('clientIdForStageUpdate').value = client.id;
        };
    }
    
    // Create stage update modal
    function createStageUpdateModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'stageUpdateModal';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Update Client Stage</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <input type="hidden" id="clientIdForStageUpdate">
                        <div class="mb-3">
                            <label for="stageSelect" class="form-label">Select New Stage</label>
                            <select class="form-select" id="stageSelect">
                                ${stages.map(stage => `<option value="${stage.id}">${stage.name}</option>`).join('')}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="stageNotes" class="form-label">Notes (Optional)</label>
                            <textarea class="form-control" id="stageNotes" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmStageUpdateBtn">Update Stage</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Confirm stage update button click handler
        document.getElementById('confirmStageUpdateBtn').onclick = async () => {
            const clientId = document.getElementById('clientIdForStageUpdate').value;
            const newStage = document.getElementById('stageSelect').value;
            const notes = document.getElementById('stageNotes').value;
            
            try {
                // Update client stage in database
                const { data, error } = await supabaseClient
                    .from('clients')
                    .update({
                        stage: newStage,
                        notes: notes ? `${new Date().toISOString()}: ${notes}\n\n${client.notes || ''}` : client.notes
                    })
                    .eq('id', clientId);
                
                if (error) {
                    console.error("Error updating client stage:", error);
                    alert("Failed to update client stage.");
                } else {
                    console.log("Client stage updated successfully:", data);
                    
                    // Close modals
                    bootstrap.Modal.getInstance(document.getElementById('stageUpdateModal')).hide();
                    bootstrap.Modal.getInstance(document.getElementById('clientDetailsModal')).hide();
                    
                    // Reload client data
                    loadClientData();
                }
            } catch (err) {
                console.error("Error in stage update process:", err);
                alert("An error occurred during the update process.");
            }
        };
        
        return modal;
    }
    
    // Update onboarding progress visualization
    function updateOnboardingProgress(clientData) {
        // Create or get progress section
        let progressSection = document.getElementById('onboardingProgressSection');
        
        if (!progressSection) {
            progressSection = document.createElement('div');
            progressSection.id = 'onboardingProgressSection';
            progressSection.className = 'my-4 p-3 bg-white rounded shadow-sm';
            progressSection.innerHTML = '<h5 class="mb-3">Onboarding Progress</h5><div id="progressCharts" class="row"></div>';
            pipelineContainer.parentNode.insertBefore(progressSection, pipelineContainer.nextSibling);
        }
        
        const progressCharts = document.getElementById('progressCharts');
        progressCharts.innerHTML = '';
        
        // Count clients by stage
        const stageCounts = {};
        stages.forEach(stage => {
            stageCounts[stage.id] = 0;
        });
        
        clientData.forEach(client => {
            if (client.stage && stageCounts[client.stage] !== undefined) {
                stageCounts[client.stage]++;
            } else if (client.status === 'pending') {
                stageCounts['intake']++;
            } else if (client.status === 'approved') {
                stageCounts['approval']++;
            }
        });
        
        // Create progress bars
        const totalClients = clientData.length || 1; // Avoid division by zero
        
        const overallCol = document.createElement('div');
        overallCol.className = 'col-md-12 mb-3';
        overallCol.innerHTML = `
            <p class="mb-1">Overall Pipeline (${totalClients} clients)</p>
            <div class="progress" style="height: 24px;">
                ${stages.map((stage, index) => {
                    const percentage = (stageCounts[stage.id] / totalClients) * 100;
                    return `<div class="progress-bar bg-${getColorForStage(stage.id)}" role="progressbar" 
                            style="width: ${percentage}%" aria-valuenow="${percentage}" aria-valuemin="0" 
                            aria-valuemax="100" title="${stage.name}: ${stageCounts[stage.id]} clients">
                            ${percentage > 8 ? `${stage.name} (${stageCounts[stage.id]})` : ''}
                            </div>`;
                }).join('')}
            </div>
        `;
        progressCharts.appendChild(overallCol);
        
        // Add individual stage progress
        stages.forEach(stage => {
            const stageCol = document.createElement('div');
            stageCol.className = 'col-md-6 col-lg-4 mb-3';
            const percentage = (stageCounts[stage.id] / totalClients) * 100;
            
            stageCol.innerHTML = `
                <p class="mb-1">${stage.name} (${stageCounts[stage.id]} clients)</p>
                <div class="progress">
                    <div class="progress-bar bg-${getColorForStage(stage.id)}" role="progressbar" 
                         style="width: ${percentage}%" aria-valuenow="${percentage}" aria-valuemin="0" 
                         aria-valuemax="100">${Math.round(percentage)}%</div>
                </div>
            `;
            progressCharts.appendChild(stageCol);
        });
    }
    
    // Helper function to get color for stage
    function getColorForStage(stageId) {
        switch(stageId) {
            case 'intake': return 'primary';
            case 'verification': return 'info';
            case 'submission': return 'warning';
            case 'approval': return 'success';
            case 'implementation': return 'secondary';
            case 'live': return 'dark';
            default: return 'primary';
        }
    }
    
    // Sample client data for demonstration
    function getSampleClientData() {
        return [
            {
                id: 1,
                business_name: 'Acme Corporation',
                client_name: 'John Smith',
                email: 'john@acme.com',
                phone: '555-123-4567',
                stage: 'intake',
                status: 'pending',
                created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                notes: 'Initial contact made'
            },
            {
                id: 2,
                business_name: 'Globex Industries',
                client_name: 'Jane Doe',
                email: 'jane@globex.com',
                phone: '555-987-6543',
                stage: 'verification',
                status: 'pending',
                created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
                notes: 'Documents received, verification in progress'
            },
            {
                id: 3,
                business_name: 'Wayne Enterprises',
                client_name: 'Bruce Wayne',
                email: 'bruce@wayne.com',
                phone: '555-876-5432',
                stage: 'submission',
                status: 'pending',
                created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
                notes: 'Submitted to carrier'
            },
            {
                id: 4,
                business_name: 'Stark Industries',
                client_name: 'Tony Stark',
                email: 'tony@stark.com',
                phone: '555-432-1098',
                stage: 'approval',
                status: 'approved',
                created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
                notes: 'Approved by carrier, proceeding to implementation'
            },
            {
                id: 5,
                business_name: 'Daily Planet',
                client_name: 'Clark Kent',
                email: 'clark@dailyplanet.com',
                phone: '555-234-5678',
                stage: 'implementation',
                status: 'approved',
                created_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
                notes: 'Setting up services'
            },
            {
                id: 6,
                business_name: 'LexCorp',
                client_name: 'Lex Luthor',
                email: 'lex@lexcorp.com',
                phone: '555-345-6789',
                stage: 'live',
                status: 'approved',
                created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                notes: 'All services active and running'
            }
        ];
    }
    
    // Add event listeners for filters
    brandFilter.addEventListener('change', loadClientData);
    dateFilter.addEventListener('change', loadClientData);
    sortFilter.addEventListener('change', loadClientData);
    viewModeFilter.addEventListener('change', loadClientData);
    searchFilter.addEventListener('input', debounce(loadClientData, 300));
    
    // Initial load
    loadClientData();
    
    console.log("Client Onboarding Pipeline enhancement complete!");
}

// Usage Instructions
/* 
 * Option 1: Run directly in console:
 * enhanceClientOnboardingComplete()
 * 
 * Option 2: Add permanently to page:
 * 1. Add this script file to your site
 * 2. Add this line to your HTML where you want the enhancement to run:
 *    <script>document.addEventListener('DOMContentLoaded', enhanceClientOnboardingComplete);</script>
 */

// Auto-run if the page is already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log("Page already loaded, running enhancement...");
    setTimeout(enhanceClientOnboardingComplete, 1000);
} else {
    console.log("Setting up to run when page loads...");
    document.addEventListener('DOMContentLoaded', enhanceClientOnboardingComplete);
} 