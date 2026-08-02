from strands.agent import AgentResult

from lucy.session.models import UsageMetrics
from lucy.config import (
    MODEL_CACHE_COST_PM, 
    MODEL_CONTEXT_WINDOW, 
    MODEL_INPUT_COST_PM, 
    MODEL_OUTPUT_COST_PM
)


def compute_usage_metrics(response: AgentResult):
    usage = response.message["metadata"]["usage"]
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    total_tokens = usage.get("totalTokens")
    cache_read = usage.get("cacheReadInputTokens", 0) 
    cache_write = usage.get("cacheWriteInputTokens", 0)
    input_cost = MODEL_INPUT_COST_PM * input_tokens / 1_000_000
    output_cost = MODEL_OUTPUT_COST_PM * output_tokens / 1_000_000
    cache_cost = MODEL_CACHE_COST_PM * (cache_read + cache_write) / 1_000_000
    context_used_pct = round(response.metrics.latest_context_size / MODEL_CONTEXT_WINDOW, 4)
    cost_usd = round(input_cost + output_cost + cache_cost, 4)
    return UsageMetrics(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cached_input_tokens=cache_read,
        cached_output_tokens=cache_write,
        context_used_pct=context_used_pct,
        cost_usd=cost_usd
    )


def compute_accumulated_metrics(response: AgentResult):
    usage = response.metrics.accumulated_usage
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    total_tokens = usage.get("totalTokens", 0)
    cache_read = usage.get("cacheReadInputTokens", 0)
    cache_write = usage.get("cacheWriteInputTokens", 0)
    input_cost = MODEL_INPUT_COST_PM * input_tokens / 1_000_000
    output_cost = MODEL_OUTPUT_COST_PM * output_tokens / 1_000_000
    cache_cost = MODEL_CACHE_COST_PM * (cache_read + cache_write) / 1_000_000
    context_used_pct = round((input_tokens + cache_read) / MODEL_CONTEXT_WINDOW, 2)
    cost_usd = round(input_cost + output_cost + cache_cost, 4)
    return UsageMetrics(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cache_read,
        cached_output_tokens=cache_write,
        context_used=context_used_pct,
        cost_usd=cost_usd
    )