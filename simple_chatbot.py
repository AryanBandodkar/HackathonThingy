#!/usr/bin/env python3
"""
Simple FloatChat AI Assistant - Console Version
A simplified version that works without Streamlit dependencies
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

from ai_chatbot import AIChatbot

def print_header():
    """Print application header"""
    print("🌊 FloatChat - Oceanographic Data AI Assistant")
    print("=" * 50)
    print("Type 'help' for available commands or 'quit' to exit")
    print("=" * 50)

def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("  help          - Show this help message")
    print("  quit/exit     - Exit the application")
    print("  clear         - Clear conversation history")
    print("  summary       - Show data summary")
    print("  stats         - Show database statistics")
    print("\n💬 Sample Queries:")
    print("  • Show me a summary of the data")
    print("  • Find profiles with temperature above 15 degrees")
    print("  • What's the salinity range?")
    print("  • Show me locations with high pressure")
    print("  • How many profiles are there?")
    print("  • Find profiles near latitude 40 degrees")
    print("  • Show me the temperature distribution")

def print_stats(chatbot):
    """Print database statistics"""
    print("\n📊 Database Statistics:")
    
    # Get summary
    summary_query = "Show me a summary of the data"
    result = chatbot.process_user_input(summary_query)
    
    if result['success']:
        print(result['response'])
    else:
        print(f"Error getting statistics: {result['error']}")

def main():
    """Main application loop"""
    print_header()
    
    # Initialize chatbot
    try:
        chatbot = AIChatbot()
        print("✅ AI Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize AI Assistant: {e}")
        return
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'clear':
                chatbot.clear_history()
                print("🗑️ Conversation history cleared!")
                continue
            elif user_input.lower() in ['summary', 'stats']:
                print_stats(chatbot)
                continue
            elif not user_input:
                continue
            
            # Process with AI chatbot
            print("🤖 AI Assistant: ", end="")
            result = chatbot.process_user_input(user_input)
            
            if result['success']:
                print(result['response'])
                
                # Show query if user wants to see it
                if 'query' in result and result['query']:
                    show_query = input("\n🔍 Show SQL query? (y/n): ").strip().lower()
                    if show_query in ['y', 'yes']:
                        print(f"\nSQL Query:\n{result['query']}")
            else:
                print(f"❌ Error: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
