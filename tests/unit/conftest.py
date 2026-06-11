"""shared fixtures for the unit-tests."""

import pytest

from flipjump.interpreter import fjm_run


@pytest.fixture(params=['fast-python', 'native'])
def engine(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    """parametrizes a test over the pure-python fast loop and the native engine."""
    if request.param == 'native':
        if fjm_run._fjcore is None:  # type: ignore[attr-defined]
            pytest.skip('the native engine (_fjcore) is not built')
        monkeypatch.delenv('FLIPJUMP_NO_NATIVE', raising=False)
    else:
        monkeypatch.setattr(fjm_run, '_fjcore', None)
    return str(request.param)
