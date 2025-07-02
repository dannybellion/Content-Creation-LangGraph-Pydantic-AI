"""
Content creation pipeline runner with interactive demo functionality.
"""

from langgraph.checkpoint.memory import MemorySaver
from src.graph.builder import create_content_workflow, execute_with_interrupts
from src.graph.state import WorkflowState
from src.utils.logging import logger


class ContentPipelineRunner:
    """Runner for the interactive content creation pipeline."""

    def __init__(self):
        self.workflow = create_content_workflow()
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    async def handle_interrupt(self, app, config):
        """Handle console-based workflow interrupts."""
        current_state = app.get_state(config)
        interrupt_message = current_state.tasks[0].interrupts[0].value

        print(f"\n❓ {interrupt_message}")
        user_response = input("\nYour response: ").strip()
        logger.info("Continuing workflow with user response")
        print("\n✅ Continuing workflow...")

        return user_response

    async def run(self):
        """Run the interactive content creation pipeline."""
        print("🚀 Interactive Content Creation Pipeline")
        print("=" * 50)

        user_input = input("\nEnter your brief: ").strip()
        print("\n" + "=" * 50)

        initial_state = WorkflowState(
            original_input=user_input, current_step="parse_brief"
        )

        thread_id = "content_session_1"
        config = {"configurable": {"thread_id": thread_id}}

        try:
            logger.info("Starting content creation workflow")
            print("🚀 Starting content creation workflow...")

            await execute_with_interrupts(
                self.app, initial_state, config, self.handle_interrupt
            )

            logger.info("Workflow completed successfully")
            print("\n✅ Workflow completed!")

        except Exception as e:
            logger.error(f"Error running pipeline: {e}")
            print(f"\n❌ Error running pipeline: {e}")
            import traceback

            traceback.print_exc()
