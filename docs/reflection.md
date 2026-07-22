# Assignment 4: Reflection

## Student Name: Jagadeesh Bhaskara

---

## Part 1: MCP Tools + Customer Data Agent

### Tool Design Decisions
- I configured two MCP toolsets using ADK McpToolset over SSE.
- Customer data toolset includes all 15 tools because that agent is responsible for full record lifecycle (read, create, update, admin actions, stats, and search).
- Support toolset includes only support-safe tools and intentionally excludes admin/destructive actions: disable_customer, activate_customer, delete_ticket, add_customer, update_customer.
- Tool signatures remained MCP-native (provided by FastMCP). ADK compatibility came from using SseConnectionParams and tool_filter with valid tool names, so no custom wrappers were needed.

### Data Agent Instruction
- The instruction defines the agent as a data specialist for customers and tickets, with responsibilities for lookup, management, stats, and precise reporting.
- It includes an explicit operating workflow: parse request, call authoritative MCP tools, confirm changes with IDs/status values, ask for missing parameters, and handle tool failures gracefully.
- The instruction guides tool usage by mapping intent to action (fetch before answering, update then confirm), and by requiring no fabricated data.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- The support instruction includes playbooks for login issues, password resets, billing/payment failures, performance incidents, feature requests, and data export issues.
- It enforces an empathetic, structured response format: context summary, issue assessment, recommended actions, ticket actions, and follow-up.
- For queries that can be answered from the built-in playbook, it can provide general troubleshooting steps without tools.
- For account-specific or ticket-specific issues, it uses support-safe MCP tools and clearly states when admin-only operations require escalation.

### Host Agent Orchestration
- The host agent is a SequentialAgent with two RemoteA2aAgent sub-agents: customer_data first, support_specialist second.
- This ordering makes data retrieval happen before support reasoning.
- The second step receives prior conversational context, so support guidance can reference fetched records, statuses, and ticket history.
- If data is missing or ambiguous, the support agent falls back to safe next-step guidance and follow-up questions.

### A2A Protocol Insights
- Discovery happens by fetching each agent's AgentCard from its known URL and reading capabilities, skills, transport preference, and metadata.
- The `.well-known/agent-card.json` endpoint is the standard discovery contract used by clients and remote agents to resolve how to connect.
- RemoteA2aAgent wraps networked agent-to-agent communication (JSON-RPC/A2A), preserving protocol boundaries and loose coupling.
- Direct function calls are tighter-coupled and bypass service boundaries, transport negotiation, and protocol-level metadata.

---

## Part 3: Challenges and Solutions

### Technical Challenges
- The hardest part was version compatibility across google-adk and a2a-sdk APIs.
- I encountered import and API drift issues (for example, helper names and class-export differences) and resolved them by pinning assignment-compatible versions and adding compatibility imports.
- A major runtime issue occurred in ADK Web when `host_agent` loaded through system Python instead of the project environment, causing missing symbols like `ClientEvent` and `A2AClientHTTPError`.
- I fixed this by ensuring compatibility patches run before `RemoteA2aAgent` imports and by aligning the active interpreter packages to `google-adk==1.9.0` and `a2a-sdk==0.3.0`.
- Debugging strategy:
	- Run unit checks incrementally (`test_mcp_toolset`, `test_agents`, `test_a2a`).
	- Reproduce stack traces from `run_agents.py --mode start`.
	- Compare system vs virtual environment executable paths and package exports.
	- Validate constructor signatures and context object fields in the installed runtime.
	- Patch compatibility points instead of changing provided architecture.

### Architecture Decisions
- Sequential orchestration is appropriate because support quality improves when recommendations are grounded in fresh customer/ticket data.
- It enforces deterministic ordering (data first, guidance second), which is easier to reason about and debug.
- Compared with direct agent calls, SequentialAgent plus A2A improves modularity and service independence.
- Trade-offs include added network overhead, more moving parts, and higher sensitivity to protocol version mismatches.

---

## Bonus: Routing Modes (if attempted)

### Advanced Router
- The advanced router analyzes query intent using keyword signals for data needs, support needs, and urgency.
- It produces a routing decision (`needs_data`, `needs_support`, `urgency`, `execution_mode`) and uses before-agent callbacks to conditionally skip unnecessary sub-agents.
- Callback pattern used:
	- `before_agent_callback` on each RemoteA2aAgent.
	- If routing indicates the step is not needed, callback returns a skip Content.
	- If missing, callbacks infer and persist routing state from user content.

### Parallel Router
- Parallel mode runs both remote specialists concurrently via ParallelAgent, reducing wall-clock time when both are needed.
- A synthesis agent then combines outputs into one cohesive response with a clear summary, data findings, support actions, and next steps.
- In this runtime, RemoteA2aAgent did not accept `output_key`, so state handoff was implemented with after-agent callbacks that guarantee summary keys exist.

### Mode Comparison

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | Always customer_data then support_specialist | Medium | Natural step-by-step context chain |
| Advanced (Dynamic) | Conditional: data only, support only, or both | Low to Medium (query dependent) | Routing decision in shared state + sequential context |
| Parallel | Usually both at once + summary agent | Lowest when both specialists are needed | Parallel results synthesized into a unified final response |

---

## Key Learnings
1. Protocol-driven multi-agent design is robust when discovery contracts (AgentCards) and transport boundaries are respected.
2. Prompt/instruction quality directly affects tool use reliability, error behavior, and output structure.
3. Version pinning and compatibility shims are essential in fast-moving ADK/A2A stacks.
4. Import order matters for compatibility layers; patches must execute before dependent module imports.

## Ideas for Improvement
- Add richer routing features (confidence scoring, fallback policies, and intent classifier tests).
- Improve observability with structured tracing for inter-agent hops and per-step latency metrics.
- Add one-click launcher scripts that force the correct interpreter to avoid environment drift.
