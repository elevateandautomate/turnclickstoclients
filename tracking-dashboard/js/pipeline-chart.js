// Pipeline Chart Configuration and Rendering
console.log('Pipeline chart.js loading...');

// Store chart instance so it can be destroyed before recreating
let pipelineConversionChart = null;

// Pipeline Conversion Chart
function renderPipelineConversionChart(pageViews, quizStarts, quizCompletions, quizSubmissions) {
    const canvas = document.getElementById('pipeline-conversion-chart');
    if (!canvas) {
        console.error('Pipeline conversion chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (pipelineConversionChart) {
        pipelineConversionChart.destroy();
    }

    // For this example, we'll use some assumptions for qualified leads and customers
    // In a real implementation, you would fetch this data from your CRM or sales database
    const visitorCount = countUniqueUsers(pageViews);
    const quizTakerCount = countUniqueUsers(quizStarts);
    const applicantCount = countUniqueUsers(quizSubmissions);
    
    // Assuming 30% of applicants become qualified leads and 20% of qualified leads become customers
    const qualifiedLeadCount = Math.round(applicantCount * 0.3);
    const customerCount = Math.round(qualifiedLeadCount * 0.2);
    
    // Calculate conversion rates between stages
    const stageLabels = ['Visitor to Quiz', 'Quiz to Application', 'Application to Qualified', 'Qualified to Customer'];
    const conversionRates = [
        quizTakerCount > 0 && visitorCount > 0 ? Math.round((quizTakerCount / visitorCount) * 100) : 0,
        applicantCount > 0 && quizTakerCount > 0 ? Math.round((applicantCount / quizTakerCount) * 100) : 0,
        qualifiedLeadCount > 0 && applicantCount > 0 ? Math.round((qualifiedLeadCount / applicantCount) * 100) : 0,
        customerCount > 0 && qualifiedLeadCount > 0 ? Math.round((customerCount / qualifiedLeadCount) * 100) : 0
    ];
    
    // Create chart
    pipelineConversionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stageLabels,
            datasets: [{
                label: 'Conversion Rate (%)',
                data: conversionRates,
                backgroundColor: [
                    '#3b82f6', // Blue
                    '#10b981', // Green
                    '#f59e0b', // Amber
                    '#ef4444'  // Red
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Conversion Rate (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Pipeline Stage'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Conversion Rate: ${context.raw}%`;
                        }
                    }
                }
            }
        }
    });
}

// Helper function to count unique users
function countUniqueUsers(data) {
    if (!Array.isArray(data)) {
        console.error('Data is not an array:', data);
        return 0;
    }
    
    const uniqueUsers = new Set();
    data.forEach(item => {
        // Create a composite key from user_first_name, user_last_name, and user_email
        const userId = `${item.user_first_name || ''}_${item.user_last_name || ''}_${item.user_email || ''}`.toLowerCase();
        if (userId && userId !== '__') {
            uniqueUsers.add(userId);
        }
    });
    return uniqueUsers.size;
}
