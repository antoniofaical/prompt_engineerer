import json
from pathlib import Path

from .config import UserConfig
from .errors import AppError
from .files import RESOURCES, atomic_output, read_seed, run_lock
from .schemas import Analysis, Draft, Review, Selection
from .target import resolve_target
from .technical import MAX_ANSWER_CHARS, MAX_QUESTIONS_PER_ROUND


def load_catalog() -> list[dict]:
    catalog = json.loads((RESOURCES / "guidelines.json").read_text(encoding="utf-8"))
    rules = catalog["rules"]
    if len({r["id"] for r in rules}) != len(rules):
        raise AppError("Catálogo contém IDs duplicados.")
    return rules


def optimize(root: Path, config: UserConfig, provider, ui) -> str:
    with run_lock(root):
        seed = read_seed(root)
        target = resolve_target(config.target_ai, config.max_clarification_rounds > 0, ui)
        context = {
            "seed": seed,
            "settings": config.model_dump(exclude={"api_key_env_var", "target_ai"}),
            "target_ai": target.model_dump(),
            "answers": [],
        }
        ui.say("[CONTEXTO] O seed e as respostas serão enviados ao provedor gerador.")
        analysis = provider.call("Interpretar demanda", context, Analysis)
        for round_number in range(config.max_clarification_rounds):
            if not analysis.questions:
                break
            if round_number == 0:
                ui.say(
                    "[PERGUNTAS] Enter pula uma pergunta; /fim encerra os esclarecimentos; "
                    "Ctrl+C cancela."
                )
            stop = False
            answered = False
            # Ask blocking questions first, without silently dropping any unresolved conflict.
            questions = sorted(analysis.questions, key=lambda q: not q.blocking)[
                :MAX_QUESTIONS_PER_ROUND
            ]
            for question_number, question in enumerate(questions, start=1):
                answer = ui.ask(
                    question.text,
                    reason=question.reason,
                    title=(
                        f"Rodada {round_number + 1}/{config.max_clarification_rounds} · "
                        f"Pergunta {question_number}/{len(questions)}"
                    ),
                )
                if answer.casefold() == "/fim":
                    stop = True
                    break
                if len(answer) > MAX_ANSWER_CHARS:
                    raise AppError(f"Resposta excede {MAX_ANSWER_CHARS} caracteres.")
                context["answers"].append({"question": question.text, "answer": answer or None})
                answered = answered or bool(answer)
            if answered:
                analysis = provider.call("Interpretar demanda", context, Analysis)
            if stop or not answered:
                break
        if analysis.blocking_conflicts or any(q.blocking for q in analysis.questions):
            ui.say("[CONFLITO] " + "; ".join(analysis.blocking_conflicts))
            raise AppError(
                "Há contradições impeditivas sem resolução. Corrija o seed/configuração "
                "e execute novamente. O resultado anterior foi preservado."
            )
        if analysis.missing_information:
            ui.say("[AVISO] Lacunas restantes serão tratadas sem inventar informações.")
        context["analysis"] = analysis.model_dump()
        catalog = [
            r for r in load_catalog() if not r.get("providers") or target.provider in r["providers"]
        ]
        selection = provider.call(
            "Selecionar guidelines", {**context, "catalog": catalog}, Selection
        )
        known = {r["id"] for r in catalog}
        if set(selection.guideline_ids) - known:
            raise AppError("A seleção retornou IDs de guidelines desconhecidos ou incompatíveis.")
        selected = set(selection.guideline_ids) | {r["id"] for r in catalog if r["always"]}
        context["guidelines"] = [r for r in catalog if r["id"] in selected]
        ui.say("[GUIDELINES] " + ", ".join(sorted(selected)))
        draft = provider.call("Gerar prompt", context, Draft)
        for revision in range(config.max_revision_rounds + 1):
            review = provider.call("Revisar prompt", {**context, "draft": draft.markdown}, Review)
            blocking = [issue for issue in review.issues if issue.severity == "blocking"]
            if review.passed and not blocking:
                for issue in review.issues:
                    ui.say(f"[SUGESTÃO] {issue.description}")
                with ui.stage("Salvar optimized_prompt.md"):
                    atomic_output(root, draft.markdown)
                return draft.markdown
            if revision == config.max_revision_rounds:
                for issue in review.issues:
                    ui.say(f"[REVISÃO] {issue.description}")
                raise AppError("Limite de correções atingido; resultado anterior preservado.")
            draft = provider.call(
                "Corrigir prompt",
                {**context, "draft": draft.markdown, "review": review.model_dump()},
                Draft,
            )
    raise AssertionError("unreachable")
