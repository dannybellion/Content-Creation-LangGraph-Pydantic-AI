"""
Test the graph workflow routing to ensure proper flow control.
"""

from src.graph.builder import create_content_workflow, process_human_feedback
from src.graph.state import WorkflowState, HumanFeedback


def test_workflow_has_proper_routing():
    """Test that workflow compiles and has expected nodes."""
    workflow = create_content_workflow()

    expected_nodes = [
        "parse_brief",
        "validate_brief",
        "enhance_brief",
        "conduct_research",
        "generate_headlines",
        "select_headline",
        "make_editorial_decisions",
        "write_content",
        "human_review",
    ]

    for node in expected_nodes:
        assert node in workflow.nodes


def test_human_feedback_routing_approve():
    """Test human feedback routes correctly when approved."""
    state = WorkflowState(
        original_input="test",
        human_feedback=HumanFeedback(
            feedback_type="approve",
            comments="Looks good!",
            requested_changes=[],
            priority="low",
            preserve_elements=[],
        ),
    )

    result = process_human_feedback(state)
    assert result == "finalize"


def test_human_feedback_routing_edit():
    """Test human feedback routes correctly for content edits."""
    state = WorkflowState(
        original_input="test",
        revision_count=1,
        human_feedback=HumanFeedback(
            feedback_type="edit_content",
            comments="Needs improvement",
            requested_changes=["Add more examples"],
            priority="high",
            preserve_elements=[],
        ),
    )

    result = process_human_feedback(state)
    assert result == "write_content"


def test_human_feedback_routing_revision_limit():
    """Test revision limit prevents infinite loops."""
    state = WorkflowState(
        original_input="test",
        revision_count=3,
        human_feedback=HumanFeedback(
            feedback_type="edit_content",
            comments="Still needs changes",
            requested_changes=["More changes"],
            priority="high",
            preserve_elements=[],
        ),
    )

    result = process_human_feedback(state)
    assert result == "finalize"


def test_workflow_compilation():
    """Test that workflow compiles without errors after routing fix."""
    workflow = create_content_workflow()

    compiled_app = workflow.compile()
    assert compiled_app is not None
