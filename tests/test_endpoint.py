"""Live endpoint tests — require a running LLM server.

Run with: pytest tests/ -m endpoint --endpoint-config config.yaml
"""

import concurrent.futures

import pytest

from arc.eval.config import load_config

pytestmark = pytest.mark.endpoint


@pytest.fixture(scope="module")
def endpoint_cfg(request):
    config_path = request.config.getoption("--endpoint-config")
    if config_path is None:
        pytest.skip("--endpoint-config not provided")
    return load_config(config_path)


@pytest.fixture(scope="module")
def client(endpoint_cfg):
    from openai import OpenAI
    ep = endpoint_cfg["endpoint"]
    return OpenAI(base_url=ep["base_url"], api_key=ep["api_key"])


@pytest.fixture(scope="module")
def model_name(endpoint_cfg):
    return endpoint_cfg["endpoint"]["model"]


def test_health_check(client):
    """Verify that the endpoint lists at least one model."""
    models = client.models.list()
    assert len(models.data) > 0


def test_simple_chat_completion(client, model_name):
    """Send a trivial prompt and verify we get a non-empty response."""
    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Say hello."}],
        max_tokens=32,
    )
    assert resp.choices[0].message.content.strip()


def test_concurrent_chat_completions(client, model_name):
    """Simulate parallel workers hitting the endpoint concurrently."""
    n_requests = 4

    def make_request(i):
        resp = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": f"Count to {i + 1}."}],
            max_tokens=64,
        )
        return resp.choices[0].message.content

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_requests) as pool:
        futures = [pool.submit(make_request, i) for i in range(n_requests)]
        results = [f.result(timeout=60) for f in futures]

    assert len(results) == n_requests
    assert all(r.strip() for r in results)
