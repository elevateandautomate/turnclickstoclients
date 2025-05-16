/**
 * ChatGPT Interface for Offer Page
 *
 * This file adds a ChatGPT-powered chat interface to the offer page
 * that allows users to ask questions about the offer.
 */

// Configuration - Use the same API key as the offer generation
// We'll get this from the openai-integration.js file
let chatApiKey = ''; // Will be populated from openai-integration.js
const OPENAI_MODEL = 'gpt-3.5-turbo'; // or 'gpt-4' if you have access
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

// Flag to determine if we're in demo mode (same as in openai-integration.js)
let chatDemoMode = true;

// Global variables
let chatHistory = [];
let offerContext = {};

/**
 * Initialize the ChatGPT interface
 */
function initChatGPTInterface() {
    // Create chat interface elements
    createChatInterface();

    // Set up event listeners
    setupChatEventListeners();

    // Extract offer context for better responses
    extractOfferContext();
}

/**
 * Create the chat interface elements
 */
function createChatInterface() {
    // Create chat container
    const chatContainer = document.createElement('div');
    chatContainer.id = 'chat-container';
    chatContainer.className = 'chat-container';
    chatContainer.innerHTML = `
        <div class="chat-header">
            <h3>Ask About This Offer</h3>
            <button id="chat-toggle" class="chat-toggle">Chat with AI</button>
        </div>
        <div id="chat-body" class="chat-body" style="display: none;">
            <div id="chat-messages" class="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" id="chat-input" class="chat-input" placeholder="Ask a question about this offer...">
                <button id="chat-send" class="chat-send">Send</button>
            </div>
        </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .chat-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            overflow: hidden;
        }

        .chat-header {
            background-color: #4a90e2;
            color: white;
            padding: 10px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header h3 {
            margin: 0;
            font-size: 16px;
        }

        .chat-toggle {
            background-color: white;
            color: #4a90e2;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }

        .chat-body {
            height: 400px;
            display: flex;
            flex-direction: column;
        }

        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
        }

        .chat-message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            max-width: 80%;
        }

        .user-message {
            background-color: #e9f5ff;
            margin-left: auto;
        }

        .ai-message {
            background-color: #f0f0f0;
            margin-right: auto;
        }

        .chat-input-container {
            display: flex;
            padding: 10px;
            border-top: 1px solid #eee;
        }

        .chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 10px;
        }

        .chat-send {
            background-color: #4a90e2;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
    `;

    // Add to document
    document.head.appendChild(style);
    document.body.appendChild(chatContainer);
}

/**
 * Set up event listeners for the chat interface
 */
