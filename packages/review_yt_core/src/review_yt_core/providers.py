import ipaddress
import re
import time
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from .domain import Failure
from .network import exchange

PROVIDER_IDS = ("disabled", "ollama", "openrouter", "openai", "gemini", "groq")
CLOUD = {
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta",
    "groq": "https://api.groq.com/openai/v1",
}


def flag(value):
    if str(value).lower() not in ("true", "false"):
        raise ValueError("Boolean settings require true or false")
    return str(value).lower() == "true"


@dataclass(frozen=True)
class AIConfig:
    selected: str = "disabled"
    allowed: tuple = PROVIDER_IDS
    model: dict = field(default_factory=dict)
    credentials: dict = field(default_factory=dict, repr=False)
    local_origin: str = "http://127.0.0.1:11434"
    paid: bool = False
    confirmed: tuple = ()
    seconds: float = 75
    output_limit: int = 768

    @classmethod
    def read(cls, env):
        if flag(env.get("SUMMARY_FALLBACK_ENABLED", "false")):
            raise ValueError("This implementation does not enable automatic fallback")
        allowed = tuple(
            x.strip()
            for x in env.get("SUMMARY_ENABLED_PROVIDERS", ",".join(PROVIDER_IDS)).split(",")
        )
        selected = env.get("SUMMARY_PROVIDER", "disabled")
        origin = env.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        parsed = urlsplit(origin)
        try:
            port = parsed.port
            if port is not None and not 1 <= port <= 65535:
                raise ValueError()
            local = (
                parsed.hostname == "localhost"
                or ipaddress.ip_address(parsed.hostname or "").is_loopback
            )
        except ValueError:
            local = False
        if (
            not local
            or parsed.scheme != "http"
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Ollama must use an HTTP loopback origin")
        if selected not in allowed or any(p not in PROVIDER_IDS for p in allowed):
            raise ValueError("Unknown or disallowed summary provider")
        for p in PROVIDER_IDS:
            name = env.get(p.upper() + "_MODEL", "")
            if (
                name
                and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_:./+@-]{0,190}", name)
                or any(part in (".", "..") for part in name.split("/"))
            ):
                raise ValueError("Invalid model identifier")
        return cls(
            selected,
            allowed,
            {
                p: env.get(
                    p.upper() + "_MODEL",
                    "openrouter/free"
                    if p == "openrouter"
                    else "gpt-4.1-mini"
                    if p == "openai"
                    else "",
                )
                for p in PROVIDER_IDS
            },
            {p: env.get(p.upper() + "_API_KEY", "") for p in CLOUD},
            origin.rstrip("/"),
            flag(env.get("SUMMARY_ALLOW_PAID", "false")),
            tuple(
                p
                for p in ("groq", "gemini")
                if flag(env.get(p.upper() + "_FREE_TIER_CONFIRMED", "false"))
            ),
        )


def zero_price(model):
    price = model.get("pricing", {})
    try:
        return {"prompt", "completion"} <= price.keys() and all(
            Decimal(str(v)).is_finite() and Decimal(str(v)) == 0 for v in price.values()
        )
    except (InvalidOperation, TypeError, AttributeError):
        return False


@dataclass
class Generation:
    text: str
    model: str
    usage: dict
    complete: bool
    milliseconds: int


