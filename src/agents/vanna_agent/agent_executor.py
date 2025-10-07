from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from .vanna import SQLVanna


class VannaAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = SQLVanna()
        self.agent.connect_to_mssql(odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,54180;DATABASE=historian;UID=n8n;PWD=password') 

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        print("Message object " + str(context.message.parts[0].root.text))
        result = self.agent.ask(context.message.parts[0].root.text)
        print("result", result)
        if result is not None:
            # If we got a result, send it
            await event_queue.enqueue_event(new_agent_text_message(str(result)))
        else:
            # If the result is None, get the last generated SQL instead.
            # You might need to expose this from your SQLVanna class.
            last_sql = self.agent.get_sql_prompt() # We will add this method in Step 2
            if last_sql:
                response_text = f"I could not execute the query, but here is the generated SQL:\n```sql\n{last_sql}\n```"
                await event_queue.enqueue_event(new_agent_text_message(response_text))
            else:
                # Fallback if we somehow got no result and no SQL
                response_text = "I was unable to generate a response."
                await event_queue.enqueue_event(new_agent_text_message(response_text))
    
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
