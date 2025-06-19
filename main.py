"""
Interactive demo script for the content creation pipeline.
"""

import asyncio
from langgraph.checkpoint.memory import MemorySaver
from src.workflow import create_content_workflow, print_workflow_summary
from src.models import WorkflowState


async def main():
    """Run an interactive demo of the content creation pipeline."""

    print("🚀 Interactive Content Creation Pipeline")
    print("=" * 50)

    # Get user input
    # user_input = input("\nEnter your brief: ").strip()
    user_input = (
        "linkedin post of using pydantic ai to build agents in production"
    )

    print("\n" + "=" * 50)

    # Create workflow and compile app
    workflow = create_content_workflow()
    memory = MemorySaver()
    app = workflow.compile(
        checkpointer=memory
    )  # Enable checkpointing for interrupts

    # Initialize state
    initial_state = WorkflowState(
        original_input=user_input, current_step="parse_brief"
    )

    # Thread configuration for this session
    thread_id = "content_session_1"
    config = {"configurable": {"thread_id": thread_id}}

    try:
        print("🚀 Starting content creation workflow...")

        # Run workflow - it will automatically pause at interrupt points
        async for event in app.astream(initial_state, config):
            event_name = list(event.keys())[0]
            print(f"📍 Event: {event_name}")

            # Check if we hit an interrupt
            if event_name == "__interrupt__":
                # Get the interrupt message
                current_state = app.get_state(config)
                interrupt_message = current_state.tasks[0].interrupts[0].value

                print(f"\n❓ {interrupt_message}")
                user_response = input("\nYour response: ").strip()

                print("\n✅ Continuing workflow...")

                # Resume with user response
                from langgraph.types import Command

                async for resume_event in app.astream(
                    Command(resume=user_response), config
                ):
                    resume_event_name = list(resume_event.keys())[0]
                    if resume_event_name != "__interrupt__":
                        print(f"📍 Event: {resume_event_name}")

                    # Handle nested interrupts (like content review)
                    if resume_event_name == "__interrupt__":
                        nested_state = app.get_state(config)
                        nested_message = (
                            nested_state.tasks[0].interrupts[0].value
                        )

                        print(f"\n❓ {nested_message}")
                        nested_response = input("\nYour response: ").strip()

                        # Resume nested interrupt
                        async for final_event in app.astream(
                            Command(resume=nested_response), config
                        ):
                            final_event_name = list(final_event.keys())[0]
                            print(f"📍 Event: {final_event_name}")

        # Get final state
        final_state = app.get_state(config)

        print("\n✅ Workflow completed!")

        if final_state.values:
            # Convert dict to WorkflowState for summary
            workflow_state = WorkflowState(**final_state.values)
            print_workflow_summary(workflow_state)

    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
