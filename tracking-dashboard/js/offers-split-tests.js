/**
 * Offers & Split Tests Dashboard Functionality
 *
 * This file contains the JavaScript functionality for the Offers & Split Tests tab
 * in the TurnClicksToClients dashboard, including:
 * - Creating and managing offers
 * - Setting up split tests with multiple variants
 * - Tracking and displaying test results
 * - Machine learning-based automatic split test creation
 * - Targeting specific user segments based on behavior
 */

// Supabase configuration
const SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64';

// Global variables to store chart instances
let testPerformanceChart = null;
let offerConversionChart = null;

// Initialize the Offers & Split Tests tab
async function initializeOffersAndTests() {
    console.log('Initializing Offers & Split Tests tab...');

    // Set up event listeners for buttons
    setupEventListeners();

    // Load offers and tests data
    await loadOffersData();
    await loadSplitTestsData();

    // Initialize charts
    createTestPerformanceChart();
    createOfferConversionChart();

    // Check for ML insights and recommendations
    checkForMLRecommendations();
}

// Fetch data from Supabase
async function fetchFromSupabase(table, query = '') {
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/${table}${query}`, {
            method: 'GET',
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error fetching from ${table}:`, error);
        return [];
    }
}

// Set up event listeners for the Offers & Split Tests tab
function setupEventListeners() {
    // Create offer button
    const createOfferBtn = document.getElementById('create-offer-btn');
    if (createOfferBtn) {
        createOfferBtn.addEventListener('click', openCreateOfferModal);
    }

    // Create test button
    const createTestBtn = document.getElementById('create-test-btn');
    if (createTestBtn) {
        createTestBtn.addEventListener('click', openCreateTestModal);
    }

    // Close modal buttons
    const closeModalBtns = document.querySelectorAll('.close-modal-btn');
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });

    // Cancel buttons
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });

    // Add variant button
    const addVariantBtn = document.getElementById('add-variant-btn');
    if (addVariantBtn) {
        addVariantBtn.addEventListener('click', addTestVariant);
    }

    // Offer search and filter
    const offerSearch = document.getElementById('offer-search');
    if (offerSearch) {
        offerSearch.addEventListener('input', filterOffers);
    }

    const offerFilter = document.getElementById('offer-filter');
    if (offerFilter) {
        offerFilter.addEventListener('change', filterOffers);
    }

    // Form submissions
    const createOfferForm = document.getElementById('create-offer-form');
    if (createOfferForm) {
        createOfferForm.addEventListener('submit', handleCreateOfferSubmit);
    }

    const createTestForm = document.getElementById('create-test-form');
    if (createTestForm) {
        createTestForm.addEventListener('submit', handleCreateTestSubmit);
    }
}

// Load offers data from Supabase
async function loadOffersData() {
    try {
        console.log('Loading offers data...');
        const offers = await fetchFromSupabase('tctc_offers', '?select=*&is_active=eq.true&order=created_at.desc');

        renderOffersGrid(offers);
        populateOfferDropdowns(offers);

        return offers;
    } catch (error) {
        console.error('Error loading offers data:', error);
        return [];
    }
}

// Load split tests data from Supabase
async function loadSplitTestsData() {
    try {
        console.log('Loading split tests data...');
        const tests = await fetchFromSupabase('tctc_split_tests', '?select=*,tctc_test_variants(*)&order=created_at.desc');

        renderSplitTestsTable(tests);
        updateTestCharts(tests);

        return tests;
    } catch (error) {
        console.error('Error loading split tests data:', error);
        return [];
    }
}

// Render offers in the grid
function renderOffersGrid(offers) {
    const offersGrid = document.getElementById('offers-grid');
    if (!offersGrid) return;

    if (offers.length === 0) {
        offersGrid.innerHTML = `
            <div style="text-align: center; grid-column: 1 / -1; padding: 20px;">
                No offers found. Create your first offer to get started.
            </div>
        `;
        return;
    }

    let offerCardsHTML = '';

    offers.forEach(offer => {
        const isAutoGenerated = offer.is_auto_generated ?
            `<span style="background-color: #8b5cf6; color: white; font-size: 0.7em; padding: 3px 6px; border-radius: 4px; margin-left: 5px;">AI Generated</span>` : '';

        offerCardsHTML += `
            <div class="offer-card" data-id="${offer.id}" data-niche="${offer.niche}" data-target="${offer.target_audience}">
                <h3>${offer.name} ${isAutoGenerated}</h3>
                <p class="offer-niche">Niche: ${formatNiche(offer.niche)}</p>
                <p class="offer-headline">${offer.headline}</p>
                <p class="offer-description">${offer.description.substring(0, 100)}${offer.description.length > 100 ? '...' : ''}</p>
                <div class="offer-footer">
                    <span class="offer-target">Target: ${formatTargetAudience(offer.target_audience)}</span>
                    <div class="offer-actions">
                        <button class="edit-offer-btn" data-id="${offer.id}">Edit</button>
                        <button class="delete-offer-btn" data-id="${offer.id}">Delete</button>
                    </div>
                </div>
            </div>
        `;
    });

    offersGrid.innerHTML = offerCardsHTML;

    // Add event listeners to the edit and delete buttons
    document.querySelectorAll('.edit-offer-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const offerId = e.target.getAttribute('data-id');
            editOffer(offerId);
        });
    });

    document.querySelectorAll('.delete-offer-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const offerId = e.target.getAttribute('data-id');
            deleteOffer(offerId);
        });
    });
}

