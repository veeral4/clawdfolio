"""Tests for console output formatting."""

from __future__ import annotations

from decimal import Decimal
from io import StringIO

from rich.console import Console

from clawdfolio.core.types import (
    Alert,
    AlertSeverity,
    AlertType,
    Exchange,
    Portfolio,
    Position,
    RiskMetrics,
    Symbol,
)
from clawdfolio.output.console import (
    ConsoleFormatter,
    _format_money,
    _format_pct,
    _get_color,
    print_portfolio,
    print_risk_metrics,
)


class TestFormatHelpers:
    """Tests for formatting helper functions."""

    def test_format_money_positive(self):
        assert _format_money(1234.56) == "+$1,234.56"

    def test_format_money_negative(self):
        assert _format_money(-500.0) == "$-500.00"

    def test_format_money_zero(self):
        assert _format_money(0.0) == "$0.00"

    def test_format_pct_positive(self):
        assert _format_pct(0.0523) == "+5.23%"

    def test_format_pct_negative(self):
        assert _format_pct(-0.032) == "-3.20%"

    def test_get_color_positive(self):
        assert _get_color(1.0) == "green"

    def test_get_color_negative(self):
        assert _get_color(-1.0) == "red"

    def test_get_color_zero(self):
        assert _get_color(0.0) == "white"


def _make_test_portfolio() -> Portfolio:
    pos = Position(
        symbol=Symbol(ticker="AAPL", exchange=Exchange.NASDAQ, name="Apple"),
        quantity=Decimal("100"),
        avg_cost=Decimal("150"),
        market_value=Decimal("17500"),
        current_price=Decimal("175"),
        unrealized_pnl=Decimal("2500"),
        day_pnl=Decimal("100"),
        day_pnl_pct=0.005,
    )
    opt = Position(
        symbol=Symbol(ticker="AAPL250620C180", exchange=Exchange.NASDAQ),
        quantity=Decimal("5"),
        avg_cost=Decimal("3.50"),
        market_value=Decimal("1750"),
        current_price=Decimal("3.50"),
        unrealized_pnl=Decimal("0"),
        is_option=True,
    )
    return Portfolio(
        positions=[pos, opt],
        net_assets=Decimal("50000"),
        market_value=Decimal("19250"),
        cash=Decimal("30750"),
        day_pnl=Decimal("100"),
        day_pnl_pct=0.002,
    )


class TestConsoleFormatter:
    """Tests for ConsoleFormatter."""

    def test_print_portfolio(self):
        console = Console(file=StringIO(), force_terminal=True)
        formatter = ConsoleFormatter(console=console)
        portfolio = _make_test_portfolio()
        # Should not raise
        formatter.print_portfolio(portfolio)
        output = console.file.getvalue()
        assert "Portfolio Summary" in output
        assert "AAPL" in output

    def test_print_risk_metrics(self):
        console = Console(file=StringIO(), force_terminal=True)
        formatter = ConsoleFormatter(console=console)
        metrics = RiskMetrics(
            volatility_annualized=0.25,
            beta_spy=1.1,
            beta_qqq=1.3,
            sharpe_ratio=1.5,
            var_95=0.03,
            var_95_amount=Decimal("1500"),
            max_drawdown=0.15,
            hhi=0.08,
            high_corr_pairs=[("AAPL", "MSFT", 0.85)],
        )
        formatter.print_risk_metrics(metrics)
        output = console.file.getvalue()
        assert "Risk Metrics" in output
        assert "1.10" in output  # beta

    def test_print_risk_metrics_no_high_corr(self):
        console = Console(file=StringIO(), force_terminal=True)
        formatter = ConsoleFormatter(console=console)
        metrics = RiskMetrics(volatility_annualized=0.20)
        formatter.print_risk_metrics(metrics)
        output = console.file.getvalue()
        assert "Risk Metrics" in output

    def test_print_alerts_empty(self):
        console = Console(file=StringIO(), force_terminal=True)
        formatter = ConsoleFormatter(console=console)
        formatter.print_alerts([])
        output = console.file.getvalue()
        assert "No alerts" in output

    def test_print_alerts_with_items(self):
        console = Console(file=StringIO(), force_terminal=True)
        formatter = ConsoleFormatter(console=console)
        alerts = [
            Alert(
                type=AlertType.PRICE_MOVE,
                severity=AlertSeverity.WARNING,
                title="AAPL moved",
                message="AAPL moved +5%",
                ticker="AAPL",
            ),
            Alert(
                type=AlertType.PNL_THRESHOLD,
                severity=AlertSeverity.CRITICAL,
                title="Big loss",
                message="Portfolio down -3%",
            ),
            Alert(
                type=AlertType.CONCENTRATION,
                severity=AlertSeverity.INFO,
                title="Concentration",
                message="Top 5 at 80%",
            ),
        ]
        formatter.print_alerts(alerts)
        output = console.file.getvalue()
        assert "AAPL moved" in output
        assert "Big loss" in output


class TestConvenienceFunctions:
    """Tests for module-level print functions."""

    def test_print_portfolio_function(self):
        portfolio = _make_test_portfolio()
        # Should not raise (uses Rich if available)
        print_portfolio(portfolio)

    def test_print_risk_metrics_function(self):
        metrics = RiskMetrics(volatility_annualized=0.20, beta_spy=1.0)
        print_risk_metrics(metrics)
