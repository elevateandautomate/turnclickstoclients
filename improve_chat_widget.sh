#!/bin/bash

# Update the chat button HTML to use a better icon
sed -i 's|<span>í²¬</span> Have a ?<br>Click Here To Send Us a Instant Message|<span><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></span> Chat|g' index.html

# Update the chat button HTML in the website/index.html file
sed -i 's|<span>í²¬</span> Have a ?<br>Click Here To Send Us a Instant Message|<span><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></span> Chat|g' website/index.html

# Create a new CSS file for the improved chat widget
cat > chat_widget_improvements.css << 'CSSEOF'
/* Improved Chat Widget Styles */

/* Desktop Chat Button */
#chat-widget-button {
    position: fixed;
    bottom: 25px;
    right: 25px;
    background-color: #007bff;
    color: white;
    padding: 12px 20px;
    border-radius: 50px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    cursor: pointer;
    z-index: 1000;
    display: flex;
    align-items: center;
    font-size: 1em;
    font-weight: 600;
    transition: all 0.3s ease;
}

#chat-widget-button:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}

#chat-widget-button span {
    margin-right: 8px;
    display: flex;
    align-items: center;
}

/* Mobile Chat Button */
@media (max-width: 768px) {
    #chat-widget-button {
        padding: 0 !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0 !important;
        line-height: 0 !important;
        bottom: 20px !important;
        right: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        /* Fix for when scrolling - keep it in view */
        position: fixed !important;
        z-index: 1500 !important;
    }

    #chat-widget-button span {
        margin-right: 0 !important;
        font-size: 1.5em !important;
    }
    
    #chat-widget-button svg {
        width: 28px !important;
        height: 28px !important;
    }
}

/* Improved Chat Modal */
.chat-modal-content {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    width: 90%;
    max-width: 500px;
    max-height: 85vh;
    overflow-y: auto;
    transform: scale(0.95);
    transition: all 0.3s ease;
    border: 1px solid rgba(0,0,0,0.1);
}

#chat-modal.modal-visible .chat-modal-content {
    transform: scale(1);
}

.chat-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eaeaea;
    padding-bottom: 15px;
    margin-bottom: 20px;
}

.chat-modal-header h2 {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.6em;
    color: #0056b3;
    font-weight: 700;
    margin: 0;
}

.chat-close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
    transition: color 0.2s ease;
    padding: 0;
    margin: 0;
    line-height: 1;
}

.chat-close-button:hover {
    color: #333;
}

.chat-modal-body {
    margin-bottom: 20px;
}

.chat-modal-body p {
    color: #555;
    line-height: 1.6;
    margin-bottom: 15px;
}

/* Form styling */
.chat-modal-body .form-group {
    margin-bottom: 18px;
}

.chat-modal-body label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    color: #444;
    font-size: 0.95em;
}

.chat-modal-body input,
.chat-modal-body select,
.chat-modal-body textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1em;
    transition: border-color 0.2s ease;
    background-color: #f9f9f9;
}

.chat-modal-body input:focus,
.chat-modal-body select:focus,
.chat-modal-body textarea:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
}

.chat-modal-body button[type="submit"] {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
    width: 100%;
    font-size: 1em;
}

.chat-modal-body button[type="submit"]:hover {
    background-color: #0056b3;
}

/* Mobile Modal Adjustments */
@media (max-width: 768px) {
    .chat-modal-content {
        width: 95%;
        max-height: 90vh;
        padding: 20px;
        margin: 20px;
    }
    
    .chat-modal-header h2 {
        font-size: 1.4em;
    }
    
    .chat-modal-body {
        font-size: 0.95em;
    }
}
CSSEOF

# Copy the chat widget improvements CSS to all directories
cp chat_widget_improvements.css website/
cp chat_widget_improvements.css apps/
cp chat_widget_improvements.css coldoutbound/

# Add the chat widget improvements CSS to the index.html file
sed -i '/<link rel="stylesheet" href="hamburger_fix.css">/a \    <link rel="stylesheet" href="chat_widget_improvements.css">' index.html

# Add the chat widget improvements CSS to the website/index.html file
sed -i '/<link rel="stylesheet" href="hamburger_fix.css">/a \    <link rel="stylesheet" href="chat_widget_improvements.css">' website/index.html

# Add the chat widget improvements CSS to all niche pages
find niches -name "*.html" -exec sed -i '/<link rel="stylesheet" href="..\/hamburger_fix.css">/a \    <link rel="stylesheet" href="../chat_widget_improvements.css">' {} \;

# Add the chat widget improvements CSS to all website/niche pages
find website/niches -name "*.html" -exec sed -i '/<link rel="stylesheet" href="..\/..\/hamburger_fix.css">/a \    <link rel="stylesheet" href="../../chat_widget_improvements.css">' {} \;

# Add the chat widget improvements CSS to the onboarding portal
sed -i '/<link rel="stylesheet" href="..\/..\/hamburger_fix.css">/a \    <link rel="stylesheet" href="../../chat_widget_improvements.css">' apps/onboarding/index.html

# Add the chat widget improvements CSS to the dashboard
sed -i '/<link rel="stylesheet" href="..\/..\/..\/hamburger_fix.css">/a \    <link rel="stylesheet" href="../../../chat_widget_improvements.css">' apps/dashboard/agencydashboard/index.html

echo "Chat widget improvements applied."
