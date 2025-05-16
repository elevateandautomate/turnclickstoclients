// Chart Configuration and Rendering

// Store chart instances so they can be destroyed before recreating
let trafficSourceChart = null;
let nicheConversionChart = null;
let activityTimelineChart = null;
let dropoutChart = null;

// Color palette for charts
const chartColors = [
    '#3b82f6', // Primary blue
    '#10b981', // Green
    '#f59e0b', // Amber
    '#ef4444', // Red
    '#8b5cf6', // Purple
    '#ec4899', // Pink
    '#06b6d4', // Cyan
    '#f97316', // Orange
    '#14b8a6', // Teal
    '#6366f1'  // Indigo
];

// Traffic Source Chart
function renderTrafficSourceChart(data) {
    const canvas = document.getElementById('traffic-source-chart');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (trafficSourceChart) {
        trafficSourceChart.destroy();
    }

    // Process data
    const sourceCount = {};
    data.forEach(item => {
        const source = item.original_source || item.track_source || 'unknown';
        sourceCount[source] = (sourceCount[source] || 0) + 1;
    });

    const labels = Object.keys(sourceCount);
    const counts = Object.values(sourceCount);

    // Create chart
    trafficSourceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: chartColors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Niche Conversion Chart
function renderNicheConversionChart(quizStarts, quizCompletions) {
    const canvas = document.getElementById('niche-conversion-chart');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (nicheConversionChart) {
        nicheConversionChart.destroy();
    }

    // Process data
    const niches = {};

    // Count quiz starts by niche
    quizStarts.forEach(item => {
        const niche = item.niche || 'unknown';
        if (!niches[niche]) {
            niches[niche] = { starts: 0, completions: 0 };
        }
        niches[niche].starts++;
    });

    // Count quiz completions by niche
    quizCompletions.forEach(item => {
        const niche = item.niche || 'unknown';
        if (!niches[niche]) {
            niches[niche] = { starts: 0, completions: 0 };
        }
        niches[niche].completions++;
    });

    // Calculate conversion rates
    const nicheLabels = Object.keys(niches);
    const conversionRates = nicheLabels.map(niche => {
        const { starts, completions } = niches[niche];
        return starts > 0 ? Math.round((completions / starts) * 100) : 0;
    });

    // Create chart
    nicheConversionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: nicheLabels,
            datasets: [{
                label: 'Conversion Rate (%)',
                data: conversionRates,
                backgroundColor: chartColors[0],
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
                        text: 'Niche'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const niche = context.label;
                            const rate = context.raw;
                            const starts = niches[niche].starts;
                            const completions = niches[niche].completions;
                            return [
                                `Conversion Rate: ${rate}%`,
                                `Starts: ${starts}`,
                                `Completions: ${completions}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Activity Timeline Chart
function renderActivityTimelineChart(data) {
    const canvas = document.getElementById('activity-timeline-chart');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (activityTimelineChart) {
        activityTimelineChart.destroy();
    }

    // Process data
    const timelineData = {};
    const now = new Date();
    const startDate = new Date(now);
    startDate.setDate(startDate.getDate() - 6);

    // Initialize timeline with zeros for the last 7 days
    for (let i = 0; i < 7; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        const dateString = date.toISOString().split('T')[0];
        timelineData[dateString] = { pageViews: 0, quizStarts: 0, quizCompletions: 0 };
    }

    // Count events by date
    data.forEach(item => {
        const date = new Date(item.timestamp);
        const dateString = date.toISOString().split('T')[0];

        if (timelineData[dateString]) {
            if (item.action_type === 'page_view') {
                timelineData[dateString].pageViews++;
            } else if (item.action_type === 'quiz_started') {
                timelineData[dateString].quizStarts++;
            } else if (item.action_type === 'quiz_completed') {
                timelineData[dateString].quizCompletions++;
            }
        }
    });

    const labels = Object.keys(timelineData);
    const pageViews = labels.map(date => timelineData[date].pageViews);
    const quizStarts = labels.map(date => timelineData[date].quizStarts);
    const quizCompletions = labels.map(date => timelineData[date].quizCompletions);

    // Format labels as readable dates
    const formattedLabels = labels.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    // Create chart
    activityTimelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedLabels,
            datasets: [
                {
                    label: 'Page Views',
                    data: pageViews,
                    borderColor: chartColors[0],
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Quiz Starts',
                    data: quizStarts,
                    borderColor: chartColors[1],
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Quiz Completions',
                    data: quizCompletions,
                    borderColor: chartColors[2],
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

// Dropout Chart
function renderDropoutChart(journeys) {
    const canvas = document.getElementById('dropout-chart');
    if (!canvas) {
        console.error('Dropout chart canvas not found');
        return;
    }

    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (dropoutChart) {
        dropoutChart.destroy();
    }

    // Define the stages in order
    const stages = ['landing', 'quiz_start', 'quiz_completion', 'application'];
    const stageLabels = ['Landing Page', 'Quiz Start', 'Quiz Completion', 'Application'];

    // Count users at each stage
    const stageCounts = stages.map(() => 0);
    const userStages = {};

    // Process journeys to determine the furthest stage each user reached
    Object.values(journeys).forEach(events => {
        if (events && events.length > 0) {
            // Create a composite key from user_first_name, user_last_name, and user_email
            const userId = `${events[0].user_first_name || ''}_${events[0].user_last_name || ''}_${events[0].user_email || ''}`.toLowerCase();
            let furthestStage = -1;

            events.forEach(event => {
                if (event.action_type === 'page_view' && furthestStage < 0) {
                    furthestStage = 0; // landing
                } else if (event.action_type === 'quiz_started' && furthestStage < 1) {
                    furthestStage = 1; // quiz_start
                } else if (event.action_type === 'quiz_completed' && furthestStage < 2) {
                    furthestStage = 2; // quiz_completion
                } else if (event.action_type === 'form_submitted' && furthestStage < 3) {
                    furthestStage = 3; // application
                }
            });

            userStages[userId] = furthestStage;
        }
    });

    // Count users at each stage
    Object.values(userStages).forEach(stage => {
        if (stage >= 0 && stage < stages.length) {
            stageCounts[stage]++;
        }
    });

    // Create chart
    dropoutChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stageLabels,
            datasets: [{
                label: 'Users',
                data: stageCounts,
                backgroundColor: chartColors.slice(0, stages.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Users'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = Object.keys(userStages).length;
                            const percentage = Math.round((value / total) * 100);
                            return `Users: ${value} (${percentage}% of total)`;
                        }
                    }
                }
            }
        }
    });

    // Update flow visualization counts if elements exist
    const updateElement = (id, value) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    };

    updateElement('landing-count', stageCounts[0] || 0);
    updateElement('quiz-start-count', stageCounts[1] || 0);
    updateElement('quiz-completion-count', stageCounts[2] || 0);
    updateElement('application-count', stageCounts[3] || 0);

    // Calculate and update percentages if elements exist
    const total = stageCounts[0] || 0;
    if (total > 0) {
        updateElement('quiz-start-percentage', Math.round(((stageCounts[1] || 0) / total) * 100) + '%');
        updateElement('quiz-completion-percentage', Math.round(((stageCounts[2] || 0) / total) * 100) + '%');
        updateElement('application-percentage', Math.round(((stageCounts[3] || 0) / total) * 100) + '%');
    } else {
        // If no data, set percentages to 0%
        updateElement('quiz-start-percentage', '0%');
        updateElement('quiz-completion-percentage', '0%');
        updateElement('application-percentage', '0%');
    }
}
