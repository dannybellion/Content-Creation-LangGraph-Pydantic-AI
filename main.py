import asyncio
from src.runner import ContentPipelineRunner


async def main():
    """Run an interactive demo of the content creation pipeline."""
    runner = ContentPipelineRunner()
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())