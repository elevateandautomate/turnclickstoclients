/**
 * Direct fix for undefined functions
 * This script directly defines the missing functions in the global scope
 */

// Define the functions immediately
window.showExistingAssetsFlow = function() {
  console.log("Direct fix: showExistingAssetsFlow called");
  
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (existingAssetsFlow) existingAssetsFlow.style.display = 'block';
  
  const setupGuide = document.getElementById('setup-guide');
  if (setupGuide) setupGuide.style.display = 'none';
};

window.showSetupGuide = function() {
  console.log("Direct fix: showSetupGuide called");
  
  const setupGuide = document.getElementById('setup-guide');
  if (setupGuide) setupGuide.style.display = 'block';
  
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (existingAssetsFlow) existingAssetsFlow.style.display = 'none';
};

// Apply immediately
console.log("Direct fix script loaded and applied!");

// For testing from console
function testAssetFlow() {
  window.showExistingAssetsFlow();
  console.log("Test: showExistingAssetsFlow executed");
}

function testSetupGuide() {
  window.showSetupGuide();
  console.log("Test: showSetupGuide executed");
} 