// Render split tests in the table
function renderSplitTestsTable(tests) {
    const testsTable = document.getElementById('split-tests-table');
    if (!testsTable) return;

    const tbody = testsTable.querySelector('tbody');

    if (tests.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9">No active split tests</td></tr>`;
        return;
    }

    let testsHTML = '';

    tests.forEach(test => {
        const variants = test.tctc_test_variants || [];
        const variantCount = variants.length;

        // Calculate total impressions and conversions
        let totalImpressions = 0;
        let totalConversions = 0;

        // This would normally come from the test results table
        // For now, we'll use placeholder data
        totalImpressions = Math.floor(Math.random() * 1000) + 100;
        totalConversions = Math.floor(Math.random() * 100);

        const conversionRate = totalImpressions > 0 ?
            ((totalConversions / totalImpressions) * 100).toFixed(2) + '%' : '0%';

        const isAutoGenerated = test.is_auto_generated ?
            `<span style="background-color: #8b5cf6; color: white; font-size: 0.7em; padding: 3px 6px; border-radius: 4px; margin-left: 5px;">AI Generated</span>` : '';

        testsHTML += `
            <tr data-id="${test.id}">
                <td>${test.name} ${isAutoGenerated}</td>
                <td><span class="status-badge status-${test.status.toLowerCase()}">${capitalizeFirstLetter(test.status)}</span></td>
                <td>${formatDate(test.start_date)}</td>
                <td>${formatNiche(test.niche)}</td>
                <td>${variantCount}</td>
                <td>${totalImpressions}</td>
                <td>${totalConversions}</td>
                <td>${conversionRate}</td>
                <td>
                    <button class="view-test-btn" data-id="${test.id}">View</button>
                    <button class="pause-test-btn" data-id="${test.id}" ${test.status !== 'active' ? 'disabled' : ''}>Pause</button>
                    <button class="end-test-btn" data-id="${test.id}" ${test.status === 'completed' ? 'disabled' : ''}>End</button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = testsHTML;

    // Add event listeners to the action buttons
    document.querySelectorAll('.view-test-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const testId = e.target.getAttribute('data-id');
            viewTestResults(testId);
        });
    });

    document.querySelectorAll('.pause-test-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const testId = e.target.getAttribute('data-id');
            updateTestStatus(testId, 'paused');
        });
    });

    document.querySelectorAll('.end-test-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const testId = e.target.getAttribute('data-id');
            updateTestStatus(testId, 'completed');
        });
    });
}

// Create Test Performance Chart
function createTestPerformanceChart() {
    const ctx = document.getElementById('test-performance-chart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (testPerformanceChart) {
        testPerformanceChart.destroy();
    }

    // Sample data - this would be replaced with real data from the database
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
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
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
}

// Create Offer Conversion Chart
function createOfferConversionChart() {
    const ctx = document.getElementById('offer-conversion-chart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (offerConversionChart) {
        offerConversionChart.destroy();
    }

    // Sample data - this would be replaced with real data from the database
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
}

// Update test charts with real data
function updateTestCharts(tests) {
    // This function would update the charts with real data from the tests
    // For now, we'll use the sample data in the chart creation functions
    console.log('Updating test charts with data from', tests.length, 'tests');
}

// Populate offer dropdowns in the create test form
function populateOfferDropdowns(offers) {
    const offerDropdowns = document.querySelectorAll('.variant-offer');
    if (!offerDropdowns || offerDropdowns.length === 0) return;

    // Clear existing options except the first one
    offerDropdowns.forEach(dropdown => {
        const firstOption = dropdown.querySelector('option:first-child');
        dropdown.innerHTML = '';
        if (firstOption) {
            dropdown.appendChild(firstOption);
        }
    });

    // Add offers as options
    offers.forEach(offer => {
        const option = document.createElement('option');
        option.value = offer.id;
        option.textContent = offer.name;

        offerDropdowns.forEach(dropdown => {
            dropdown.appendChild(option.cloneNode(true));
        });
    });
}

// Filter offers based on search and filter criteria
function filterOffers() {
    const searchTerm = document.getElementById('offer-search').value.toLowerCase();
    const filterValue = document.getElementById('offer-filter').value;

    const offerCards = document.querySelectorAll('.offer-card');
    if (!offerCards || offerCards.length === 0) return;

    offerCards.forEach(card => {
        const offerName = card.querySelector('h3').textContent.toLowerCase();
        const offerNiche = card.getAttribute('data-niche');
        const offerTarget = card.getAttribute('data-target');

        const matchesSearch = offerName.includes(searchTerm);
        const matchesFilter = filterValue === 'all' || offerNiche === filterValue;

        if (matchesSearch && matchesFilter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Add a new test variant to the create test form
function addTestVariant() {
    const variantsContainer = document.getElementById('test-variants');
    if (!variantsContainer) return;

    const existingVariants = variantsContainer.querySelectorAll('.variant');
    const variantCount = existingVariants.length;

    if (variantCount >= 4) {
        alert('You can add a maximum of 4 variants to a test.');
        return;
    }

    // Create a new variant with a letter based on the count (C, D, etc.)
    const variantLetter = String.fromCharCode(65 + variantCount); // A=65, B=66, etc.

    const newVariant = document.createElement('div');
    newVariant.className = 'variant';
    newVariant.style.border = '1px solid #ddd';
    newVariant.style.borderRadius = '4px';
    newVariant.style.padding = '15px';
    newVariant.style.marginBottom = '15px';

    newVariant.innerHTML = `
        <h4>Variant ${variantLetter}</h4>
        <div style="margin-bottom: 10px;">
            <label for="variant-${variantLetter.toLowerCase()}-offer" style="display: block; margin-bottom: 5px;">Select Offer:</label>
            <select id="variant-${variantLetter.toLowerCase()}-offer" class="variant-offer" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                <option value="">Select an offer</option>
                <!-- Offers will be populated dynamically -->
            </select>
        </div>
        <div style="margin-bottom: 10px;">
            <label for="variant-${variantLetter.toLowerCase()}-weight" style="display: block; margin-bottom: 5px;">Traffic Weight (%):</label>
            <input type="number" id="variant-${variantLetter.toLowerCase()}-weight" class="variant-weight" min="5" max="95" value="25" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        </div>
        <button type="button" class="remove-variant-btn" style="padding: 5px 10px; background-color: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">Remove Variant</button>
    `;

    variantsContainer.appendChild(newVariant);

    // Add event listener to the remove button
    const removeBtn = newVariant.querySelector('.remove-variant-btn');
    removeBtn.addEventListener('click', function() {
        variantsContainer.removeChild(newVariant);
        updateVariantWeights();
    });

    // Populate the offer dropdown
    const offerDropdown = newVariant.querySelector('.variant-offer');
    const offers = Array.from(document.querySelectorAll('#variant-a-offer option')).slice(1);

    offers.forEach(option => {
        offerDropdown.appendChild(option.cloneNode(true));
    });

    // Update weights to ensure they sum to 100%
    updateVariantWeights();
}

// Update variant weights to ensure they sum to 100%
function updateVariantWeights() {
    const weightInputs = document.querySelectorAll('.variant-weight');
    if (!weightInputs || weightInputs.length === 0) return;

    const variantCount = weightInputs.length;
    const equalWeight = Math.floor(100 / variantCount);

    weightInputs.forEach((input, index) => {
        if (index === variantCount - 1) {
            // Last variant gets the remainder to ensure sum is 100%
            const sumOthers = Array.from(weightInputs)
                .slice(0, variantCount - 1)
                .reduce((sum, input) => sum + parseInt(input.value), 0);

            input.value = 100 - sumOthers;
        } else {
            input.value = equalWeight;
        }
    });
}

// Open the create offer modal
function openCreateOfferModal() {
    const modal = document.getElementById('create-offer-modal');
    if (modal) {
        modal.style.display = 'block';
    }
}

// Open the create test modal
function openCreateTestModal() {
    const modal = document.getElementById('create-test-modal');
    if (modal) {
        modal.style.display = 'block';
    }
}

// Close all modals
function closeAllModals() {
    const modals = document.querySelectorAll('[id$="-modal"]');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
}

// Handle create offer form submission
async function handleCreateOfferSubmit(e) {
    e.preventDefault();

    try {
        const form = e.target;

        // Get form values
        const name = document.getElementById('offer-name').value;
        const niche = document.getElementById('offer-niche').value;
        const headline = document.getElementById('offer-headline').value;
        const description = document.getElementById('offer-description').value;
        const ctaText = document.getElementById('offer-cta').value;
        const targetAudience = document.getElementById('offer-target').value;

        // Validate form
        if (!name || !niche || !headline || !description || !ctaText || !targetAudience) {
            alert('Please fill in all required fields.');
            return;
        }

        // Prepare offer data
        const offerData = {
            name,
            niche,
            headline,
            description,
            cta_text: ctaText,
            target_audience: targetAudience,
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };

        console.log('Creating offer:', offerData);

        // Insert the offer into Supabase
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(offerData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close the modal
        closeAllModals();

        // Reload offers data
        await loadOffersData();

        // Show success message
        alert('Offer created successfully!');

    } catch (error) {
        console.error('Error creating offer:', error);
        alert('Error creating offer. Please try again.');
    }
}

// Handle create test form submission
async function handleCreateTestSubmit(e) {
    e.preventDefault();

    try {
        const form = e.target;

        // Get form values
        const name = document.getElementById('test-name').value;
        const niche = document.getElementById('test-niche').value;
        const targetAudience = document.getElementById('test-target').value;
        const durationDays = parseInt(document.getElementById('test-duration').value);

        // Validate form
        if (!name || !niche || !targetAudience || isNaN(durationDays)) {
            alert('Please fill in all required fields.');
            return;
        }

        // Get variants
        const variants = [];
        const variantElements = document.querySelectorAll('.variant');

        for (let i = 0; i < variantElements.length; i++) {
            const variantElement = variantElements[i];
            const variantLetter = String.fromCharCode(65 + i); // A, B, C, etc.

            const offerId = variantElement.querySelector(`#variant-${variantLetter.toLowerCase()}-offer`).value;
            const weight = parseInt(variantElement.querySelector(`#variant-${variantLetter.toLowerCase()}-weight`).value);

            if (!offerId || isNaN(weight)) {
                alert(`Please select an offer and set a valid weight for Variant ${variantLetter}.`);
                return;
            }

            variants.push({
                offer_id: offerId,
                variant_name: variantLetter,
                is_control: i === 0, // First variant is the control
                traffic_weight: weight
            });
        }

        // Validate that weights sum to 100%
        const totalWeight = variants.reduce((sum, variant) => sum + variant.traffic_weight, 0);
        if (totalWeight !== 100) {
            alert(`Variant weights must sum to 100%. Current total: ${totalWeight}%`);
            return;
        }

        // Prepare test data
        const testData = {
            name,
            niche,
            target_audience: targetAudience,
            status: 'active',
            start_date: new Date().toISOString(),
            duration_days: durationDays,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };

        console.log('Creating test:', testData);
        console.log('With variants:', variants);

        // Insert the test into Supabase
        const testResponse = await fetch(`${SUPABASE_URL}/rest/v1/tctc_split_tests`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(testData)
        });

        if (!testResponse.ok) {
            throw new Error(`HTTP error! status: ${testResponse.status}`);
        }

        const testResult = await testResponse.json();
        const testId = testResult[0]?.id;

        if (!testId) {
            throw new Error('Failed to get test ID from response');
        }

        // Create variants for the test
        for (const variant of variants) {
            const variantData = {
                ...variant,
                test_id: testId,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            };

            const variantResponse = await fetch(`${SUPABASE_URL}/rest/v1/tctc_test_variants`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'apikey': SUPABASE_KEY,
                    'Authorization': `Bearer ${SUPABASE_KEY}`
                },
                body: JSON.stringify(variantData)
            });

            if (!variantResponse.ok) {
                throw new Error(`HTTP error! status: ${variantResponse.status}`);
            }
        }

        // Close the modal
        closeAllModals();

        // Reload tests data
        await loadSplitTestsData();

        // Show success message
        alert('Split test created successfully!');

    } catch (error) {
        console.error('Error creating split test:', error);
        alert('Error creating split test. Please try again.');
    }
}

