"""The pipeline: message -> AI analysis -> lookup -> draft -> approval -> log.
Nothing is ever recorded as "sent" unless a human types y."""
from .ai import AIServiceError, InvalidAIOutput, call_gemini, parse_analysis
from .replies import draft_reply, load_data
from .status_log import append_entry

MAX_APPROVAL_TRIES = 3


def ask_approval(input_fn, print_fn) -> tuple[bool, str]:
    for _ in range(MAX_APPROVAL_TRIES):
        try:
            answer = input_fn("Send? (y/n) ").strip().lower()
        except EOFError:
            return False, "no answer from staff"
        if answer == "y":
            return True, "approved by staff"
        if answer == "n":
            return False, "staff answered n"
        print_fn("Please type y or n.")
    return False, "no valid answer from staff"


def process_enquiry(message, *, data_path, log_path, call_ai=call_gemini,
                    input_fn=input, print_fn=print) -> dict:
    record = {"customer_message": message, "draft": None, "needs_escalation": None,
              "ai_analysis": None}

    def finish(status, reason):
        return append_entry(log_path, {**record, "status": status, "reason": reason})

    if not message or not message.strip():
        print_fn("Empty message: nothing to do.")
        return finish("invalid_input", "empty customer message")

    try:
        raw = call_ai(message)
    except AIServiceError as exc:
        print_fn(f"AI service failed. Nothing was sent. ({exc})")
        return finish("failed_ai_service", str(exc))
    except Exception as exc:  # any unexpected failure also fails safe
        print_fn(f"AI service failed. Nothing was sent. ({type(exc).__name__})")
        return finish("failed_ai_service", f"{type(exc).__name__}: {exc}")

    try:
        analysis = parse_analysis(raw)
    except InvalidAIOutput as exc:
        print_fn("AI returned invalid data. Nothing was sent.")
        return finish("failed_invalid_ai_output", str(exc))
    record["ai_analysis"] = analysis.model_dump()

    draft = draft_reply(analysis, load_data(data_path))
    record["draft"], record["needs_escalation"] = draft.text, draft.needs_escalation

    print_fn("\n--- DRAFT REPLY ---")
    print_fn(draft.text)
    print_fn("-------------------")
    if draft.needs_escalation:
        print_fn("(Some facts are not in the data. Approving sends the escalation message.)")

    approved, reason = ask_approval(input_fn, print_fn)
    if approved:
        print_fn("Recorded as sent. (No message is actually sent in this version.)")
        return finish("sent", reason)
    print_fn("Not sent.")
    return finish("rejected", reason)
