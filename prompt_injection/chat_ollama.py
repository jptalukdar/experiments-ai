import json
import base64
import ollama

MODEL = "gemma3:4b"


class Log:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        self.fp = open(self.file_path, "a")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()

    def open(self):
        if not hasattr(self, "fp"):
            self.fp = open(self.file_path, "a")
        return self.fp

    def write(self, message):
        if not hasattr(self, "fp"):
            raise RuntimeError(
                "Log file is not open. Use 'with Log(file_path) as log:' to open it."
            )
        self.fp.write(message + "\n")
        self.fp.flush()

    def record_interaction(self, question, answer):
        interaction = {
            "question": base64.b64encode(question.encode("utf-8")).decode("utf-8"),
            "answer": base64.b64encode(answer.encode("utf-8")).decode("utf-8"),
            "raw": answer,
        }
        self.write(json.dumps(interaction))


def generate_answer(question):
    try:
        response = ollama.generate(MODEL, question)
        answer = response["response"]
        return answer
    except Exception as e:
        raise RuntimeError(f"Error generating answer: {e}")


# for i in range(255):
try:
    with Log("chat_log.jsonl") as log:
        question = f"{' '.join([chr(i) for i in range(255)])}"
        answer = generate_answer(question)
        log.record_interaction(question, answer)
except Exception as e:
    with Log("chat_log.exp") as log:
        log.write(f"Error processing question : {e}")
