import os
from typing import Type, TypeVar, Generic, Any, List, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent, ImageUrl, AudioUrl, DocumentUrl

from src.utils.logging import logger, log_object
from src.services.shared.ai.observability import (
    flush_traces,
    configure_observability,
)

T = TypeVar("T", bound=BaseModel)


configure_observability()


class BaseAgent(Generic[T]):
    """Base class for AI agents with common setup and run logic."""

    def __init__(
        self,
        name: str,
        output_type: Type[T],
        system_prompt: str,
        model_name: str,
        deps: Any = None,
        deps_type: Type = None,
        temperature: float = 0.0,
        tools: List[callable] = None,
    ):
        """Initialize the base agent.

        Args:
            output_type: Expected result type from the agent (Pydantic model)
            system_prompt: System prompt for the agent
            model_name: Name of the language model to use
            provider: LLM provider to use (defaults to environment or Azure)
            deps: Optional dependencies object required by tools/agent
            temperature: Model temperature setting
            tools: Optional list of tools to register with the agent
        """
        self.name = name
        self.model_name = model_name
        self.output_type = output_type
        self.system_prompt = system_prompt
        self.deps = deps
        self.deps_type = deps_type or (type(deps) if deps else None)
        self.temperature = temperature
        self.tools = tools or []

        # Lazy initialization - create agent when first needed
        self._agent = None

    @property
    def agent(self) -> Agent:
        """Lazy-loaded agent instance."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def _create_agent(self) -> Agent:
        """Create the underlying pydantic_ai Agent instance."""
        agent_args = {
            "name": self.name,
            "model": self.model_name,
            "output_type": self.output_type,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "instrument": True,
        }

        if self.deps_type:
            agent_args["deps_type"] = self.deps_type

        agent = Agent(**agent_args)

        # Register tools if provided
        if self.tools:
            for tool in self.tools:
                agent.tool(tool)
        logger.info(f"Agent created: {agent.name}")
        return agent

    def register_tools(self, tools: List[callable]) -> None:
        """Register tools with the underlying pydantic_ai Agent."""
        if not tools:
            return

        for tool in tools:
            self.agent.tool(tool)

    async def run(
        self,
        inputs: Union[
            str,
            List[Union[str, BinaryContent, ImageUrl, AudioUrl, DocumentUrl]],
        ],
        **kwargs: Any,
    ) -> T:
        """
        Run the agent with the given inputs (supports multi-modal).

        Args:
            inputs: The user input(s) - string or list of multi-modal content
            **kwargs: Additional keyword arguments for the agent run

        Returns:
            The Pydantic model instance representing the agent's result
        """
        try:
            run_kwargs = kwargs.copy()
            if self.deps:
                run_kwargs["deps"] = self.deps

            result = await self.agent.run(inputs, **run_kwargs)
            flush_traces()
            log_object(
                title="Agent Result",
                object=result.output,
                subtitle=f"Agent: {self.model_name}",
            )
            return result.output
        except Exception as e:
            logger.error(f"Agent analysis failed: {e}")
            flush_traces()
            raise