class TextProvider:
    def __init__(self, config, identity, client=None):
        if identity not in config.allowed:
            raise Failure("provider_input", "This summary provider is not enabled.", 400)
        self.config, self.identity, self.client = config, identity, client
        self.model = config.model.get(identity, "")
        self.base = config.local_origin if identity == "ollama" else CLOUD.get(identity, "")

    def availability(self):
        if self.identity == "disabled":
            return True, "Sentiment only; no model requests."
        if not self.model:
            return False, "No model has been selected by the server operator."
        if self.identity != "ollama" and not self.config.credentials.get(self.identity):
            return False, "A server credential is required."
        if self.identity == "openai" and not self.config.paid:
            return False, "Paid inference has not been authorized."
        if (
            self.identity in ("gemini", "groq")
            and not self.config.paid
            and self.identity not in self.config.confirmed
        ):
            return False, "Free-tier eligibility must be confirmed by the operator."
        return True, "Configured; real inference can still fail or be rate limited."

    def request(self, method, suffix, body=None, seconds=None):
        key = self.config.credentials.get(self.identity, "")
        headers = (
            {"x-goog-api-key": key}
            if self.identity == "gemini"
            else {"Authorization": "Bearer " + key}
            if key
            else {}
        )
        status, data = exchange(
            method,
            self.base + suffix,
            payload=body,
            headers=headers,
            timeout=seconds or self.config.seconds,
            client=self.client,
        )
        if status >= 300 or "error" in data:
            code = {
                401: "ai_unauthorized",
                402: "ai_payment_required",
                403: "ai_forbidden",
                404: "ai_model_missing",
                429: "ai_rate_limited",
            }.get(status, "ai_provider_error")
            raise Failure(
                code,
                {
                    "ai_unauthorized": "The provider rejected its configured credential.",
                    "ai_payment_required": "The provider requires credits; paid fallback is disabled.",
                    "ai_rate_limited": "Free inference is rate limited. Sentiment results remain available.",
                }.get(code, "The selected model could not generate a summary."),
                503,
            )
        return data

    def discover(self):
        data = self.request(
            "GET", "/api/tags" if self.identity == "ollama" else "/models", seconds=6
        )
        values = data.get("models" if self.identity in ("ollama", "gemini") else "data", [])
        return values if isinstance(values, list) else []

    def generate(self, instructions, evidence):
        ready, reason = self.availability()
        if not ready or self.identity == "disabled":
            raise Failure("ai_unavailable", reason, 503)
        start = time.monotonic()
        cap = self.config.output_limit
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": evidence[:14000]},
        ]
        if self.identity == "openrouter":
            match = next((m for m in self.discover() if m.get("id") == self.model), None)
            if match is None or not self.config.paid and not zero_price(match):
                raise Failure(
                    "ai_price_unverified",
                    "No generation was sent because zero model pricing could not be verified.",
                    503,
                )
        if self.identity == "ollama":
            suffix, body = (
                "/api/chat",
                {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                    "format": "json",
                    "options": {"num_predict": cap, "temperature": 0.2, "num_ctx": 8192},
                },
            )
        elif self.identity == "gemini":
            suffix, body = (
                "/models/" + self.model + ":generateContent",
                {
                    "systemInstruction": {"parts": [{"text": instructions}]},
                    "contents": [{"role": "user", "parts": [{"text": evidence[:14000]}]}],
                    "generationConfig": {"maxOutputTokens": cap, "temperature": 0.2},
                },
            )
        elif self.identity == "openai":
            suffix, body = (
                "/responses",
                {
                    "model": self.model,
                    "instructions": instructions,
                    "input": evidence[:14000],
                    "max_output_tokens": cap,
                    "store": False,
                },
            )
        else:
            suffix, body = (
                "/chat/completions",
                {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": cap,
                    "temperature": 0.2,
                    "stream": False,
                },
            )
            if self.identity == "openrouter":
                body["provider"] = {"allow_fallbacks": False}
                if not self.config.paid:
                    body["provider"]["max_price"] = {"prompt": 0, "completion": 0}
        remaining = self.config.seconds - (time.monotonic() - start)
        if remaining <= 0:
            raise Failure("ai_timeout", "Discovery exhausted the inference budget.", 504)
        data = self.request("POST", suffix, body, seconds=remaining)
        try:
            actual = data.get("model", self.model)
            usage = data.get("usage", {})
            if self.identity == "ollama":
                text, complete = (
                    data["message"]["content"],
                    data.get("done") is True and data.get("done_reason") != "length",
                )
                usage = {
                    "inputTokens": data.get("prompt_eval_count"),
                    "outputTokens": data.get("eval_count"),
                }
            elif self.identity == "gemini":
                item = data["candidates"][0]
                text = "".join(
                    p.get("text", "") for p in item["content"]["parts"] if not p.get("thought")
                )
                complete = item.get("finishReason") == "STOP"
                actual = data.get("modelVersion", self.model)
                usage = data.get("usageMetadata", {})
            elif self.identity == "openai":
                text = "".join(
                    p["text"]
                    for item in data.get("output", [])
                    if item.get("type") == "message"
                    for p in item.get("content", [])
                    if p.get("type") == "output_text"
                )
                complete = data.get("status") == "completed"
            else:
                item = data["choices"][0]
                text, complete = item["message"]["content"], item.get("finish_reason") == "stop"
            if (
                not isinstance(text, str)
                or not text.strip()
                or len(text) > 40000
                or not isinstance(actual, str)
            ):
                raise ValueError()
            permitted = {
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "input_tokens",
                "output_tokens",
                "inputTokens",
                "outputTokens",
                "promptTokenCount",
                "candidatesTokenCount",
                "totalTokenCount",
            }
            usage = {
                k: v
                for k, v in usage.items()
                if k in permitted and isinstance(v, int) and not isinstance(v, bool) and v >= 0
            }
            return Generation(
                text, actual, usage, complete, round((time.monotonic() - start) * 1000)
            )
        except (KeyError, IndexError, TypeError, ValueError, AttributeError):
            raise Failure(
                "ai_response_invalid", "The model did not return usable summary content."
            ) from None
