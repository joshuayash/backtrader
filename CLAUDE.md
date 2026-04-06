# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands

```bash
# Create virtual environment (one-time setup)
python3.12 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install matplotlib  # for plotting support

# Run all tests (from project root)
cd tests && nosetests -v -v

# Run a single test file
cd tests && python3.12 -m pytest test_order.py -v
```

## Architecture Overview

backtrader is a **backtesting engine** for trading strategies. The core execution flow:

1. **Cerebro** (`cerebro.py`) - Main orchestration class that runs the backtesting engine
2. **Strategy** (`strategy.py`) - Base class for user strategies; defines `__init__`, `next()`, `nextstart()`, `prenext()`
3. **Data Feeds** (`feeds/`) - Load market data (CSV, Yahoo, pandas, etc.)
4. **Indicators** (`indicators/`) - Technical indicators (SMA, RSI, MACD, etc.) built on `LineIterator`
5. **Analyzers** (`analyzers/`) - Performance metrics (Sharpe, DrawDown, TradeAnalyzer, etc.)
6. **Broker** (`broker.py`) - Simulates broker with order execution, commission schemes
7. **LineBuffer** (`linebuffer.py`) - Core data structure holding time-series lines

### Key Patterns

- **Lines**: Core data structure - each indicator/data has multiple `lines` (e.g., OHLC has `open, high, low, close`)
- **Params**: Strategies/indicators use `params` dict for configuration (metaclass-based)
- **Min Period**: Indicators have minimum periods before producing values; `prec伸next()` and `nextstart()` handle warmup
- **Observers**: Track system state (broker value, trades, orders) during backtesting
- **Resampling/Replaying**: `resamplerfilter.py` handles timeframes conversion

### Directory Structure

```
backtrader/
  __init__.py         # Main exports
  cerebro.py          # Core engine (63KB)
  strategy.py         # Strategy base class (61KB)
  indicator.py       # Indicator base class
  linebuffer.py       # Line data structure
  lineiterator.py    # Iterator over lines
  feeds/              # Data feed implementations
  indicators/         # Built-in indicators
  analyzers/          # Built-in analyzers
  brokers/            # Broker implementations (IB, Oanda, VisualChart)
  filters/            # Data filters (Renko, Heikin-Ashi, etc.)
samples/              # Example scripts
tests/                # Test suite
datas/                # Sample data files for tests
```

### Test Data

Test data files are in `datas/` directory (e.g., `2006-day-001.txt`). Tests use `tests/testcommon.py` which provides `getdata()` and `runtest()` helpers with `TestStrategy` base class.

### Entry Points

- CLI: `btrun` (installed via setup.py entry_points)
- Script: `tools/bt-run.py`
