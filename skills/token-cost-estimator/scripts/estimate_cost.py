#!/usr/bin/env python3
"""
Estimate Claude API costs under different optimization strategies:
baseline, prompt caching, Batch API, and combinations.

Pricing must be supplied by the caller (fetched from current Anthropic docs) --
this script does no hardcoding of prices since they change over time.
"""
import argparse
import json


def monthly_requests(requests_per_day: float) -> float:
    return requests_per_day * 30


def baseline_cost(reqs: float, input_tokens: float, output_tokens: float,
                   input_price: float, output_price: float) -> float:
    input_cost = reqs * input_tokens / 1_000_000 * input_price
    output_cost = reqs * output_tokens / 1_000_000 * output_price
    return input_cost + output_cost


def cached_cost(reqs: float, input_tokens: float, output_tokens: float,
                 input_price: float, output_price: float,
                 cached_fraction: float, cache_discount: float,
                 cache_write_premium: float) -> float:
    """
    cached_fraction: fraction of input tokens that come from a reusable cached prefix
    cache_discount: discount applied to cached-read tokens (e.g. 0.9 = 90% off)
    cache_write_premium: extra cost multiplier on first write of the cached segment
    Assumes cache is written once and read on all subsequent requests within the window --
    modeled simply here as: 1 write + (reqs - 1) reads for the cached segment.
    """
    cached_tokens = input_tokens * cached_fraction
    uncached_tokens = input_tokens * (1 - cached_fraction)

    # one cache write (at a premium), rest are discounted reads
    write_cost = cached_tokens / 1_000_000 * input_price * (1 + cache_write_premium)
    read_cost = (reqs - 1) * cached_tokens / 1_000_000 * input_price * (1 - cache_discount)
    uncached_cost = reqs * uncached_tokens / 1_000_000 * input_price
    output_cost = reqs * output_tokens / 1_000_000 * output_price

    return write_cost + read_cost + uncached_cost + output_cost


def batch_cost(reqs: float, input_tokens: float, output_tokens: float,
               input_price: float, output_price: float, batch_discount: float) -> float:
    full = baseline_cost(reqs, input_tokens, output_tokens, input_price, output_price)
    return full * (1 - batch_discount)


def main():
    p = argparse.ArgumentParser(description="Estimate Claude API costs across strategies")
    p.add_argument("--requests-per-day", type=float, required=True)
    p.add_argument("--input-tokens", type=float, required=True, help="avg input tokens per request")
    p.add_argument("--output-tokens", type=float, required=True, help="avg output tokens per request")
    p.add_argument("--input-price-per-mtok", type=float, required=True, help="$ per million input tokens")
    p.add_argument("--output-price-per-mtok", type=float, required=True, help="$ per million output tokens")
    p.add_argument("--cached-fraction", type=float, default=None,
                   help="fraction (0-1) of input tokens that are a reusable cached prefix")
    p.add_argument("--cache-discount", type=float, default=0.9,
                   help="discount on cached reads, default 0.9 (90%% off)")
    p.add_argument("--cache-write-premium", type=float, default=0.25,
                   help="premium multiplier on cache write, default 0.25 (25%% extra)")
    p.add_argument("--batch-discount", type=float, default=0.5,
                   help="Batch API discount, default 0.5 (50%% off)")
    p.add_argument("--json", action="store_true", help="output as JSON instead of text")
    args = p.parse_args()

    reqs = monthly_requests(args.requests_per_day)

    results = {}
    results["baseline_monthly_usd"] = round(baseline_cost(
        reqs, args.input_tokens, args.output_tokens,
        args.input_price_per_mtok, args.output_price_per_mtok), 2)

    if args.cached_fraction is not None:
        results["with_caching_monthly_usd"] = round(cached_cost(
            reqs, args.input_tokens, args.output_tokens,
            args.input_price_per_mtok, args.output_price_per_mtok,
            args.cached_fraction, args.cache_discount, args.cache_write_premium), 2)
        results["caching_savings_pct"] = round(
            100 * (1 - results["with_caching_monthly_usd"] / results["baseline_monthly_usd"]), 1)

    results["with_batch_monthly_usd"] = round(batch_cost(
        reqs, args.input_tokens, args.output_tokens,
        args.input_price_per_mtok, args.output_price_per_mtok, args.batch_discount), 2)
    results["batch_savings_pct"] = round(
        100 * (1 - results["with_batch_monthly_usd"] / results["baseline_monthly_usd"]), 1)

    if args.cached_fraction is not None:
        # combined: apply batch discount on top of the cached estimate
        combined = results["with_caching_monthly_usd"] * (1 - args.batch_discount)
        results["with_caching_and_batch_monthly_usd"] = round(combined, 2)
        results["combined_savings_pct"] = round(
            100 * (1 - combined / results["baseline_monthly_usd"]), 1)

    results["monthly_requests"] = int(reqs)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Monthly requests: {results['monthly_requests']:,}")
        print(f"Baseline cost:            ${results['baseline_monthly_usd']:,.2f}/mo")
        if "with_caching_monthly_usd" in results:
            print(f"With caching:              ${results['with_caching_monthly_usd']:,.2f}/mo "
                  f"({results['caching_savings_pct']}% savings)")
        print(f"With Batch API:            ${results['with_batch_monthly_usd']:,.2f}/mo "
              f"({results['batch_savings_pct']}% savings)")
        if "with_caching_and_batch_monthly_usd" in results:
            print(f"With caching + batch:      ${results['with_caching_and_batch_monthly_usd']:,.2f}/mo "
                  f"({results['combined_savings_pct']}% savings)")


if __name__ == "__main__":
    main()