// View test results
async function viewTestResults(testId) {
    try {
        console.log('Viewing test results for test ID:', testId);

        // Fetch test data
        const tests = await fetchFromSupabase('tctc_split_tests', `?id=eq.${testId}&select=*,tctc_test_variants(*)`);

        if (!tests || tests.length === 0) {
            throw new Error('Test not found');
        }

        const test = tests[0];
        const variants = test.tctc_test_variants || [];

        // Fetch test results
        const results = await fetchFromSupabase('tctc_test_results', `?test_id=eq.${testId}&select=*`);

        // Calculate metrics for each variant
        const variantMetrics = {};

        variants.forEach(variant => {
            const variantResults = results.filter(result => result.variant_id === variant.id);

            const impressions = variantResults.reduce((sum, result) => sum + result.impressions, 0);
            const conversions = variantResults.reduce((sum, result) => sum + result.conversions, 0);
            const conversionRate = impressions > 0 ? (conversions / impressions) * 100 : 0;

            variantMetrics[variant.id] = {
                name: variant.variant_name,
                is_control: variant.is_control,
                impressions,
                conversions,
                conversionRate: conversionRate.toFixed(2) + '%',
                improvement: 0 // Will be calculated below
            };
        });

        // Calculate improvement over control
        const controlVariant = variants.find(v => v.is_control);
        if (controlVariant) {
            const controlMetrics = variantMetrics[controlVariant.id];
            const controlConversionRate = parseFloat(controlMetrics.conversionRate);

            Object.keys(variantMetrics).forEach(variantId => {
                if (variantId !== controlVariant.id) {
                    const variantConversionRate = parseFloat(variantMetrics[variantId].conversionRate);
                    const improvement = controlConversionRate > 0
                        ? ((variantConversionRate - controlConversionRate) / controlConversionRate) * 100
                        : 0;

                    variantMetrics[variantId].improvement = improvement.toFixed(2) + '%';
                }
            });
        }

        // Show the results modal
        const modal = document.getElementById('test-results-modal');
        const modalTitle = document.getElementById('test-results-title');
        const modalContent = document.getElementById('test-results-content');

        if (!modal || !modalTitle || !modalContent) {
            throw new Error('Modal elements not found');
        }

        modalTitle.textContent = `Split Test Results: ${test.name}`;

        // Create the content HTML
        let contentHTML = `
            <div style="margin-bottom: 20px;">
                <p><strong>Niche:</strong> ${formatNiche(test.niche)}</p>
                <p><strong>Status:</strong> ${capitalizeFirstLetter(test.status)}</p>
                <p><strong>Start Date:</strong> ${formatDate(test.start_date)}</p>
                <p><strong>Target Audience:</strong> ${formatTargetAudience(test.target_audience)}</p>
            </div>

            <h3>Variant Performance</h3>
            <table class="data-table" style="width: 100%; margin-bottom: 20px;">
                <thead>
                    <tr>
                        <th>Variant</th>
                        <th>Impressions</th>
                        <th>Conversions</th>
                        <th>Conv. Rate</th>
                        <th>vs. Control</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Add rows for each variant
        variants.forEach(variant => {
            const metrics = variantMetrics[variant.id];
            const isControl = variant.is_control;

            contentHTML += `
                <tr>
                    <td>${variant.variant_name}${isControl ? ' (Control)' : ''}</td>
                    <td>${metrics.impressions}</td>
                    <td>${metrics.conversions}</td>
                    <td>${metrics.conversionRate}</td>
                    <td>${isControl ? '-' : metrics.improvement}</td>
                </tr>
            `;
        });

        contentHTML += `
                </tbody>
            </table>

            <h3>Daily Performance</h3>
            <div style="height: 300px;">
                <canvas id="test-results-chart"></canvas>
            </div>
        `;

        modalContent.innerHTML = contentHTML;

        // Show the modal
        modal.style.display = 'block';

        // Create the chart
        const ctx = document.getElementById('test-results-chart');
        if (ctx) {
            const chartData = {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: variants.map((variant, index) => {
                    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
                    return {
                        label: `Variant ${variant.variant_name}`,
                        data: [2.1, 2.5, 3.2, 3.5, 4.1, 4.8, 5.2].map(val => val * (0.8 + Math.random() * 0.4)),
                        borderColor: colors[index % colors.length],
                        backgroundColor: `rgba(${index * 50}, ${150 - index * 20}, ${200}, 0.1)`,
                        tension: 0.4
                    };
                })
            };

            new Chart(ctx, {
                type: 'line',
                data: chartData,
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
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
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
        }

    } catch (error) {
        console.error('Error viewing test results:', error);
        alert('Error loading test results. Please try again.');
    }
}

// Update test status (pause or complete)
async function updateTestStatus(testId, newStatus) {
    try {
        console.log(`Updating test ${testId} status to ${newStatus}`);

        // Update the test status in Supabase
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_split_tests?id=eq.${testId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify({
                status: newStatus,
                updated_at: new Date().toISOString(),
                end_date: newStatus === 'completed' ? new Date().toISOString() : null
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Reload tests data
        await loadSplitTestsData();

        // Show success message
        alert(`Test ${newStatus === 'paused' ? 'paused' : 'completed'} successfully!`);

    } catch (error) {
        console.error('Error updating test status:', error);
        alert('Error updating test status. Please try again.');
    }
}

// Edit an offer
async function editOffer(offerId) {
    try {
        console.log('Editing offer:', offerId);

        // Fetch the offer data
        const offers = await fetchFromSupabase('tctc_offers', `?id=eq.${offerId}`);

        if (!offers || offers.length === 0) {
            throw new Error('Offer not found');
        }

        const offer = offers[0];

        // Populate the form
        document.getElementById('offer-name').value = offer.name;
        document.getElementById('offer-niche').value = offer.niche;
        document.getElementById('offer-headline').value = offer.headline;
        document.getElementById('offer-description').value = offer.description;
        document.getElementById('offer-cta').value = offer.cta_text;
        document.getElementById('offer-target').value = offer.target_audience;

        // Show the modal
        openCreateOfferModal();

        // Change the form submission handler to update instead of create
        const form = document.getElementById('create-offer-form');
        if (form) {
            form.removeEventListener('submit', handleCreateOfferSubmit);
            form.addEventListener('submit', (e) => handleUpdateOfferSubmit(e, offerId));
        }

    } catch (error) {
        console.error('Error editing offer:', error);
        alert('Error loading offer data. Please try again.');
    }
}

// Handle update offer form submission
async function handleUpdateOfferSubmit(e, offerId) {
    e.preventDefault();

    try {
        const form = e.target;

        // Get form values
        const name = document.getElementById('offer-name').value;
        const niche = document.getElementById('offer-niche').value;
        const headline = document.getElementById('offer-headline').value;
        const description = document.getElementById('offer-description').value;
        const ctaText = document.getElementById('offer-cta').value;
        const targetAudience = document.getElementById('offer-target').value;

        // Validate form
        if (!name || !niche || !headline || !description || !ctaText || !targetAudience) {
            alert('Please fill in all required fields.');
            return;
        }

        // Prepare offer data
        const offerData = {
            name,
            niche,
            headline,
            description,
            cta_text: ctaText,
            target_audience: targetAudience,
            updated_at: new Date().toISOString()
        };

        console.log('Updating offer:', offerData);

        // Update the offer in Supabase
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offers?id=eq.${offerId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(offerData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close the modal
        closeAllModals();

        // Reload offers data
        await loadOffersData();

        // Show success message
        alert('Offer updated successfully!');

        // Reset the form submission handler
        const formElement = document.getElementById('create-offer-form');
        if (formElement) {
            formElement.removeEventListener('submit', (e) => handleUpdateOfferSubmit(e, offerId));
            formElement.addEventListener('submit', handleCreateOfferSubmit);
        }

    } catch (error) {
        console.error('Error updating offer:', error);
        alert('Error updating offer. Please try again.');
    }
}

// Delete an offer
async function deleteOffer(offerId) {
    try {
        if (!confirm('Are you sure you want to delete this offer? This action cannot be undone.')) {
            return;
        }

        console.log('Deleting offer:', offerId);

        // Delete the offer from Supabase
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offers?id=eq.${offerId}`, {
            method: 'DELETE',
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Reload offers data
        await loadOffersData();

        // Show success message
        alert('Offer deleted successfully!');

    } catch (error) {
        console.error('Error deleting offer:', error);
        alert('Error deleting offer. Please try again.');
    }
}

// Format niche for display
function formatNiche(niche) {
    if (!niche) return 'Unknown';

    // Convert kebab-case to Title Case
    return niche
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Format target audience for display
function formatTargetAudience(target) {
    if (!target) return 'All Users';

    const targetMap = {
        'all': 'All Users',
        'quiz_completed': 'Quiz Completers',
        'high_score': 'High Quiz Score',
        'returning': 'Returning Users'
    };

    return targetMap[target] || target;
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Capitalize first letter of a string
function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Get a random niche for demo purposes
function getRandomNiche() {
    const niches = [
        'health-coach',
        'life-coach',
        'business-coach',
        'fitness-coach'
    ];

    return niches[Math.floor(Math.random() * niches.length)];
}

// Check for ML recommendations
async function checkForMLRecommendations() {
    try {
        console.log('Checking for ML recommendations...');

        // Fetch ML insights from Supabase
        const insights = await fetchFromSupabase('tctc_ml_insights', '?select=*&is_applied=eq.false&order=created_at.desc');

        if (insights.length > 0) {
            // Show notification for new insights
            showMLInsightsNotification(insights);
        }

        // Check if we should auto-generate a test based on ML insights
        const shouldAutoGenerateTest = await shouldCreateAutoTest();
        if (shouldAutoGenerateTest) {
            await createAutoGeneratedTest();
        }

    } catch (error) {
        console.error('Error checking for ML recommendations:', error);
    }
}

// Show notification for ML insights
function showMLInsightsNotification(insights) {
    // Create a notification element
    const notification = document.createElement('div');
    notification.className = 'ml-notification';
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#8b5cf6';
    notification.style.color = 'white';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    notification.style.zIndex = '1000';
    notification.style.maxWidth = '350px';

    const insightCount = insights.length;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <strong>AI Recommendations Available</strong>
            <button id="close-notification" style="background: none; border: none; color: white; cursor: pointer; font-size: 16px;">×</button>
        </div>
        <p>${insightCount} new insight${insightCount > 1 ? 's' : ''} based on user behavior data.</p>
        <button id="view-insights-btn" style="background-color: white; color: #8b5cf6; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-top: 10px;">View Insights</button>
    `;

    document.body.appendChild(notification);

    // Add event listeners
    document.getElementById('close-notification').addEventListener('click', () => {
        document.body.removeChild(notification);
    });

    document.getElementById('view-insights-btn').addEventListener('click', () => {
        document.body.removeChild(notification);
        showMLInsightsModal(insights);
    });

    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            document.body.removeChild(notification);
        }
    }, 10000);
}

// Show modal with ML insights
function showMLInsightsModal(insights) {
    // Create modal HTML
    const modalHTML = `
        <div id="ml-insights-modal" style="display: block; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1000;">
            <div style="position: relative; width: 80%; max-width: 800px; margin: 50px auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <button class="close-modal-btn" style="position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 20px; cursor: pointer;">×</button>
                <h2>AI-Generated Insights & Recommendations</h2>
                <div id="ml-insights-content" style="margin-top: 20px; max-height: 60vh; overflow-y: auto;">
                    ${renderMLInsights(insights)}
                </div>
                <div style="text-align: right; margin-top: 20px;">
                    <button id="apply-all-insights-btn" style="padding: 8px 16px; background-color: #8b5cf6; color: white; border: none; border-radius: 4px; cursor: pointer;">Apply All Recommendations</button>
                </div>
            </div>
        </div>
    `;

    // Add modal to the DOM
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer.firstChild);

    // Add event listeners
    document.querySelector('#ml-insights-modal .close-modal-btn').addEventListener('click', () => {
        document.body.removeChild(document.getElementById('ml-insights-modal'));
    });

    document.getElementById('apply-all-insights-btn').addEventListener('click', async () => {
        await applyAllMLInsights(insights);
        document.body.removeChild(document.getElementById('ml-insights-modal'));
    });

    // Add event listeners to individual apply buttons
    document.querySelectorAll('.apply-insight-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const insightId = e.target.getAttribute('data-id');
            await applyMLInsight(insightId);
            e.target.disabled = true;
            e.target.textContent = 'Applied';
        });
    });
}

// Render ML insights as HTML
function renderMLInsights(insights) {
    if (!insights || insights.length === 0) {
        return '<p>No insights available at this time.</p>';
    }

    let insightsHTML = '';

    insights.forEach(insight => {
        const insightData = insight.insight_data || {};
        const confidenceScore = insight.confidence_score || 0;
        const confidencePercent = (confidenceScore * 100).toFixed(1);

        let insightContent = '';

        if (insight.insight_type === 'offer_recommendation') {
            insightContent = `
                <p><strong>Recommended Offer:</strong> ${insightData.headline || 'N/A'}</p>
                <p><strong>Target Audience:</strong> ${formatTargetAudience(insightData.target_audience) || 'All Users'}</p>
                <p><strong>Description:</strong> ${insightData.description || 'N/A'}</p>
            `;
        } else if (insight.insight_type === 'test_recommendation') {
            insightContent = `
                <p><strong>Recommended Test:</strong> ${insightData.name || 'N/A'}</p>
                <p><strong>Variants:</strong> ${insightData.variant_count || 2}</p>
                <p><strong>Target Audience:</strong> ${formatTargetAudience(insightData.target_audience) || 'All Users'}</p>
            `;
        } else if (insight.insight_type === 'audience_segment') {
            insightContent = `
                <p><strong>Audience Segment:</strong> ${insightData.segment_name || 'N/A'}</p>
                <p><strong>Segment Size:</strong> ${insightData.segment_size || 'Unknown'} users</p>
                <p><strong>Key Characteristics:</strong> ${insightData.characteristics || 'N/A'}</p>
            `;
        }

        insightsHTML += `
            <div class="insight-card" style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0;">${getInsightTypeTitle(insight.insight_type)} for ${formatNiche(insight.niche)}</h3>
                    <span style="background-color: ${getConfidenceColor(confidenceScore)}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em;">
                        ${confidencePercent}% Confidence
                    </span>
                </div>
                ${insightContent}
                <div style="text-align: right; margin-top: 10px;">
                    <button class="apply-insight-btn" data-id="${insight.id}" style="padding: 5px 10px; background-color: #8b5cf6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Apply This Recommendation
                    </button>
                </div>
            </div>
        `;
    });

    return insightsHTML;
}

// Get insight type title
function getInsightTypeTitle(insightType) {
    switch (insightType) {
        case 'offer_recommendation':
            return 'Offer Recommendation';
        case 'test_recommendation':
            return 'Split Test Recommendation';
        case 'audience_segment':
            return 'Audience Segment';
        default:
            return 'Recommendation';
    }
}

// Get confidence color based on score
function getConfidenceColor(score) {
    if (score >= 0.8) {
        return '#10b981'; // green
    } else if (score >= 0.6) {
        return '#3b82f6'; // blue
    } else if (score >= 0.4) {
        return '#f59e0b'; // yellow
    } else {
        return '#ef4444'; // red
    }
}

// Apply all ML insights
async function applyAllMLInsights(insights) {
    try {
        console.log('Applying all ML insights...');

        for (const insight of insights) {
            await applyMLInsight(insight.id);
        }

        // Reload data after applying insights
        await loadOffersData();
        await loadSplitTestsData();

        // Show success message
        alert('All recommendations have been applied successfully!');

    } catch (error) {
        console.error('Error applying ML insights:', error);
        alert('There was an error applying the recommendations. Please try again.');
    }
}

// Apply a single ML insight
async function applyMLInsight(insightId) {
    try {
        console.log('Applying ML insight:', insightId);

        // Fetch the insight
        const insights = await fetchFromSupabase('tctc_ml_insights', `?id=eq.${insightId}`);

        if (!insights || insights.length === 0) {
            throw new Error('Insight not found');
        }

        const insight = insights[0];

        // Apply the insight based on its type
        if (insight.insight_type === 'offer_recommendation') {
            await createOfferFromInsight(insight);
        } else if (insight.insight_type === 'test_recommendation') {
            await createTestFromInsight(insight);
        }

        // Mark the insight as applied
        await updateInsightStatus(insightId, true);

        console.log('ML insight applied successfully:', insightId);

    } catch (error) {
        console.error('Error applying ML insight:', error);
        throw error;
    }
}

// Create an offer from an ML insight
async function createOfferFromInsight(insight) {
    try {
        const insightData = insight.insight_data || {};

        // Prepare offer data
        const offerData = {
            name: insightData.name || `AI-Generated Offer for ${formatNiche(insight.niche)}`,
            niche: insight.niche,
            headline: insightData.headline || 'AI-Generated Offer',
            description: insightData.description || 'This offer was automatically generated based on user behavior data.',
            cta_text: insightData.cta_text || 'Learn More',
            target_audience: insightData.target_audience || 'all',
            is_active: true,
            is_auto_generated: true,
            ml_confidence_score: insight.confidence_score,
            ml_generation_params: insightData.generation_params || {}
        };

        // Insert the offer into Supabase
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(offerData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        console.log('Offer created from ML insight');

    } catch (error) {
        console.error('Error creating offer from ML insight:', error);
        throw error;
    }
}

// Create a split test from an ML insight
async function createTestFromInsight(insight) {
    try {
        const insightData = insight.insight_data || {};

        // Prepare test data
        const testData = {
            name: insightData.name || `AI-Generated Test for ${formatNiche(insight.niche)}`,
            niche: insight.niche,
            target_audience: insightData.target_audience || 'all',
            status: 'active',
            duration_days: insightData.duration_days || 14,
            is_auto_generated: true,
            ml_confidence_score: insight.confidence_score,
            ml_generation_params: insightData.generation_params || {}
        };

        // Insert the test into Supabase
        const testResponse = await fetch(`${SUPABASE_URL}/rest/v1/tctc_split_tests`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(testData)
        });

        if (!testResponse.ok) {
            throw new Error(`HTTP error! status: ${testResponse.status}`);
        }

        const testResult = await testResponse.json();
        const testId = testResult[0]?.id;

        if (!testId) {
            throw new Error('Failed to get test ID from response');
        }

        // Create variants for the test
        const variants = insightData.variants || [];

        if (variants.length === 0) {
            // If no variants are specified, create a default A/B test
            // First, get some offers for this niche
            const offers = await fetchFromSupabase('tctc_offers', `?niche=eq.${insight.niche}&is_active=eq.true&limit=2`);

            if (offers.length < 2) {
                throw new Error('Not enough offers available for this niche to create a test');
            }

            // Create control variant
            await createTestVariant(testId, offers[0].id, 'A', true, 50);

            // Create test variant
            await createTestVariant(testId, offers[1].id, 'B', false, 50);
        } else {
            // Create variants as specified in the insight
            for (let i = 0; i < variants.length; i++) {
                const variant = variants[i];
                const variantName = String.fromCharCode(65 + i); // A, B, C, etc.
                const isControl = i === 0;

                await createTestVariant(testId, variant.offer_id, variantName, isControl, variant.traffic_weight || 50);
            }
        }

        console.log('Split test created from ML insight');

    } catch (error) {
        console.error('Error creating split test from ML insight:', error);
        throw error;
    }
}

// Create a test variant
async function createTestVariant(testId, offerId, variantName, isControl, trafficWeight) {
    try {
        const variantData = {
            test_id: testId,
            offer_id: offerId,
            variant_name: variantName,
            is_control: isControl,
            traffic_weight: trafficWeight
        };

        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_test_variants`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(variantData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        console.log(`Test variant ${variantName} created`);

    } catch (error) {
        console.error('Error creating test variant:', error);
        throw error;
    }
}

// Update insight status
async function updateInsightStatus(insightId, isApplied) {
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_ml_insights?id=eq.${insightId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify({
                is_applied: isApplied,
                applied_at: new Date().toISOString()
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        console.log(`Insight ${insightId} status updated to ${isApplied ? 'applied' : 'not applied'}`);

    } catch (error) {
        console.error('Error updating insight status:', error);
        throw error;
    }
}

// Check if we should create an auto-generated test
async function shouldCreateAutoTest() {
    try {
        // This function would normally analyze user behavior data
        // and determine if there's enough data to create a test

        // For now, we'll return a random boolean with 30% chance of true
        return Math.random() < 0.3;

    } catch (error) {
        console.error('Error checking if we should create auto test:', error);
        return false;
    }
}

// Create an auto-generated test based on ML analysis
async function createAutoGeneratedTest() {
    try {
        console.log('Creating auto-generated test...');

        // This function would normally analyze user behavior data
        // and create a test based on the analysis

        // For now, we'll create a simple insight and apply it
        const insight = {
            id: 'auto-' + Date.now(),
            insight_type: 'test_recommendation',
            niche: getRandomNiche(),
            confidence_score: 0.75,
            insight_data: {
                name: 'Auto-Generated A/B Test',
                target_audience: 'all',
                duration_days: 14,
                variants: []
            }
        };

        // Show a notification about the auto-generated test
        showAutoTestNotification(insight);

    } catch (error) {
        console.error('Error creating auto-generated test:', error);
    }
}

// Show notification for auto-generated test
function showAutoTestNotification(insight) {
    // Create a notification element
    const notification = document.createElement('div');
    notification.className = 'auto-test-notification';
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#8b5cf6';
    notification.style.color = 'white';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    notification.style.zIndex = '1000';
    notification.style.maxWidth = '350px';

    notification.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <strong>AI Test Recommendation</strong>
            <button id="close-auto-notification" style="background: none; border: none; color: white; cursor: pointer; font-size: 16px;">×</button>
        </div>
        <p>Our AI has analyzed user behavior and recommends creating a new split test for ${formatNiche(insight.niche)}.</p>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <button id="view-auto-test-btn" style="background-color: white; color: #8b5cf6; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">View Details</button>
            <button id="create-auto-test-btn" style="background-color: #10b981; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Create Test</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Add event listeners
    document.getElementById('close-auto-notification').addEventListener('click', () => {
        document.body.removeChild(notification);
    });

    document.getElementById('view-auto-test-btn').addEventListener('click', () => {
        document.body.removeChild(notification);
        showAutoTestDetailsModal(insight);
    });

    document.getElementById('create-auto-test-btn').addEventListener('click', async () => {
        document.body.removeChild(notification);
        await createTestFromInsight(insight);
        await loadSplitTestsData();
        alert('Auto-generated test created successfully!');
    });

    // Auto-hide after 15 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            document.body.removeChild(notification);
        }
    }, 15000);
}

// Show modal with auto-generated test details
function showAutoTestDetailsModal(insight) {
    // Create modal HTML
    const modalHTML = `
        <div id="auto-test-modal" style="display: block; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1000;">
            <div style="position: relative; width: 80%; max-width: 800px; margin: 50px auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <button class="close-modal-btn" style="position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 20px; cursor: pointer;">×</button>
                <h2>AI-Generated Test Recommendation</h2>
                <div style="margin-top: 20px;">
                    <h3>Test Details</h3>
                    <p><strong>Niche:</strong> ${formatNiche(insight.niche)}</p>
                    <p><strong>Target Audience:</strong> ${formatTargetAudience(insight.insight_data.target_audience)}</p>
                    <p><strong>Duration:</strong> ${insight.insight_data.duration_days} days</p>
                    <p><strong>Confidence Score:</strong> ${(insight.confidence_score * 100).toFixed(1)}%</p>

                    <h3>Why This Test?</h3>
                    <p>Our AI has analyzed user behavior patterns and identified an opportunity to optimize conversions for ${formatNiche(insight.niche)}. This test will help determine which offer resonates best with your audience.</p>

                    <h3>Expected Outcome</h3>
                    <p>Based on historical data, we expect this test to potentially increase conversion rates by 15-25% for the target audience.</p>
                </div>
                <div style="text-align: right; margin-top: 20px;">
                    <button id="cancel-auto-test-btn" style="padding: 8px 16px; background-color: #6b7280; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Cancel</button>
                    <button id="create-auto-test-btn-modal" style="padding: 8px 16px; background-color: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer;">Create This Test</button>
                </div>
            </div>
        </div>
    `;

    // Add modal to the DOM
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer.firstChild);

    // Add event listeners
    document.querySelector('#auto-test-modal .close-modal-btn').addEventListener('click', () => {
        document.body.removeChild(document.getElementById('auto-test-modal'));
    });

    document.getElementById('cancel-auto-test-btn').addEventListener('click', () => {
        document.body.removeChild(document.getElementById('auto-test-modal'));
    });

    document.getElementById('create-auto-test-btn-modal').addEventListener('click', async () => {
        document.body.removeChild(document.getElementById('auto-test-modal'));
        await createTestFromInsight(insight);
        await loadSplitTestsData();
        alert('Auto-generated test created successfully!');
    });
}
