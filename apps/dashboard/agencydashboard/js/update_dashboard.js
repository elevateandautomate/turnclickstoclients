const fs = require('fs');
const path = require('path');
const { performUpdateAndBackup } = require('./update_and_backup');

// Function to update the dashboard file
async function updateDashboard(updateFunction) {
    try {
        console.log('Starting dashboard update...');
        
        // Read the current dashboard file
        const dashboardPath = path.join(__dirname, 'clinehelpnowcursor.html');
        let content = fs.readFileSync(dashboardPath, 'utf8');
        
        // Apply the update
        const updatedContent = await updateFunction(content);
        
        // Write the updated content
        fs.writeFileSync(dashboardPath, updatedContent, 'utf8');
        
        // Verify and backup
        const success = await performUpdateAndBackup();
        
        if (success) {
            console.log('Dashboard updated and backed up successfully');
            return true;
        } else {
            console.error('Update verification failed');
            return false;
        }
    } catch (error) {
        console.error('Error updating dashboard:', error);
        return false;
    }
}

// Example update function
async function exampleUpdate(content) {
    // This is where you would implement your specific update logic
    // For example, updating a specific section or adding new features
    
    // Example: Update the title
    return content.replace(
        /<title>.*?<\/title>/,
        '<title>Updated Dashboard</title>'
    );
}

// Export the update function
module.exports = {
    updateDashboard
};

// If run directly, execute the example update
if (require.main === module) {
    updateDashboard(exampleUpdate)
        .then(success => {
            if (!success) {
                process.exit(1);
            }
        })
        .catch(error => {
            console.error('Fatal error:', error);
            process.exit(1);
        });
} 
 