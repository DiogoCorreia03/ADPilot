PLAN_PROMPT = """

All created tasks must be relevant to Windows Active Directory and the current phase's objective and scope.


## PLANNING PRINCIPLES

### Evidence-driven planning

Only create tasks supported by evidence.

Evidence sources:
* scan results
* previously discovered findings
* existing task tree
* known credentials
* known hosts
* known access

Do not create speculative attack paths unsupported by evidence.


### Minimal planning

Create only:
* 3-5 high-priority task groups initially

Do not generate a large attack tree.

Expand incrementally as evidence emerges.

## TOOL-AWARE PLANNING

Only plan actions achievable using available tools.

When proposing a task:
* consider tool availability
* prefer low-setup tools
* avoid interactive workflows
* avoid GUI tools
* avoid tools with excessive startup overhead

Prefer only tools explicitly listed in <tools>
Do not assume unavailable tooling exists.




Never delete historical context.


Focus on Windows Active Directory-specific attack paths.
"""