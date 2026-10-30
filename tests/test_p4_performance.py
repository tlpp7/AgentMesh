import pytest
from agentmesh.performance import BenchmarkConfig,benchmark,compare,percentile

def test_percentile():
    assert percentile([4,1,2,3],50)==2.5
    with pytest.raises(ValueError):percentile([],50)

def test_parallel_load():
    result=benchmark(BenchmarkConfig(agents=6,concurrency=3,delay_ms=1,runs=2))
    metrics=result["metrics"]
    assert metrics["run_success_rate"]==1
    assert metrics["completed_rate"]==1
    assert metrics["p95_ms"]>=metrics["p50_ms"]>0

def test_failure_propagation():
    result=benchmark(BenchmarkConfig(agents=4,concurrency=2,delay_ms=0,runs=1,failure_every=2,graph="chain"))
    metrics=result["metrics"]
    assert metrics["run_success_rate"]==0
    assert metrics["node_failure_rate"]==pytest.approx(.25)
    assert metrics["blocked_rate"]==pytest.approx(.5)

def test_invalid_load():
    with pytest.raises(ValueError):BenchmarkConfig(agents=501)
    with pytest.raises(ValueError):BenchmarkConfig(graph="unknown")

def test_compare():
    baseline={"workload":{"agents":3},"metrics":{"p95_ms":100}}
    current={"workload":{"agents":3},"metrics":{"p95_ms":130}}
    assert compare(current,baseline)["regression"]
    current["workload"]={"agents":4}
    with pytest.raises(ValueError):compare(current,baseline)
