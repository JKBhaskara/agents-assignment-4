"""
Part 2b: Support Agent (15 points)

Create an ADK Agent that provides customer support solutions and troubleshooting.

This agent should:
  - Use the Gemini model from agents_config
  - Have a detailed instruction covering support scenarios
  - Include the support McpToolset so it can look up customer data and manage tickets

The McpToolset auto-discovers tools from the MCP server. The support toolset uses
tool_filter to exclude admin/destructive operations (disable_customer, delete_ticket,
etc.) so the support agent can only perform safe operations.

Requirements:
  - create_agent() returns a configured google.adk.agents.Agent (5 pts)
  - Agent has a comprehensive instruction with support knowledge base (5 pts)
  - Agent uses create_support_toolset() for data-driven support (5 pts)

The support agent's instruction should include a "knowledge base" covering:
  - Login issues (password resets, account lockouts)
  - Payment issues (failed transactions, billing errors)
  - Performance problems (slow loading, timeouts)
  - Feature requests and suggestions
  - Data export issues

The instruction should also describe:
  - How to handle support queries (analyze, categorize, solve)
  - Response structure (customer context, issue category, solutions, ticket actions)
  - When to create/update tickets
  - Professional and empathetic tone
"""

import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_support_toolset

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [SUPPORT_AGENT] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    """
    Create the Support Agent.

    TODO: Create and return an Agent instance with:
      1. model=GEMINI_MODEL
      2. name='support_agent'
      3. instruction=<your detailed support instruction>
      4. tools=[create_support_toolset()]

    The McpToolset automatically discovers support-safe tools from the MCP
    server. Admin/destructive tools are excluded by the tool_filter.

    Example:
        return Agent(
            model=GEMINI_MODEL,
            name='support_agent',
            instruction=\"\"\"
            You are the Support Agent, a specialist in customer service...

            Your knowledge base includes solutions for:
            - Login issues (password resets, account lockouts)
            - Payment issues (failed transactions, billing errors)
            ...

            When handling support queries:
            1. Use MCP tools to retrieve customer information
            2. Analyze the customer's issue
            ...
            \"\"\",
            tools=[create_support_toolset()],
        )

    Returns:
        Configured Agent instance
    """
    instruction = """
  You are the Support Agent, a customer support specialist focused on diagnosis and resolution.

  Knowledge base and playbooks:
  - Login issues: verify account status, advise password reset flow, handle lockout guidance.
  - Payment and billing issues: identify failed transactions, suggest retrial and billing checks.
  - Performance issues: isolate scope (user-specific vs broad), recommend troubleshooting steps.
  - Feature and usability requests: clarify expected behavior and suggest alternatives.
  - Data export/reporting issues: verify ticket/customer context and provide practical next steps.

  Operating procedure:
  1. Gather context with support-safe MCP tools (customer/ticket lookup, search, stats).
  2. Classify issue category and likely root cause.
  3. Provide step-by-step, actionable guidance in a calm and empathetic tone.
  4. Create or update tickets when needed and report resulting ticket IDs/status.
  5. Escalate clearly when the issue requires admin-only actions outside your tool scope.

  Response format:
  - Summary of customer context
  - Issue assessment
  - Recommended actions
  - Ticket actions taken (if any)
  - Follow-up guidance

  Never invent tool outputs. If a tool call fails or returns no data, say that explicitly and propose a clear next step.
  """.strip()

    return Agent(
        model=GEMINI_MODEL,
        name="support_agent",
        instruction=instruction,
        tools=[create_support_toolset()],
    )
