/**
 * Offers & Split Tests Dashboard Functionality
 *
 * This file contains the JavaScript functionality for the Offers & Split Tests tab
 * in the TurnClicksToClients dashboard, including:
 * - Creating and managing offers
 * - Setting up split tests with multiple variants
 * - Tracking and displaying test results
 */

// Global variables to store chart instances
let testPerformanceChart = null;
let offerConversionChart = null;

// Define the main initialization function
(function() {
    // Make the function globally accessible
    window.offersAndSplitTests = {
        // Store available niches
        niches: [],

        initialize: function() {
            console.log('Initializing Offers & Split Tests tab...');

            try {
                // Fix modal overflow issues
                this.fixModalOverflow();

                // Load niches from the main dashboard
                this.loadNiches();

                // Set up event listeners for buttons
                this.setupEventListeners();

                // Load data
                this.loadOffersData();
                this.loadSplitTestsData();

                // Initialize charts
                this.createTestPerformanceChart();
                this.createOfferConversionChart();

                console.log('Offers & Split Tests tab initialization complete');
            } catch (error) {
                console.error('Error initializing Offers & Split Tests tab:', error);
            }
        },

        // Fix modal overflow issues
        fixModalOverflow: function() {
            // Add overflow-y: auto to all modals
            const modals = document.querySelectorAll('[id$="-modal"]');
            modals.forEach(modal => {
                if (!modal.style.overflowY || modal.style.overflowY !== 'auto') {
                    modal.style.overflowY = 'auto';
                }

                // Adjust the modal content container
                const contentContainer = modal.querySelector('div');
                if (contentContainer) {
                    // Ensure there's enough margin at the bottom
                    contentContainer.style.marginBottom = '50px';
                }
            });
        },

        // Load niches from the main dashboard
        loadNiches: function() {
            try {
                // Get niches from the main niche filter if available
                const nicheFilter = document.getElementById('niche-filter');
                if (nicheFilter) {
                    const options = nicheFilter.querySelectorAll('option');
                    this.niches = [];

                    options.forEach(option => {
                        if (option.value && option.value !== 'all') {
                            this.niches.push({
                                value: option.value,
                                text: option.textContent
                            });
                        }
                    });

                    console.log('Loaded niches:', this.niches);

                    // Populate niche dropdowns
                    this.populateNicheDropdowns();
                } else {
                    console.warn('Niche filter not found in the main dashboard');
                }
            } catch (error) {
                console.error('Error loading niches:', error);
            }
        },

        // Populate niche dropdowns in the modals
        populateNicheDropdowns: function() {
            try {
                const offerNicheDropdown = document.getElementById('offer-niche');
                const testNicheDropdown = document.getElementById('test-niche');

                if (offerNicheDropdown) {
                    // Clear existing options except the first one
                    const firstOption = offerNicheDropdown.querySelector('option:first-child');
                    offerNicheDropdown.innerHTML = '';
                    if (firstOption) {
                        offerNicheDropdown.appendChild(firstOption);
                    }

                    // Add niches as options
                    this.niches.forEach(niche => {
                        const option = document.createElement('option');
                        option.value = niche.value;
                        option.textContent = niche.text;
                        offerNicheDropdown.appendChild(option);
                    });
                }

                if (testNicheDropdown) {
                    // Clear existing options except the first one
                    const firstOption = testNicheDropdown.querySelector('option:first-child');
                    testNicheDropdown.innerHTML = '';
                    if (firstOption) {
                        testNicheDropdown.appendChild(firstOption);
                    }

                    // Add niches as options
                    this.niches.forEach(niche => {
                        const option = document.createElement('option');
                        option.value = niche.value;
                        option.textContent = niche.text;
                        testNicheDropdown.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error populating niche dropdowns:', error);
            }
        },

        // Generate AI offers using Gemini
        generateAIOffers: async function() {
            try {
                console.log('Generating AI offers...');

                // Check if Gemini integration is available
                if (!window.geminiIntegration) {
                    throw new Error('Gemini integration not found. Make sure gemini-integration.js is loaded.');
                }

                // Get available niches
                const niches = this.niches.map(niche => niche.value);
                if (niches.length === 0) {
                    throw new Error('No niches available. Please add niches first.');
                }

                // Define target audiences
                const audiences = ['all', 'quiz_completed', 'high_score', 'returning'];

                // Show loading state
                const generateBtn = document.getElementById('generate-ai-offers-btn');
                if (generateBtn) {
                    generateBtn.disabled = true;
                    generateBtn.textContent = 'Generating...';
                }

                // Get quiz data to inform the AI
                let quizData = [];
                try {
                    quizData = await fetchFromSupabase('tctc_quiz_submission', '?select=*&limit=20');
                } catch (error) {
                    console.warn('Could not fetch quiz data:', error);
                }

                // Generate offers for each niche and audience
                const generatedOffers = [];

                // Process one niche at a time to avoid rate limiting
                for (const niche of niches) {
                    // Get niche-specific quiz data
                    const nicheQuizData = quizData.filter(submission => submission.niche === niche);

                    // Create a filtered list of niche/audience combinations that need offers
                    const combinationsToGenerate = [];

                    for (const audience of audiences) {
                        try {
                            // Check if we already have enough offers for this combination
                            const existingOffers = await fetchFromSupabase('tctc_offers',
                                `?niche=eq.${niche}&target_audience=eq.${audience}&is_auto_generated=eq.true`);

                            // Only generate if we have fewer than 2 offers for this combination
                            if (existingOffers.length < 2) {
                                combinationsToGenerate.push({
                                    niche,
                                    audience,
                                    nicheQuizData
                                });
                            } else {
                                console.log(`Already have enough offers for ${niche}, ${audience}`);
                            }
                        } catch (error) {
                            console.error(`Error checking existing offers for ${niche}, ${audience}:`, error);
                        }
                    }

                    // If we have combinations to generate, use the rate-limited function
                    if (combinationsToGenerate.length > 0) {
                        // Generate at most 2 offers at a time to avoid rate limits
                        const batchSize = 2;
                        const batches = [];

                        for (let i = 0; i < combinationsToGenerate.length; i += batchSize) {
                            batches.push(combinationsToGenerate.slice(i, i + batchSize));
                        }

                        for (const batch of batches) {
                            // Process each batch
                            for (const combo of batch) {
                                try {
                                    const offer = await window.geminiIntegration.generateOffer(combo.niche, combo.audience, combo.nicheQuizData);

                                    if (offer) {
                                        generatedOffers.push(offer);
                                        console.log(`Created new AI offer for ${combo.niche}, targeting ${combo.audience}`);
                                    }
                                } catch (error) {
                                    console.error(`Error generating offer for ${combo.niche}, ${combo.audience}:`, error);
                                }
                            }

                            // Add a delay between batches
                            if (batch !== batches[batches.length - 1]) {
                                await new Promise(resolve => setTimeout(resolve, 30000)); // 30 second delay between batches
                                console.log("Waiting 30 seconds before processing next batch...");
                            }
                        }
                    }
                }

                // Reset button state
                if (generateBtn) {
                    generateBtn.disabled = false;
                    generateBtn.textContent = 'Generate AI Offers';
                }

                // Reload offers data
                await this.loadOffersData();

                // Show success message
                alert(`Successfully generated ${generatedOffers.length} new AI offers!`);

                return generatedOffers;
            } catch (error) {
                console.error('Error generating AI offers:', error);

                // Reset button state
                const generateBtn = document.getElementById('generate-ai-offers-btn');
                if (generateBtn) {
                    generateBtn.disabled = false;
                    generateBtn.textContent = 'Generate AI Offers';
                }

                alert(`Error generating AI offers: ${error.message}`);
                return [];
            }
        },

        // Set up event listeners for the Offers & Split Tests tab
        setupEventListeners: function() {
            // Create offer button
            const createOfferBtn = document.getElementById('create-offer-btn');
            if (createOfferBtn) {
                createOfferBtn.addEventListener('click', this.openCreateOfferModal);
            }

            // Create test button
            const createTestBtn = document.getElementById('create-test-btn');
            if (createTestBtn) {
                createTestBtn.addEventListener('click', this.openCreateTestModal);
            }

            // Generate AI offers button
            const generateAIOffersBtn = document.getElementById('generate-ai-offers-btn');
            if (generateAIOffersBtn) {
                generateAIOffersBtn.addEventListener('click', () => this.generateAIOffers());
            } else {
                // If the button doesn't exist, create it
                this.createGenerateAIOffersButton();
            }

            // Close modal buttons
            const closeModalBtns = document.querySelectorAll('.close-modal-btn');
            closeModalBtns.forEach(btn => {
                btn.addEventListener('click', this.closeAllModals);
            });

            // Cancel buttons
            const cancelBtns = document.querySelectorAll('.cancel-btn');
            cancelBtns.forEach(btn => {
                btn.addEventListener('click', this.closeAllModals);
            });

            // Add variant button
            const addVariantBtn = document.getElementById('add-variant-btn');
            if (addVariantBtn) {
                addVariantBtn.addEventListener('click', this.addTestVariant);
            }

            // Offer search and filter
            const offerSearch = document.getElementById('offer-search');
            if (offerSearch) {
                offerSearch.addEventListener('input', this.filterOffers);
            }

            const offerFilter = document.getElementById('offer-filter');
            if (offerFilter) {
                offerFilter.addEventListener('change', this.filterOffers);
            }

            // Form submissions
            const createOfferForm = document.getElementById('create-offer-form');
            if (createOfferForm) {
                createOfferForm.addEventListener('submit', this.handleCreateOfferSubmit);
            }

            const createTestForm = document.getElementById('create-test-form');
            if (createTestForm) {
                createTestForm.addEventListener('submit', this.handleCreateTestSubmit);
            }
        },

        // Load offers data from Supabase
        loadOffersData: function() {
            console.log('Loading offers data...');

            // This would normally fetch data from Supabase
            // For now, we'll just log a message

            // Render empty offers grid
            const offersGrid = document.getElementById('offers-grid');
            if (offersGrid) {
                offersGrid.innerHTML = `
                    <div style="text-align: center; grid-column: 1 / -1; padding: 20px;">
                        No offers found. Create your first offer to get started.
                    </div>
                `;
            }
        },

        // Load split tests data from Supabase
        loadSplitTestsData: function() {
            console.log('Loading split tests data...');

            // This would normally fetch data from Supabase
            // For now, we'll just log a message

            // Render empty tests table
            const testsTable = document.getElementById('split-tests-table');
            if (testsTable) {
                const tbody = testsTable.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = `<tr><td colspan="9">No active split tests</td></tr>`;
                }
            }
        },

        // Create Test Performance Chart
        createTestPerformanceChart: function() {
            const ctx = document.getElementById('test-performance-chart');
            if (!ctx) return;

            // Destroy existing chart if it exists
            if (testPerformanceChart) {
                testPerformanceChart.destroy();
            }

            // Sample data
            const labels = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
            const datasets = [
                {
                    label: 'Variant A',
                    data: [2.1, 2.5, 3.2, 3.5, 4.1, 4.8, 5.2],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Variant B',
                    data: [1.8, 2.2, 2.7, 3.0, 3.5, 4.0, 4.3],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                }
            ];

            testPerformanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Conversion Rate Over Time (%)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Conversion Rate (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Day'
                            }
                        }
                    }
                }
            });
        },

        // Create Offer Conversion Chart
        createOfferConversionChart: function() {
            const ctx = document.getElementById('offer-conversion-chart');
            if (!ctx) return;

            // Destroy existing chart if it exists
            if (offerConversionChart) {
                offerConversionChart.destroy();
            }

            // Sample data
            const labels = ['Offer 1', 'Offer 2', 'Offer 3', 'Offer 4', 'Offer 5'];
            const data = [4.8, 3.2, 5.7, 2.9, 4.1];

            offerConversionChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Conversion Rate (%)',
                        data: data,
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.7)',
                            'rgba(16, 185, 129, 0.7)',
                            'rgba(245, 158, 11, 0.7)',
                            'rgba(239, 68, 68, 0.7)',
                            'rgba(139, 92, 246, 0.7)'
                        ],
                        borderColor: [
                            'rgba(59, 130, 246, 1)',
                            'rgba(16, 185, 129, 1)',
                            'rgba(245, 158, 11, 1)',
                            'rgba(239, 68, 68, 1)',
                            'rgba(139, 92, 246, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Conversion Rate by Offer (%)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Conversion Rate (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Offer'
                            }
                        }
                    }
                }
            });
        },

        // Open the create offer modal
        openCreateOfferModal: function() {
            const modal = document.getElementById('create-offer-modal');
            if (modal) {
                modal.style.display = 'block';
            }
        },

        // Open the create test modal
        openCreateTestModal: function() {
            const modal = document.getElementById('create-test-modal');
            if (modal) {
                modal.style.display = 'block';
            }
        },

        // Close all modals
        closeAllModals: function() {
            const modals = document.querySelectorAll('[id$="-modal"]');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        },

        // Create the Generate AI Offers button if it doesn't exist
        createGenerateAIOffersButton: function() {
            // Check if the button already exists
            if (document.getElementById('generate-ai-offers-btn')) {
                return;
            }

            // Find the container where we want to add the button
            const container = document.querySelector('.offers-grid-header');
            if (!container) {
                // If the container doesn't exist, try to find the offers section
                const offersSection = document.getElementById('offers');
                if (offersSection) {
                    // Find the first h2 element in the offers section
                    const header = offersSection.querySelector('h2');
                    if (header) {
                        // Create a container for the header and button
                        const newContainer = document.createElement('div');
                        newContainer.className = 'offers-grid-header';
                        newContainer.style.display = 'flex';
                        newContainer.style.justifyContent = 'space-between';
                        newContainer.style.alignItems = 'center';
                        newContainer.style.marginBottom = '20px';

                        // Clone the header and add it to the container
                        const newHeader = header.cloneNode(true);
                        newContainer.appendChild(newHeader);

                        // Create a button container
                        const buttonContainer = document.createElement('div');
                        buttonContainer.style.display = 'flex';
                        buttonContainer.style.gap = '10px';

                        // Add the existing create offer button if it exists
                        const createOfferBtn = document.getElementById('create-offer-btn');
                        if (createOfferBtn) {
                            buttonContainer.appendChild(createOfferBtn);
                        }

                        // Create the generate AI offers button
                        const generateBtn = document.createElement('button');
                        generateBtn.id = 'generate-ai-offers-btn';
                        generateBtn.textContent = 'Generate AI Offers';
                        generateBtn.style.padding = '8px 16px';
                        generateBtn.style.backgroundColor = '#8b5cf6';
                        generateBtn.style.color = 'white';
                        generateBtn.style.border = 'none';
                        generateBtn.style.borderRadius = '4px';
                        generateBtn.style.cursor = 'pointer';

                        // Add the button to the container
                        buttonContainer.appendChild(generateBtn);
                        newContainer.appendChild(buttonContainer);

                        // Replace the header with the new container
                        header.parentNode.replaceChild(newContainer, header);

                        // Add event listener to the button
                        generateBtn.addEventListener('click', () => this.generateAIOffers());
                    }
                }
            } else {
                // If the container exists, just add the button
                const generateBtn = document.createElement('button');
                generateBtn.id = 'generate-ai-offers-btn';
                generateBtn.textContent = 'Generate AI Offers';
                generateBtn.style.padding = '8px 16px';
                generateBtn.style.backgroundColor = '#8b5cf6';
                generateBtn.style.color = 'white';
                generateBtn.style.border = 'none';
                generateBtn.style.borderRadius = '4px';
                generateBtn.style.cursor = 'pointer';

                container.appendChild(generateBtn);

                // Add event listener to the button
                generateBtn.addEventListener('click', () => this.generateAIOffers());
            }
        },

        // Add a new test variant
        addTestVariant: function() {
            console.log('Adding test variant...');
            alert('This functionality is not yet implemented.');
        },

        // Filter offers
        filterOffers: function() {
            console.log('Filtering offers...');
            // This would normally filter the offers grid
        },

        // Handle create offer form submission
        handleCreateOfferSubmit: function(e) {
            e.preventDefault();
            console.log('Creating offer...');
            alert('This functionality is not yet implemented.');
        },

        // Handle create test form submission
        handleCreateTestSubmit: function(e) {
            e.preventDefault();
            console.log('Creating test...');
            alert('This functionality is not yet implemented.');
        }
    };
})();
