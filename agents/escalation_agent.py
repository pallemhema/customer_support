from langchain.agents import (
create_agent
)



from tools.escalation.refund_escalation import (
handle_refund
)

from tools.escalation.delivery_escalation import (
handle_delivery
)

from tools.escalation.payment_escalation import (
handle_payment
)

from tools.escalation.account_escalation import (
handle_account
)
from agents.llm import llm





system_prompt = """

You are an Escalation Agent.

Your work:

1. Detect escalation type

2. Select proper escalation tool

3. Create tickets

4. Request customer approval if needed

5. Escalate to humans

6. Assign teams


Available escalation types:

refund_issue

delivery_issue

payment_issue

account_issue


Rules:

refund_issue

Use refund escalation.


delivery_issue

Use delivery escalation.


payment_issue

Use payment escalation.


account_issue

Use account escalation.


Never answer policies.

Never retrieve knowledge.

Never perform tracking.

Never close tickets.

Return escalation result only.

"""


escalation_agent = create_agent(

model=llm,

tools=[

handle_refund,

handle_delivery,

handle_payment,

handle_account

],


system_prompt=system_prompt

)