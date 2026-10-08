from userclient.client import build_url


def test_build_url() -> None:
    assert build_url(7).endswith("/users/7")
