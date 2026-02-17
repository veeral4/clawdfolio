"""Tests for market hours module."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from clawdfolio.market.hours import (
    MarketHours,
    MarketSession,
    MarketStatus,
    _get_market_hours,
    get_market_status,
    is_market_open,
    time_to_close,
    time_to_open,
)


class TestMarketHours:
    """Tests for MarketHours class methods."""

    def _make_dt(self, hour: int, minute: int = 0, tz: str = "America/New_York") -> datetime:
        return datetime(2025, 6, 16, hour, minute, tzinfo=ZoneInfo(tz))  # a Monday

    def test_is_pre_market(self):
        us = MarketHours.US
        assert us.is_pre_market(self._make_dt(5, 0)) is True
        assert us.is_pre_market(self._make_dt(9, 29)) is True
        assert us.is_pre_market(self._make_dt(9, 30)) is False
        assert us.is_pre_market(self._make_dt(3, 0)) is False

    def test_is_market_open(self):
        us = MarketHours.US
        assert us.is_market_open(self._make_dt(9, 30)) is True
        assert us.is_market_open(self._make_dt(12, 0)) is True
        assert us.is_market_open(self._make_dt(15, 59)) is True
        assert us.is_market_open(self._make_dt(16, 0)) is False
        assert us.is_market_open(self._make_dt(9, 29)) is False

    def test_is_after_hours(self):
        us = MarketHours.US
        assert us.is_after_hours(self._make_dt(16, 0)) is True
        assert us.is_after_hours(self._make_dt(18, 0)) is True
        assert us.is_after_hours(self._make_dt(19, 59)) is True
        assert us.is_after_hours(self._make_dt(20, 0)) is False
        assert us.is_after_hours(self._make_dt(12, 0)) is False

    def test_is_extended_hours(self):
        us = MarketHours.US
        assert us.is_extended_hours(self._make_dt(5, 0)) is True  # pre-market
        assert us.is_extended_hours(self._make_dt(17, 0)) is True  # after-hours
        assert us.is_extended_hours(self._make_dt(12, 0)) is False  # regular
        assert us.is_extended_hours(self._make_dt(21, 0)) is False  # closed

    def test_get_status(self):
        us = MarketHours.US
        assert us.get_status(self._make_dt(5, 0)) == MarketStatus.PRE_MARKET
        assert us.get_status(self._make_dt(10, 0)) == MarketStatus.OPEN
        assert us.get_status(self._make_dt(17, 0)) == MarketStatus.AFTER_HOURS
        assert us.get_status(self._make_dt(21, 0)) == MarketStatus.CLOSED

    def test_time_to_open_when_open(self):
        us = MarketHours.US
        result = us.time_to_open(self._make_dt(12, 0))
        assert result is None

    def test_time_to_open_before_open(self):
        us = MarketHours.US
        result = us.time_to_open(self._make_dt(8, 30))
        assert result is not None
        assert result == timedelta(hours=1)

    def test_time_to_open_after_close(self):
        us = MarketHours.US
        dt = self._make_dt(17, 0)
        result = us.time_to_open(dt)
        assert result is not None
        # Should be next day 9:30 - 17:00 = 16.5 hours
        assert result == timedelta(hours=16, minutes=30)

    def test_time_to_close_when_open(self):
        us = MarketHours.US
        result = us.time_to_close(self._make_dt(14, 0))
        assert result == timedelta(hours=2)

    def test_time_to_close_when_closed(self):
        us = MarketHours.US
        assert us.time_to_close(self._make_dt(17, 0)) is None

    def test_hk_market(self):
        hk = MarketHours.HK
        dt_open = datetime(2025, 6, 16, 10, 0, tzinfo=ZoneInfo("Asia/Hong_Kong"))
        assert hk.is_market_open(dt_open) is True
        assert hk.get_status(dt_open) == MarketStatus.OPEN

    def test_cn_market(self):
        cn = MarketHours.CN
        dt_open = datetime(2025, 6, 16, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        assert cn.is_market_open(dt_open) is True


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_market_hours_us(self):
        assert _get_market_hours("US").market == "US"

    def test_get_market_hours_hk(self):
        assert _get_market_hours("HK").market == "HK"

    def test_get_market_hours_cn(self):
        assert _get_market_hours("CN").market == "CN"

    def test_get_market_hours_unknown_defaults_us(self):
        assert _get_market_hours("XX").market == "US"

    def test_get_market_hours_case_insensitive(self):
        assert _get_market_hours("us").market == "US"

    def test_is_market_open_returns_bool(self):
        # Just check it returns a boolean without error
        result = is_market_open("US")
        assert isinstance(result, bool)

    def test_get_market_status_returns_status(self):
        result = get_market_status("US")
        assert isinstance(result, MarketStatus)

    def test_time_to_open_returns_type(self):
        result = time_to_open("US")
        assert result is None or isinstance(result, timedelta)

    def test_time_to_close_returns_type(self):
        result = time_to_close("US")
        assert result is None or isinstance(result, timedelta)
