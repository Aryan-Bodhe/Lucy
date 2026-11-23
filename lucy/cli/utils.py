from strands.agent import AgentResult

from lucy.session.models import UsageMetrics
from lucy.config import (
    MODEL_CACHE_COST_PM,
    MODEL_CONTEXT_WINDOW,
    MODEL_INPUT_COST_PM,
    MODEL_OUTPUT_COST_PM
)


def compute_usage_metrics(response: AgentResult) -> UsageMetrics:
    """Usage for the request that produced `response` (one turn), not a running total.

    Strands' `metrics.accumulated_usage` spans every call on the cached agent, so it
    must not be used here: callers add these per-turn values into session totals.
    A turn can span several model calls (tool use), so the invocation's usage is
    used instead of the final message's metadata, which covers only the last call.
    """
    invocation = response.metrics.latest_agent_invocation
    usage = invocation.usage if invocation else {}

    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    total_tokens = usage.get("totalTokens", input_tokens + output_tokens)
    cache_read = usage.get("cacheReadInputTokens", 0)
    cache_write = usage.get("cacheWriteInputTokens", 0)

    # OpenAI reports cached tokens as a subset of input tokens; bill them once,
    # at the cache rate.
    uncached_input = max(input_tokens - cache_read, 0)
    input_cost = MODEL_INPUT_COST_PM * uncached_input / 1_000_000
    cache_cost = MODEL_CACHE_COST_PM * cache_read / 1_000_000
    output_cost = MODEL_OUTPUT_COST_PM * output_tokens / 1_000_000

    context_size = response.metrics.latest_context_size or 0
    context_used_pct = round(100 * context_size / MODEL_CONTEXT_WINDOW, 2)

    return UsageMetrics(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cached_input_tokens=cache_read,
        cached_output_tokens=cache_write,
        context_used_pct=context_used_pct,
        cost_usd=round(input_cost + cache_cost + output_cost, 6),
    )
