import pytest

from lucy.cli import utils
from ._helpers import fake_agent_result


@pytest.fixture(autouse=True)
def fixed_prices(monkeypatch):
    monkeypatch.setattr(utils, "MODEL_INPUT_COST_PM", 1.0)
    monkeypatch.setattr(utils, "MODEL_CACHE_COST_PM", 0.1)
    monkeypatch.setattr(utils, "MODEL_OUTPUT_COST_PM", 10.0)
    monkeypatch.setattr(utils, "MODEL_CONTEXT_WINDOW", 100_000)


def test_usage_comes_from_latest_invocation_not_lifetime_totals():
    response = fake_agent_result(usage={"inputTokens": 1_000, "outputTokens": 100, "totalTokens": 1_100})

    usage = utils.compute_usage_metrics(response)

    assert usage.input_tokens == 1_000
    assert usage.output_tokens == 100
    assert usage.total_tokens == 1_100


def test_cached_input_tokens_are_billed_once_at_cache_rate():
    response = fake_agent_result(
        usage={"inputTokens": 1_000_000, "outputTokens": 0, "totalTokens": 1_000_000, "cacheReadInputTokens": 400_000}
    )

    usage = utils.compute_usage_metrics(response)

    # 600k uncached at $1/M + 400k cached at $0.10/M
    assert usage.cost_usd == pytest.approx(0.64)
    assert usage.cached_input_tokens == 400_000


def test_context_used_is_a_percentage_of_the_window():
    response = fake_agent_result(context_size=25_000)

    assert utils.compute_usage_metrics(response).context_used_pct == 25.0


def test_missing_invocation_and_context_yield_zero_usage():
    response = fake_agent_result()
    response.metrics.latest_agent_invocation = None
    response.metrics.latest_context_size = None

    usage = utils.compute_usage_metrics(response)

    assert usage.input_tokens == 0
    assert usage.cost_usd == 0
    assert usage.context_used_pct == 0
