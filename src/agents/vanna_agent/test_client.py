import logging
import asyncio
from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient, ClientFactory
from a2a.types import (
    AgentCard,
    Message,      # Import Message
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
    TextPart,     # Import TextPart
)
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)

async def main() -> None:
    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    base_url = 'http://localhost:5000'

    async with httpx.AsyncClient(timeout=60.0) as httpx_client:
        # Resolver and card fetching logic remains the same...
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        
        try:
            logger.info(f'Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}')
            final_agent_card_to_use = await resolver.get_agent_card()
            logger.info('Successfully fetched public agent card:')
            logger.info(final_agent_card_to_use.model_dump_json(indent=2, exclude_none=True))

            if final_agent_card_to_use.supports_authenticated_extended_card:
                # (Your extended card logic would go here if needed)
                pass
            else:
                logger.info('\nPublic card does not indicate support for an extended card. Using public card.')

        except Exception as e:
            logger.error(f'Critical error fetching public agent card: {e}', exc_info=True)
            raise RuntimeError('Failed to fetch the public agent card. Cannot continue.') from e

        client = A2AClient(httpx_client=httpx_client, agent_card=final_agent_card_to_use)
        logger.info('A2AClient initialized.')

        # --- FIX IS HERE ---
        # Construct the message using Pydantic models directly
        # instead of a raw dictionary.
        user_message = Message(
            role='user',
            parts=[TextPart(text='get me the average "Value" from historian table')],
            # messageId is often optional, but we can add it if needed
            messageId=uuid4().hex
        )

        send_params = MessageSendParams(message=user_message)
        # --- END OF FIX ---
        
        # Non-streaming request
        logger.info("\n--- Sending Non-Streaming Request ---")
        request = SendMessageRequest(id=str(uuid4()), params=send_params)
        try:
            response = await client.send_message(request)
            print("Response: " + str(response))
            print(response.model_dump(mode='json', exclude_none=True))
        except Exception as e:
            logger.error(f"Error during non-streaming request: {e}", exc_info=True)

        # Streaming request
        # logger.info("\n--- Sending Streaming Request ---")
        # streaming_request = SendStreamingMessageRequest(id=str(uuid4()), params=send_params)
        # try:
        #     stream_response = client.send_message_streaming(streaming_request)
        #     async for chunk in stream_response:
        #         print(chunk.model_dump(mode='json', exclude_none=True))
        # except Exception as e:
        #     logger.error(f"Error during streaming request: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())