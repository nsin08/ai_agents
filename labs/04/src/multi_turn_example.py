"""
Multi-turn conversation example demonstrating memory accumulation.

This example shows how the MemoryAgent maintains context across multiple turns,
storing facts in long-term memory and conversation history in short-term memory.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from memory_agent import MemoryAgent


def run_conversation() -> None:
    """Run a 7-turn conversation demonstrating memory accumulation."""
    # Initialize agent with small short-term memory to demonstrate FIFO pruning
    agent = MemoryAgent(max_short_term=10)
    
    print("=" * 70)
    print("Multi-Turn Conversation Example - Memory Management")
    print("=" * 70)
    
    # Turn 1: User shares location
    print("\n--- Turn 1 ---")
    user_msg = "I live in Seattle"
    agent.add_conversation_turn("user", user_msg)
    # Extract fact and store in long-term memory
    agent.add_fact("User lives in Seattle", confidence=1.0, key="location")
    print(f"User: {user_msg}")
    agent_response = "Got it! I'll remember that you live in Seattle."
    agent.add_conversation_turn("assistant", agent_response)
    print(f"Agent: {agent_response}")
    print(f"Memory stats: {agent.get_memory_stats()}")
    
    # Turn 2: Query that requires location context
    print("\n--- Turn 2 ---")
    user_msg = "What's the weather like here?"
    agent.add_conversation_turn("user", user_msg)
    # Retrieve relevant memories
    memories = agent.retrieve("weather location Seattle", include_trace=True)
    print(f"User: {user_msg}")
    agent_response = "Based on your location in Seattle, I can help with the weather there."
    agent.add_conversation_turn("assistant", agent_response)
    print(f"Agent: {agent_response}")
    
    # Turn 3: User shares hobby
    print("\n--- Turn 3 ---")
    user_msg = "I like hiking"
    agent.add_conversation_turn("user", user_msg)
    agent.add_fact("User enjoys hiking", confidence=1.0, key="hobby_hiking")
    print(f"User: {user_msg}")
    agent_response = "Hiking is a great activity! I'll remember that."
    agent.add_conversation_turn("assistant", agent_response)
    print(f"Agent: {agent_response}")
    print(f"Memory stats: {agent.get_memory_stats()}")
    
    # Turn 4: Query requiring multiple contexts
    print("\n--- Turn 4 ---")
    user_msg = "Recommend weekend activities"
    agent.add_conversation_turn("user", user_msg)
    # Retrieve memories about location and hobbies
    memories = agent.retrieve("activities hiking Seattle weekend", include_trace=True)
    print(f"User: {user_msg}")
    agent_response = (
        "For weekend activities in Seattle, considering your love for hiking, "
        "I'd recommend trails like Mount Si or Discovery Park!"
    )
    agent.add_conversation_turn("assistant", agent_response)
    print(f"Agent: {agent_response}")
    
    # Turn 5: User shares dietary preference
    print("\n--- Turn 5 ---")
    user_msg = "Remember: I'm vegetarian"
    agent.add_conversation_turn("user", user_msg)
    agent.add_fact("User is vegetarian", confidence=1.0, key="diet_vegetarian")
    print(f"User: {user_msg}")
    agent_response = "I've noted that you're vegetarian. I'll keep that in mind!"
    agent.add_conversation_turn("assistant", agent_response)
    print(f"Agent: {agent_response}")
    print(f"Memory stats: {agent.get_memory_stats()}")
    
    # Turn 6: Restaurant recommendation using dietary preference and location
    print("\n--- Turn 6 ---")
    user_msg = "Suggest a restaurant"
    agent.add_conversation_turn("user", user_msg)
    # Retrieve memories about location and dietary preferences
    memories = agent.retrieve("restaurant vegetarian Seattle", include_trace=True)
    print(f"User: {user_msg}")
    agent_response = (
        "For vegetarian options in Seattle, I'd recommend Plum Bistro or Cafe Flora. "
        "Both have excellent plant-based menus!"
    )
    agent.add_conversation_turn("assistant", agent_response)
    print(f"Agent: {agent_response}")
    
    # Turn 7: User asks what agent knows about them
    print("\n--- Turn 7 ---")
    user_msg = "What do you know about me?"
    agent.add_conversation_turn("user", user_msg)
    # Retrieve all facts
    facts = agent.get_all_facts()
    print(f"User: {user_msg}")
    
    print("\nAgent: Here's what I know about you:")
    for fact in facts:
        print(f"  - {fact.content} (confidence: {fact.confidence:.2f})")
    
    agent_response = "I know several things about you based on our conversation."
    agent.add_conversation_turn("assistant", agent_response)
    
    # Show final memory state
    print("\n" + "=" * 70)
    print("Final Memory State")
    print("=" * 70)
    
    stats = agent.get_memory_stats()
    print(f"\nMemory Statistics:")
    print(f"  Short-term: {stats['short_term_count']}/{stats['short_term_max']} items "
          f"({stats['short_term_usage']:.0%} full)")
    print(f"  Long-term: {stats['long_term_count']} facts")
    print(f"  Total: {stats['total_items']} items")
    
    print(f"\nConversation History (last {len(agent.get_conversation_history())} turns):")
    for turn in agent.get_conversation_history()[-6:]:
        role = turn['role'].capitalize()
        content = turn['content'][:80] + "..." if len(turn['content']) > 80 else turn['content']
        print(f"  {role}: {content}")
    
    print(f"\nStored Facts:")
    for fact in facts:
        print(f"  - {fact.content}")
    
    # Demonstrate persistence
    print("\n" + "=" * 70)
    print("Demonstrating Persistence")
    print("=" * 70)
    
    save_path = "labs/04/data/memory_state.json"
    agent.save_to_json(save_path)
    print(f"\nSaved memory state to: {save_path}")
    
    # Load and verify
    loaded_agent = MemoryAgent.load_from_json(save_path)
    loaded_stats = loaded_agent.get_memory_stats()
    print(f"Loaded agent - Short-term: {loaded_stats['short_term_count']}, "
          f"Long-term: {loaded_stats['long_term_count']}")
    print("\nMemory state successfully persisted and restored!")


if __name__ == "__main__":
    run_conversation()
