"""Configuração do GERADOR; não confundir com a IA destinatária em user/configs.toml."""

PROVIDER = "openai"
MODEL = "gpt-5-mini"
BASE_URL = "https://api.openai.com/v1"
API_TIMEOUT_SECONDS = 120
API_MAX_RETRIES = 2
MAX_OUTPUT_TOKENS = 12000
MAX_SEED_BYTES = 120_000
MAX_ANSWER_CHARS = 10_000
MAX_QUESTIONS_PER_ROUND = 3
