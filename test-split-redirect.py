#!/usr/bin/env python3
"""
Script to test the split test redirect functionality.
This script will:
1. Open a browser to a main variant page
2. Check the console logs for redirect messages
3. Verify that the redirect is working correctly
"""

import os
import time
import webbrowser
import http.server
import socketserver
import threading
import sys

# Port for the local server
PORT = 8000

# Path to the main variant page to test
TEST_PAGE = "quiz-applications/cosmetic-dentistry/foundation/foundation-variant-a-solution.html"

def start_server():
    """Start a local HTTP server."""
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()

def open_browser():
    """Open the browser to the test page."""
    url = f"http://localhost:{PORT}/{TEST_PAGE}"
    print(f"Opening browser to {url}")
    webbrowser.open(url)

def main():
    """Main function."""
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for the server to start
    time.sleep(1)
    
    # Open the browser
    open_browser()
    
    # Wait for user to check the console logs
    print("\nPlease check the browser console logs for redirect messages.")
    print("The script should be logging debug information about the redirect process.")
    print("If the redirect is working, you should be redirected to a split test variation.")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
