import re

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

SENT_SPLIT = re.compile(r"(?<=[\.!?…])\s+")

def _extractive_summary(text: str, max_sent: int = 3) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    sents = SENT_SPLIT.split(text)
    sents = [s.strip() for s in sents if len(s.strip()) > 0]
    return " ".join(sents[:max_sent])

def _llm_summary(text: str, max_sent: int = 3) -> str:
    if not OpenAI:
        return _extractive_summary(text, max_sent)
    try:
        client = OpenAI()
        prompt = (
            "Tóm tắt ngắn gọn nội dung sau bằng tiếng Việt, tối đa 3 câu, "
            "không thêm thông tin ngoài bài:\n\n" + text[:6000]
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=220,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return _extractive_summary(text, max_sent)

def summarize_text(text: str, use_llm: bool = False) -> str:
    return _llm_summary(text) if use_llm else _extractive_summary(text)
