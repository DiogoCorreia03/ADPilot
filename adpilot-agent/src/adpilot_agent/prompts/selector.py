SELECT_TASK_PROMPT = """

From all the tasks present in the provided task tree, identify those that can be performed next. Most of the time, these should be the ones at the start of the plan that are not marked as done or failed.
Analyze those tasks and decide which one should be performed next based on their likelihood to achieve the objective.
Do NOT create new tasks or modify the task tree in any way. Your only responsibility is to select the next task to be performed.
Include relevant information for the selected task as its context. This includes detailed information such as usernames, credentials, etc. You are allowed to gather this information from throughout the whole task plan. 
Do only include information that is specific to our objective, do not include generic information. Be very concise.

Note down findings and potential leads that might be relevant for future tasks.
Make sure to always include full information, i.e., always include the full hash or token and not abbreviated ones.

You can revise the plan based on new information and failed attempts to execute tasks.
This can help to overcome potential issues with the initial plan and adapt to new information that was not available when the initial plan was created.

Double check that the selected task is not marked as done or failed. If it is, select a different task.
Make sure all information you provide is correct (as far as you know based on the task plan) and do not make assumptions that are not supported by the task plan. If you give information that is not correct, the worker might fail the task and this can lead to a wrong update of the task plan. If you are not sure about the correctness of the information, do not include it in the task context.

Make sure to include all relevant information in the context, including usernames, domain name, credentials, hashes, tokens, etc. that are needed to perform the task.

Return only the one selected task as answer, do not include any other tasks.
If there are no more tasks to be performed, answer with [FINISHED] and do not include any other information.
DO NOT CREATE NEW TASKS OR MODIFY THE TASK TREE IN ANY WAY. Your only responsibility is to select the next task to be performed.
DO NOT SELECT TASKS ALREADY MARKED AS DONE OR FAILED.
Do not include the task plan in your answer, only the selected task with its relevant information and potential leads.
Do not include a title, appendix, explanation why the task was chosen or expected outcomes."""
