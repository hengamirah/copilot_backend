"""
Simple Vanna A2A Server - Uses only dataAgent.ask()
"""

import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from .agent_executor import (
    VannaAgentExecutor, 
)


if __name__ == "__main__":
    skill = AgentSkill(
        id='vanna_agent',
        name='Vanna SQL Agent',
        description='AI agent that can query SQL databases',
        tags=['sql', 'database', 'query', 'ask'],
        examples=['What is the total sales for the last quarter?', 'Show me the top 5 customers by revenue.'],
    )

    public_agent_card = AgentCard(
        name='Vanna SQL Agent',
        description='AI agent that can query SQL databases',
        url='http://localhost:5000/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],  # Only the basic skill for the public card
        supports_authenticated_extended_card=False,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=VannaAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=5000)

    