# Content Creation Pipeline using LangGraph and Pydantic AI

I watched this Greg Isenberg video on effective writing: https://www.youtube.com/watch?v=om-etwwp3Wg&t=6s which inspired me to create a multi-agent workflow to replicate this process.

## Overview

This project implements an automated content creation pipeline that mimics effective human writing processes. The system uses multiple AI agents working in coordination to research, analyze, and generate high-quality content based on trending topics and real-time web data.


## Technical Implementation

### Architecture

The system is built around a modular architecture with clear separation of concerns:

- **State Management**: Centralized workflow state using LangGraph's state management
- **Agent System**: Pydantic AI agents with structured outputs and validation
- **Workflow Orchestration**: LangGraph manages the pipeline with interrupt handling
- **Research Tools**: Integrated web search and YouTube analysis capabilities
- **Prompt Management**: Template-based prompting with Jinja2


### Agents

- **Brief Parser** (`brief_parser.py`): Converts free text to structured briefs
- **Brief Validator** (`brief_validator.py`): Validates brief completeness
- **Headline Generator** (`headline_generator.py`): Creates compelling headlines
- **Researcher** (`researcher.py`): Conducts comprehensive research
- **Content Writer** (`content_writer.py`): Generates initial content drafts
- **Content Editor** (`content_editor.py`): Refines content based on feedback

## Project Structure

```
├── src/
│   ├── agents/                 # AI agents for different pipeline stages
│   │   ├── base.py            # Base agent class with Pydantic AI integration
│   │   ├── brief_parser.py    # Brief parsing agent
│   │   ├── brief_validator.py # Brief validation agent
│   │   ├── headline_generator.py # Headline generation agent
│   │   ├── researcher.py      # Research agent
│   │   ├── content_writer.py  # Content writing agent
│   │   └── content_editor.py  # Content editing agent
│   ├── graph/                 # LangGraph workflow management
│   │   ├── builder.py         # Workflow graph construction
│   │   ├── nodes.py           # Individual workflow nodes
│   │   └── state.py           # Workflow state management
│   ├── models/                # Pydantic data models
│   │   ├── agent_outputs.py   # Agent output models
│   │   └── domain.py          # Core domain models
│   ├── prompts/               # Prompt templates and management
│   │   ├── prompt_manager.py  # Template rendering and management
│   │   └── templates/         # Jinja2 template files
│   ├── tools/                 # Research and analysis tools
│   │   ├── web_search.py      # Web search capabilities
│   │   ├── youtube_search.py  # YouTube content analysis
│   │   ├── content_analysis.py # Content quality analysis
│   │   └── style_guidelines.py # Writing style guidelines
│   ├── utils/                 # Utility functions
│   │   ├── logging.py         # Structured logging
│   │   ├── observability.py   # Tracing and monitoring
│   │   └── utils.py           # Common utilities
│   ├── config.py              # Configuration management
│   └── runner.py              # Pipeline execution runner
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests for agents and components
│   └── integration/           # Integration tests
├── main.py                    # Interactive demo application
├── validate_config.py         # Configuration validation script
├── pyproject.toml            # Project dependencies and configuration
├── CLAUDE.md                 # AI assistant instructions
└── README.md                 # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd content-creation-pipeline
   ```

2. **Install dependencies using uv**
   ```bash
   uv sync
   ```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_key_here

# Observability (optional)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key  
LANGFUSE_HOST=https://cloud.langfuse.com

# External APIs
APIFY_API_KEY=your_apify_key_for_youtube_search
SERP_API_KEY=your_serp_api_key_for_web_search
```

## Usage

```bash
uv run -m main
```

## Dependencies

- **Python**: >=3.11
- **Core Frameworks**: LangGraph, Pydantic AI
- **AI/ML**: OpenAI API integration
- **Research**: Apify (YouTube), SERP API (web search)
- **Templates**: Jinja2
- **Observability**: Langfuse (optional)
- **Development**: Ruff (formatting/linting), pytest (testing)