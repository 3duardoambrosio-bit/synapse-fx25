# main.py — launcher FX-25 con overrides
from __future__ import annotations
import argparse, json, sys
from fx25.orchestrator import Orchestrator, orchestrate_task, TaskPacket, ResultEnvelope

def _print(s: str):
    sys.stdout.write(s + ("\n" if not s.endswith("\n") else "")); sys.stdout.flush()

def build_args():
    p = argparse.ArgumentParser(description="FX-25 runner")
    p.add_argument("--task-id", required=True)
    p.add_argument("--mode", choices=["fallback", "trinity"], default="fallback")
    p.add_argument("--topic", required=True)
    # Overrides Trinity
    p.add_argument("--qa", type=int, default=None)
    p.add_argument("--topk", type=int, default=None)
    p.add_argument("--batch", type=int, default=None)
    p.add_argument("--rounds", type=int, default=None)
    # Comunes
    p.add_argument("--temp", type=float, default=None)
    p.add_argument("--max-tokens", type=int, default=None)
    return p.parse_args()

def run_fallback(orch: Orchestrator, args) -> ResultEnvelope:
    pkt = TaskPacket(
        task_id=args.task_id, prompt=args.topic, task_type="research",
        temperature=args.temp if args.temp is not None else 0.2,
        max_tokens=args.max_tokens if args.max_tokens is not None else 1200,
        metadata={"mode": "fallback"},
    )
    return orchestrate_task(pkt)

def run_trinity(orch: Orchestrator, args) -> ResultEnvelope:
    pkt = TaskPacket(
        task_id=args.task_id, prompt=args.topic, task_type="research",
        temperature=args.temp if args.temp is not None else 0.2,
        max_tokens=args.max_tokens if args.max_tokens is not None else 1200,
        metadata={"mode": "trinity"},
    )
    cfg = Orchestrator.TrinityConfig()
    if args.qa is not None:     cfg.qa_per_role = int(args.qa)
    if args.topk is not None:   cfg.top_k = int(args.topk)
    if args.batch is not None:  cfg.batch_size = int(args.batch)
    if args.rounds is not None: cfg.rounds = int(args.rounds)
    return orch.orchestrate_trinity(pkt, cfg)

def main() -> int:
    args = build_args()
    orch = Orchestrator()
    try:
        env = run_trinity(orch, args) if args.mode == "trinity" else run_fallback(orch, args)
        if env.ok and env.output_text:
            _print(env.output_text)
        else:
            _print(json.dumps({"ok": False, "error": env.error, "connector": env.connector,
                               "status_code": env.status_code}, ensure_ascii=False, indent=2))
        _print("\n[FX25] Artefactos y logs guardados en la carpeta 'outputs/'.")
        return 0
    except Exception as e:
        _print(f"[FX25] Error en ejecución: {e}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
