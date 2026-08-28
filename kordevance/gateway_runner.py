import os

os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "1")

import uvicorn  # noqa: E402

from kordevance.application.main import app  # noqa: E402


def main() -> None:
    host = os.environ.get("KORDEVANCE_GATEWAY_HOST", "127.0.0.1")
    port = int(os.environ.get("KORDEVANCE_GATEWAY_PORT", "24680"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
