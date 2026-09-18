from adpilot_agent.util.state import Phase
from adpilot_agent.prompts.template import build_plan_prompt, build_update_plan_prompt
from adpilot_agent.prompts.specs import get_phase_spec


def test_get_phase_specs_all_phases():
    for phase in Phase:
        spec = get_phase_spec(phase)
        assert spec.phase == phase
        assert len(spec.name) > 0
        assert len(spec.objective) > 0
        assert len(spec.scope) > 0


def test_build_plan_prompt_external_recon():
    prompt = build_plan_prompt(
        phase=Phase.EXTERNAL_RECON,
        dc_ip="10.0.0.1",
        network="10.0.0.0/24",
        ignored_hosts="10.0.0.2",
        scan_results="Nmap scan: 445 open",
        tools="Tool 1",
    )
    assert "External Reconnaissance and Enumeration" in prompt
    assert "10.0.0.1" in prompt
    assert "10.0.0.0/24" in prompt
    assert "<scan_results>" in prompt
    assert "Nmap scan: 445 open" in prompt
    # External recon should not include previous task trees
    assert "<previous_task_trees>" not in prompt


def test_build_plan_prompt_initial_access():
    prompt = build_plan_prompt(
        phase=Phase.INITIAL_ACCESS,
        dc_ip="10.0.0.1",
        network="10.0.0.0/24",
        ignored_hosts="10.0.0.2",
        scan_results="Nmap scan: 445 open",
        tools="Tool 1",
        previous_task_trees="1.1 [DONE] Anonymous SMB",
    )
    assert "Gaining Initial Access" in prompt
    assert "<previous_task_trees>" in prompt
    assert "1.1 [DONE] Anonymous SMB" in prompt
    # Initial access should not include network scan results
    assert "<scan_results>" not in prompt
    assert "Nmap scan: 445 open" not in prompt


def test_build_update_plan_prompt():
    prompt = build_update_plan_prompt(
        phase=Phase.INITIAL_ACCESS,
        dc_ip="10.0.0.1",
        network="10.0.0.0/24",
        ignored_hosts="10.0.0.2",
        tools="netexec",
        plan="1. Spray passwords",
        task="1.1 Spray admin",
        task_result="Password found: admin123",
        task_verdict="SUCCESS",
        previous_task_trees="Phase 1 completed",
    )
    assert "Gaining Initial Access" in prompt
    assert "1. Spray passwords" in prompt
    assert "Password found: admin123" in prompt
    assert "SUCCESS" in prompt