function setupChatEventListeners() {
    // Toggle chat visibility
    const chatToggle = document.getElementById('chat-toggle');
    const chatBody = document.getElementById('chat-body');

    if (chatToggle && chatBody) {
        chatToggle.addEventListener('click', () => {
            const isVisible = chatBody.style.display !== 'none';
            chatBody.style.display = isVisible ? 'none' : 'flex';
            chatToggle.textContent = isVisible ? 'Chat with AI' : 'Close Chat';
        });
    }

    // Send message
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');

    if (chatInput && chatSend) {
        // Send on button click
        chatSend.addEventListener('click', () => {
            sendMessage();
        });

        // Send on Enter key
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

/**
 * Extract context from the offer to improve AI responses
 */
function extractOfferContext() {
    // Get offer details
    offerContext = {
        headline: document.getElementById('offer-headline')?.textContent || '',
        subheadline: document.getElementById('offer-subheadline')?.textContent || '',
        businessName: document.querySelector('.business-name-placeholder')?.textContent || 'the business',
        problemAgitation: document.getElementById('offer-problem-agitation')?.textContent || '',
        solution: document.getElementById('offer-solution-introduction')?.textContent || '',
        bulletPoints: Array.from(document.querySelectorAll('#offer-bullet-points li')).map(li => li.textContent),
        pricing: {
            growth: '$1,500/month',
            accelerate: '$2,500/month',
            fastTrack: '$3,500/month'
        }
    };

    console.log('Extracted offer context:', offerContext);
}

/**
 * Send a message to the ChatGPT API
 */
async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatInput || !chatMessages) return;

    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // Clear input
    chatInput.value = '';

    // Add user message to UI
    addMessageToUI('user', userMessage);

    // Add thinking indicator
    const thinkingId = addThinkingIndicator();

    try {
        // Add to chat history
        chatHistory.push({ role: 'user', content: userMessage });

        // If we're in demo mode or don't have an API key, use a canned response
        if (!chatApiKey) {
            await simulateAPICall(userMessage, thinkingId);
            return;
        }

        // Prepare system message with context
        const systemMessage = `You are a helpful assistant for TurnClicksToClients.com. You're helping answer questions about an offer that has been presented to ${offerContext.businessName}.

        The offer is about client acquisition services with the headline: "${offerContext.headline}"

        Key details about the offer:
        - Three pricing tiers: Growth Plan (${offerContext.pricing.growth}), Accelerate Plan (${offerContext.pricing.accelerate}), and Fast Track Plan (${offerContext.pricing.fastTrack})
        - The service helps businesses get more clients through digital marketing
        - The company handles everything from ads to lead follow-up
        - They guarantee results or the client doesn't pay

        Keep your answers concise, helpful, and focused on the offer details. If you don't know something specific, suggest they book a call to learn more.`;

        // Make API request
        const response = await fetch(OPENAI_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${chatApiKey}`
            },
            body: JSON.stringify({
                model: OPENAI_MODEL,
                messages: [
                    { role: 'system', content: systemMessage },
                    ...chatHistory
                ],
                temperature: 0.7,
                max_tokens: 150
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const aiMessage = data.choices[0].message.content;

        // Add AI response to chat history
        chatHistory.push({ role: 'assistant', content: aiMessage });

        // Remove thinking indicator and add AI message
        removeThinkingIndicator(thinkingId);
        addMessageToUI('ai', aiMessage);

    } catch (error) {
        console.error('Error sending message to ChatGPT:', error);
        removeThinkingIndicator(thinkingId);
        addMessageToUI('ai', "I'm sorry, I couldn't process your request. Please try again later.");
    }
}

/**
 * Simulate an API call for demo purposes
 */
async function simulateAPICall(userMessage, thinkingId) {
    // Wait for a realistic delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Generate a canned response based on the user's question
    let aiResponse = "I'm sorry, I don't have specific information about that. Would you like to schedule a call to discuss this with a representative?";

    const lowerCaseMessage = userMessage.toLowerCase();

    if (lowerCaseMessage.includes('price') || lowerCaseMessage.includes('cost') || lowerCaseMessage.includes('how much')) {
        aiResponse = "We offer three pricing tiers: Growth Plan ($1,500/month), Accelerate Plan ($2,500/month), and Fast Track Plan ($3,500/month). Each includes different levels of service and ad spend. Would you like to know more about what's included in each plan?";
    } else if (lowerCaseMessage.includes('guarantee') || lowerCaseMessage.includes('refund')) {
        aiResponse = "Yes, we offer a performance guarantee. If you don't see real, qualified appointments booked on your calendar and measurable growth within the first 30 days, you pay absolutely nothing for our service fee.";
    } else if (lowerCaseMessage.includes('how') && lowerCaseMessage.includes('work')) {
        aiResponse = "Our Client Attraction Engine handles every aspect of your client acquisition. We create ads, respond to leads 24/7, nurture prospects, and book qualified consultations directly into your calendar. You focus on serving clients while we handle the marketing.";
    } else if (lowerCaseMessage.includes('results') || lowerCaseMessage.includes('expect')) {
        aiResponse = "Most clients see a 40-50% increase in booked appointments within 60 days. Some see results in as little as 2 weeks. The exact results depend on your industry, location, and service offerings.";
    }

    // Remove thinking indicator and add AI message
    removeThinkingIndicator(thinkingId);
    addMessageToUI('ai', aiResponse);

    // Add to chat history
    chatHistory.push({ role: 'user', content: userMessage });
    chatHistory.push({ role: 'assistant', content: aiResponse });
}

/**
 * Add a message to the UI
 */
function addMessageToUI(role, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${role}-message`;
    messageElement.textContent = message;

    chatMessages.appendChild(messageElement);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Add a thinking indicator while waiting for a response
 */
function addThinkingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return null;

    const id = 'thinking-' + Date.now();
    const thinkingElement = document.createElement('div');
    thinkingElement.id = id;
    thinkingElement.className = 'chat-message ai-message';
    thinkingElement.innerHTML = '<div class="thinking-dots"><span>.</span><span>.</span><span>.</span></div>';

    // Add animation style
    const style = document.createElement('style');
    style.textContent = `
        .thinking-dots span {
            animation: thinking 1.4s infinite;
            animation-fill-mode: both;
            display: inline-block;
            margin-right: 2px;
        }

        .thinking-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .thinking-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes thinking {
            0% { opacity: 0.2; }
            20% { opacity: 1; }
            100% { opacity: 0.2; }
        }
    `;

    document.head.appendChild(style);
    chatMessages.appendChild(thinkingElement);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

/**
 * Remove the thinking indicator
 */
function removeThinkingIndicator(id) {
    if (!id) return;

    const thinkingElement = document.getElementById(id);
    if (thinkingElement) {
        thinkingElement.remove();
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Try to get the API key and demo mode from openai-integration.js
    if (window.openaiIntegration && window.openaiIntegration.getConfig) {
        const config = window.openaiIntegration.getConfig();
        if (config) {
            chatApiKey = config.apiKey || '';
            chatDemoMode = config.demoMode || true;
            console.log('ChatGPT interface using configuration from openai-integration.js');
        }
    }

    // Wait for the offer to load first
    const checkOfferLoaded = setInterval(() => {
        const offerContent = document.getElementById('offer-content');
        if (offerContent && offerContent.style.display !== 'none') {
            clearInterval(checkOfferLoaded);
            // Initialize ChatGPT interface after a short delay
            setTimeout(initChatGPTInterface, 1000);
        }
    }, 500);
});
