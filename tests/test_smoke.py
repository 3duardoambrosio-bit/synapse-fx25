from fx25.orchestrator import TaskPacket, orchestrate_task

def test_smoke_runs():
    task = TaskPacket(description="Diseña estrategia de precios dinámica y valida con datos históricos",
                      payload={"csv": "ventas.csv"})
    res = orchestrate_task(task)
    assert res.ok is True
    assert res.task_type in {"design", "hybrid", "data_analysis", "research"}
    assert isinstance(res.output, dict)
