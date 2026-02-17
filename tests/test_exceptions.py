"""Tests for custom exceptions."""

from __future__ import annotations

import pytest

from clawdfolio.core.exceptions import (
    AuthenticationError,
    BrokerError,
    ConfigError,
    MarketClosedError,
    MarketDataError,
    PortfolioMonitorError,
    RateLimitError,
)


class TestExceptions:
    """Tests for exception classes."""

    def test_portfolio_monitor_error(self):
        with pytest.raises(PortfolioMonitorError):
            raise PortfolioMonitorError("base error")

    def test_broker_error(self):
        err = BrokerError("longport", "connection failed")
        assert err.broker == "longport"
        assert "[longport] connection failed" in str(err)

    def test_config_error(self):
        with pytest.raises(ConfigError):
            raise ConfigError("missing key")

    def test_market_data_error(self):
        err = MarketDataError("AAPL", "yfinance", "timeout")
        assert err.ticker == "AAPL"
        assert err.source == "yfinance"
        assert "[yfinance] AAPL: timeout" in str(err)

    def test_authentication_error(self):
        err = AuthenticationError("futu")
        assert err.broker == "futu"
        assert "Authentication failed" in str(err)

    def test_rate_limit_error_no_retry(self):
        err = RateLimitError("longport")
        assert err.retry_after is None
        assert "Rate limit exceeded" in str(err)

    def test_rate_limit_error_with_retry(self):
        err = RateLimitError("longport", retry_after=30)
        assert err.retry_after == 30
        assert "retry after 30s" in str(err)

    def test_market_closed_error(self):
        err = MarketClosedError("HK")
        assert err.market == "HK"
        assert "HK market is currently closed" in str(err)

    def test_market_closed_error_default(self):
        err = MarketClosedError()
        assert "US" in str(err)

    def test_inheritance(self):
        assert issubclass(BrokerError, PortfolioMonitorError)
        assert issubclass(AuthenticationError, BrokerError)
        assert issubclass(RateLimitError, BrokerError)
        assert issubclass(ConfigError, PortfolioMonitorError)
        assert issubclass(MarketDataError, PortfolioMonitorError)
        assert issubclass(MarketClosedError, PortfolioMonitorError)
