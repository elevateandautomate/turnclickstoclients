/**
 * Split Test Distribution Test Script
 * 
 * This script tests the distribution of users across split test variations.
 * It simulates multiple visits to quiz result pages and tracks which split variation is shown.
 */

// Configuration
const BASE_URL = 'http://localhost'; // Change to your actual domain when deployed
const TEST_ITERATIONS = 100; // Number of test iterations to run

// Test combinations to check
const TEST_COMBINATIONS = [
  {
    niche: 'cosmetic-dentistry',
    bucket: 'foundation',
    variant: 'a-solution'
  },
  {
    niche: 'cosmetic-dentistry',
    bucket: 'foundation',
    variant: 'b-problem'
  },
  {
    niche: 'cosmetic-dentistry',
    bucket: 'foundation',
    variant: 'c-most-aware'
  },
  {
    niche: 'pmu-artists',
    bucket: 'growth',
    variant: 'a-solution'
  },
  {
    niche: 'child-care',
    bucket: 'enrollment',
    variant: 'a-solution'
  }
];

// Main test function
async function runSplitTestDistributionTest() {
  console.log('Starting split test distribution test...');
  console.log(`Running ${TEST_ITERATIONS} iterations for each combination...`);
  
  const results = {};
  
  for (const combo of TEST_COMBINATIONS) {
    const { niche, bucket, variant } = combo;
    const comboKey = `${niche}/${bucket}/${variant}`;
    
    console.log(`Testing combination: ${comboKey}`);
    
    results[comboKey] = {
      total: TEST_ITERATIONS,
      splits: {
        0: 0, // Main variation (no split)
        1: 0, // Split 1
        2: 0, // Split 2
        3: 0  // Split 3
      },
      errors: 0
    };
    
    for (let i = 0; i < TEST_ITERATIONS; i++) {
      try {
        // Create a unique URL with a random parameter to avoid caching
        const url = `${BASE_URL}/quiz-applications/${niche}/${bucket}/${bucket}-variant-${variant}.html?test=${Date.now()}-${Math.random()}`;
        
        // Use fetch with redirect: 'manual' to see the redirect without following it
        const response = await fetch(url, { redirect: 'manual' });
        
        // Check if there was a redirect (status 302)
        if (response.status === 302 || response.type === 'opaqueredirect') {
          // Get the redirect URL from the Location header
          const location = response.headers.get('Location');
          
          if (location) {
            // Extract the split parameter from the redirect URL
            const splitMatch = location.match(/split=(\d+)/);
            const split = splitMatch ? parseInt(splitMatch[1]) : 0;
            
            // Increment the count for this split
            results[comboKey].splits[split]++;
          } else {
            // No redirect URL found
            results[comboKey].splits[0]++;
          }
        } else {
          // No redirect, assume it's the main variation
          results[comboKey].splits[0]++;
        }
      } catch (error) {
        console.error(`Error in iteration ${i + 1} for ${comboKey}:`, error);
        results[comboKey].errors++;
      }
      
      // Add a small delay between requests
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Update progress every 10 iterations
      if ((i + 1) % 10 === 0 || i === TEST_ITERATIONS - 1) {
        console.log(`Progress for ${comboKey}: ${i + 1}/${TEST_ITERATIONS}`);
      }
    }
  }
  
  // Display results
  displayResults(results);
}

// Display test results
function displayResults(results) {
  console.log('Split Test Distribution Results:');
  console.log('===============================');
  
  for (const [combo, result] of Object.entries(results)) {
    console.log(`\nCombination: ${combo}`);
    console.log(`Total iterations: ${result.total}`);
    console.log(`Errors: ${result.errors}`);
    
    const validResults = result.total - result.errors;
    console.log(`Valid results: ${validResults}`);
    
    console.log('Split distribution:');
    for (const [split, count] of Object.entries(result.splits)) {
      const percentage = validResults > 0 ? ((count / validResults) * 100).toFixed(2) : 0;
      console.log(`  - Split ${split}: ${count} (${percentage}%)`);
    }
    
    // Check if distribution is roughly even (within 20% of expected)
    const expectedPerSplit = validResults / 3; // Should be evenly distributed among 3 splits
    const isBalanced = Object.entries(result.splits)
      .filter(([split, _]) => split !== '0') // Exclude the main variation
      .every(([_, count]) => Math.abs(count - expectedPerSplit) <= (expectedPerSplit * 0.2));
    
    if (isBalanced) {
      console.log('✅ Split test distribution is balanced');
    } else {
      console.log('⚠️ Split test distribution appears unbalanced');
    }
  }
  
  // Create a visual representation of the results
  createResultsChart(results);
}

// Create a visual chart of the results
function createResultsChart(results) {
  const chartContainer = document.getElementById('chart-container');
  if (!chartContainer) return;
  
  chartContainer.innerHTML = '';
  
  for (const [combo, result] of Object.entries(results)) {
    const comboContainer = document.createElement('div');
    comboContainer.className = 'combo-container';
    
    const comboTitle = document.createElement('h3');
    comboTitle.textContent = combo;
    comboContainer.appendChild(comboTitle);
    
    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart';
    
    const validResults = result.total - result.errors;
    
    for (const [split, count] of Object.entries(result.splits)) {
      if (split === '0') continue; // Skip the main variation in the chart
      
      const percentage = validResults > 0 ? ((count / validResults) * 100).toFixed(2) : 0;
      
      const bar = document.createElement('div');
      bar.className = 'bar';
      
      const barFill = document.createElement('div');
      barFill.className = 'bar-fill';
      barFill.style.width = `${percentage}%`;
      barFill.style.backgroundColor = getColorForSplit(split);
      
      const barLabel = document.createElement('div');
      barLabel.className = 'bar-label';
      barLabel.textContent = `Split ${split}`;
      
      const barValue = document.createElement('div');
      barValue.className = 'bar-value';
      barValue.textContent = `${count} (${percentage}%)`;
      
      bar.appendChild(barLabel);
      bar.appendChild(barFill);
      bar.appendChild(barValue);
      
      chartDiv.appendChild(bar);
    }
    
    comboContainer.appendChild(chartDiv);
    chartContainer.appendChild(comboContainer);
  }
}

// Get a color for a split variation
function getColorForSplit(split) {
  const colors = {
    '1': '#3b82f6', // Blue
    '2': '#10b981', // Green
    '3': '#f59e0b'  // Amber
  };
  
  return colors[split] || '#6b7280';
}

// Run the test when the button is clicked
document.addEventListener('DOMContentLoaded', function() {
  const runTestButton = document.getElementById('run-test-button');
  if (runTestButton) {
    runTestButton.addEventListener('click', runSplitTestDistributionTest);
  }
});
