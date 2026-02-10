"""Tests for option buyback monitor."""

from __future__ import annotations

from clawdfolio.core.config import OptionBuybackConfig, OptionBuybackTargetConfig
from clawdfolio.market.data import OptionQuoteData
from clawdfolio.monitors.options import OptionBuybackMonitor


def test_buyback_monitor_triggers_then_deduplicates(monkeypatch, tmp_path):
    cfg = OptionBuybackConfig(
        enabled=True,
        symbol="TQQQ",
        state_path=str(tmp_path / "buyback_state.json"),
        targets=[
            OptionBuybackTargetConfig(
                name="target1",
                strike=60.0,
                expiry="2026-06-18",
                option_type="C",
                trigger_price=1.60,
                qty=2,
                reset_pct=0.20,
            ),
            OptionBuybackTargetConfig(
                name="target2",
                strike=60.0,
                expiry="2026-06-18",
                option_type="C",
                trigger_price=0.80,
                qty=1,
                reset_pct=0.20,
            ),
        ],
    )

    quote = OptionQuoteData(
        ticker="TQQQ",
        expiry="2026-06-18",
        strike=60.0,
        option_type="C",
        bid=1.45,
        ask=1.55,
        last=1.50,
        source="test",
    )
    monkeypatch.setattr(
        "clawdfolio.monitors.options.get_option_quote",
        lambda *_args, **_kwargs: quote,
    )

    monitor = OptionBuybackMonitor(cfg)
    first = monitor.check()
    second = monitor.check()

    assert first is not None
    assert len(first.triggered) == 1
    assert first.triggered[0].name == "target1"

    assert second is not None
    assert len(second.triggered) == 0


def test_buyback_monitor_resets_after_rebound(monkeypatch, tmp_path):
    cfg = OptionBuybackConfig(
        enabled=True,
        symbol="TQQQ",
        state_path=str(tmp_path / "buyback_state.json"),
        targets=[
            OptionBuybackTargetConfig(
                name="target1",
                strike=60.0,
                expiry="2026-06-18",
                option_type="C",
                trigger_price=1.60,
                qty=2,
                reset_pct=0.20,
            ),
        ],
    )

    quote_series = [
        OptionQuoteData(
            ticker="TQQQ",
            expiry="2026-06-18",
            strike=60.0,
            option_type="C",
            last=1.50,  # trigger
            source="test",
        ),
        OptionQuoteData(
            ticker="TQQQ",
            expiry="2026-06-18",
            strike=60.0,
            option_type="C",
            last=2.00,  # reset (> 1.6 * 1.2)
            source="test",
        ),
        OptionQuoteData(
            ticker="TQQQ",
            expiry="2026-06-18",
            strike=60.0,
            option_type="C",
            last=1.55,  # trigger again after reset
            source="test",
        ),
    ]

    def _fake_quote(*_args, **_kwargs):
        if quote_series:
            return quote_series.pop(0)
        return None

    monkeypatch.setattr("clawdfolio.monitors.options.get_option_quote", _fake_quote)

    monitor = OptionBuybackMonitor(cfg)
    first = monitor.check()
    second = monitor.check()
    third = monitor.check()

    assert first is not None and len(first.triggered) == 1
    assert second is not None and len(second.triggered) == 0
    assert third is not None and len(third.triggered) == 1
