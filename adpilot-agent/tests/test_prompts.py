from adpilot_agent.prompts.template import build_plan_prompt, build_update_plan_prompt




def test_build_plan_prompt():
    prompt = build_plan_prompt(
        dc_ip="10.0.0.1",
        network="10.0.0.0/24",
        ignored_hosts="10.0.0.2",
        scan_results="Nmap scan: 445 open",
        tools="Tool 1",
    )
    assert "10.0.0.1" in prompt
    assert "10.0.0.0/24" in prompt
    assert "<scan_results>" in prompt
    assert "Nmap scan: 445 open" in prompt


def test_build_update_plan_prompt():
    prompt = build_update_plan_prompt(
        dc_ip="10.0.0.1",
        network="10.0.0.0/24",
        ignored_hosts="10.0.0.2",
        tools="netexec",
        plan="1. Spray passwords",
        task="1.1 Spray admin",
        task_result="Password found: admin123",
        task_verdict="SUCCESS",
    )
    assert "1. Spray passwords" in prompt
    assert "Password found: admin123" in prompt
    assert "SUCCESS" in prompt
