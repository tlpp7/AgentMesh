"""Explicit trace outcome counters; not a semantic evaluation."""
from collections import Counter

def evaluate_trace(trace):
    counts=Counter(event.get('status') for event in trace if isinstance(event,dict))
    passed=counts['ok']+counts['completed']
    failed=counts['error']+counts['failed']
    blocked=counts['blocked']
    total=passed+failed+blocked
    return {'passed':passed,'failed':failed,'blocked':blocked,'total':total,'success_rate':passed/total if total else 0.0}
