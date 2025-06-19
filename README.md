# Content Creation Pipeline using LangGraph and Pydantic AI

I watched this Greg Isenberg video on effective writing: https://www.youtube.com/watch?v=om-etwwp3Wg&t=6s which inspired me to create a multi-agent workflow to replicate this process.

## Overview

This project implements an automated content creation pipeline that mimics effective human writing processes. The system uses multiple AI agents working in coordination to research, analyze, and generate high-quality content based on trending topics and real-time web data.

### Key Features

- **Multi-agent workflow**: Specialized agents for research, analysis, and content generation
- **Real-time web research**: Integration with Apify for up-to-date information gathering
- **Structured data handling**: Pydantic AI ensures type-safe agent interactions
- **Orchestrated pipeline**: LangGraph manages the complex workflow between agents
- **Quality control**: Built-in review and refinement processes

## Technical Implementation

### LangGraph Orchestration

LangGraph is used to orchestrate the workflow, managing the complex interactions between different agents and ensuring proper data flow throughout the pipeline. The workflow includes:

- **Research Agent**: Identifies trending topics and gathers initial research
- **Data Collection Agent**: Uses Apify to search for relevant, up-to-date information
- **Analysis Agent**: Processes and synthesizes the collected information
- **Content Generation Agent**: Creates engaging, well-structured content
- **Review Agent**: Performs quality checks and suggests improvements

### Pydantic AI Agents

Pydantic AI is used for the individual agents, providing:

- **Type Safety**: Ensures data consistency between agent interactions
- **Structured Outputs**: Guarantees properly formatted responses from each agent
- **Validation**: Automatic validation of agent inputs and outputs
- **Error Handling**: Robust error handling with clear feedback
- **Modular Design**: Easy to extend and modify individual agents

### Apify & Tavily Integrations

- **Apify** is used to get relevant youtube videos and transcripts.
- **Tavily** is used to get relevant web pages.


## Project Structure

```
├── agents/
│   ├── research_agent.py
│   ├── data_collection_agent.py
│   ├── analysis_agent.py
│   ├── content_generation_agent.py
│   └── review_agent.py
├── workflows/
│   ├── content_pipeline.py
│   └── workflow_states.py
├── models/
│   ├── content_models.py
│   └── research_models.py
├── integrations/
│   ├── apify_client.py
│   └── web_search.py
├── config/
│   ├── settings.py
│   └── prompts/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```


## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd content-creation-pipeline
   ```

2. **Create and activate virtual environment**
   ```bash
   uv sync
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key
   # TAVILY_API_KEY=your_tavily_key
   # APIFY_API_KEY=your_apify_key
   ```