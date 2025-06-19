"""
Interactive demo script for the content creation pipeline.
"""

import asyncio
from langgraph.checkpoint.memory import MemorySaver
from src.workflow import create_content_workflow, execute_with_interrupts
from src.models import WorkflowState


async def handle_interrupt(app, config):
    """Handle console-based workflow interrupts."""
    current_state = app.get_state(config)
    interrupt_message = current_state.tasks[0].interrupts[0].value
    
    print(f"\n❓ {interrupt_message}")
    user_response = input("\nYour response: ").strip()
    print("\n✅ Continuing workflow...")
    
    return user_response


async def main():
    """Run an interactive demo of the content creation pipeline."""

    print("🚀 Interactive Content Creation Pipeline")
    print("=" * 50)

    user_input = input("\nEnter your brief: ").strip()

    print("\n" + "=" * 50)

    workflow = create_content_workflow()
    memory = MemorySaver()
    app = workflow.compile(
        checkpointer=memory
    )

    initial_state = WorkflowState(
        original_input=user_input, current_step="parse_brief"
    )

    thread_id = "content_session_1"
    config = {"configurable": {"thread_id": thread_id}}

    try:
        print("🚀 Starting content creation workflow...")
        
        await execute_with_interrupts(app, initial_state, config, handle_interrupt)

        print("\n✅ Workflow completed!")

    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
