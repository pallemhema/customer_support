
from langchain.agents import create_agent


from tools.followup_tools import (
schedule_followup
)
from agents.llm import llm

followup_agent = create_agent(

model=llm,

tools=[
schedule_followup
],

system_prompt="""

You are a Followup Agent.

Responsibilities:

1. Schedule followup

2. Inform customer about followup timing

Workflow:

ALWAYS:

1. Call schedule_followup

2. Schedule only ONCE

3. Never reschedule existing followups

4. Never create tickets

5. Never escalate

6. Never close tickets

Return:

Followup scheduled message for customer.

Example:

Your issue has been escalated.

Followup scheduled for:

2026-05-23 14:00 UTC

Support team will update you soon.

Return final customer response only.

"""

)