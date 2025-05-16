#!/bin/bash

# Create a temporary file
cat > temp_chat_button.html << 'HTMLEOF'
    <div id="chat-widget-button">
        <span><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></span> Chat
    </div>
HTMLEOF

# Replace the chat button in index.html
awk '
/id="chat-widget-button"/ {
    getline; getline;
    system("cat temp_chat_button.html");
    next;
}
/id="chat-widget-button"/ { p=1 }
p && /^    <\/div>/ { p=0; next }
!p { print }
' index.html > index.html.new && mv index.html.new index.html

# Replace the chat button in website/index.html
awk '
/id="chat-widget-button"/ {
    getline; getline;
    system("cat temp_chat_button.html");
    next;
}
/id="chat-widget-button"/ { p=1 }
p && /^    <\/div>/ { p=0; next }
!p { print }
' website/index.html > website/index.html.new && mv website/index.html.new website/index.html

# Clean up
rm temp_chat_button.html

echo "Chat button updated."
