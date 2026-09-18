from adpilot_agent.util.state import CheckVerdict
from adpilot_agent.util.nodes import _parse_check_verdict


def test_parse_verdict_explicit_standard():
    assert _parse_check_verdict("VERDICT: [SUCCESS]") == CheckVerdict.SUCCESS
    assert _parse_check_verdict("VERDICT: [RETRY]") == CheckVerdict.RETRY
    assert _parse_check_verdict("VERDICT: [FAILURE]") == CheckVerdict.FAILURE


def test_parse_verdict_case_insensitive():
    assert _parse_check_verdict("verdict: [success]\nREASON: worked") == CheckVerdict.SUCCESS
    assert _parse_check_verdict("Verdict: [retry]\nREASON: syntax error") == CheckVerdict.RETRY
    assert _parse_check_verdict("VERDICT: [failure]\nREASON: dead end") == CheckVerdict.FAILURE


def test_parse_verdict_fallback():
    assert _parse_check_verdict("The execution was a success overall.") == CheckVerdict.SUCCESS


def test_parse_verdict_failure_precedence_over_success():
    # If the response mentions both success and failure, failure should take precedence
    assert _parse_check_verdict("The execution was not a success; task failed with authentication error.") == CheckVerdict.FAILURE


def test_parse_verdict_retry_precedence_over_success():
    assert _parse_check_verdict("No success yet, please retry with valid flags.") == CheckVerdict.RETRY
