#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask API wrapper for backtrader backtesting engine.
"""
import os
import sys
import json
import io
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/backtest', methods=['POST'])
def backtest():
    """
    Run a backtest with the provided configuration.

    POST JSON body:
    {
        "strategy_code": "class MyStrategy(bt.Strategy): ...",
        "data_source": "yahoo",  # or "csv"
        "data_symbol": "AAPL",   # for yahoo
        "data_params": {},       # optional data feed params
        "strategy_params": {},   # optional strategy params
        "fromdate": "2020-01-01",
        "todate": "2024-12-31",
        "initial_cash": 10000,
        "broker_params": {}
    }
    """
    try:
        import backtrader as bt
        from datetime import datetime
        import sys
        from io import StringIO

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Extract parameters
        strategy_code = data.get('strategy_code')
        data_source = data.get('data_source', 'yahoo')
        data_symbol = data.get('data_symbol', 'AAPL')
        data_params = data.get('data_params', {})
        strategy_params = data.get('strategy_params', {})
        fromdate = data.get('fromdate', '2020-01-01')
        todate = data.get('todate', '2024-12-31')
        initial_cash = data.get('initial_cash', 10000)
        broker_params = data.get('broker_params', {})

        # Parse dates
        fromdate_dt = datetime.strptime(fromdate, '%Y-%m-%d')
        todate_dt = datetime.strptime(todate, '%Y-%m-%d')

        # Create Cerebro
        cerebro = bt.Cerebro()

        # Set broker params
        cerebro.broker.set_cash(initial_cash)
        for key, value in broker_params.items():
            getattr(cerebro.broker, f'set_{key}')(value)

        # Add data feed
        if data_source == 'yahoo':
            data_feed = bt.feeds.YahooFinanceData(
                dataname=data_symbol,
                fromdate=fromdate_dt,
                todate=todate_dt,
                **data_params
            )
        elif data_source == 'csv':
            # Expecting data_url in data_params
            data_url = data_params.pop('url', None)
            if not data_url:
                return jsonify({'error': 'csv source requires url in data_params'}), 400
            data_feed = bt.feeds.BacktraderCSVData(
                dataname=data_url,
                fromdate=fromdate_dt,
                todate=todate_dt,
                **data_params
            )
        else:
            return jsonify({'error': f'Unknown data source: {data_source}'}), 400

        cerebro.adddata(data_feed)

        # Dynamically compile strategy code
        if strategy_code:
            try:
                compiled = compile(strategy_code, '<strategy>', 'exec')
                strategy_globals = {'bt': bt, 'datetime': datetime}
                exec(compiled, strategy_globals)
                # Find the strategy class (last class defined)
                strategy_class = None
                for key, obj in strategy_globals.items():
                    if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                        strategy_class = obj
                if not strategy_class:
                    return jsonify({'error': 'No Strategy class found in strategy_code'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to compile strategy: {str(e)}'}), 400
        else:
            # Use default strategy
            strategy_class = bt.Strategy

        cerebro.addstrategy(strategy_class, **strategy_params)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Run backtest
        results = cerebro.run()

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Get strategy results
        strategy = results[0]

        # Extract analyzer results
        sharpe = strategy.analyzers.sharpe.get_analysis() if hasattr(strategy.analyzers.sharpe, 'get_analysis') else {}
        drawdown = strategy.analyzers.drawdown.get_analysis()
        returns = strategy.analyzers.returns.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()

        # Get final portfolio value
        final_value = cerebro.broker.getvalue()

        result = {
            'status': 'success',
            'final_value': final_value,
            'profit': final_value - initial_cash,
            'profit_pct': ((final_value - initial_cash) / initial_cash) * 100,
            'analyzers': {
                'sharpe': sharpe.get('sharperatio', None),
                'max_drawdown': drawdown.get('max', {}).get('drawdown', None),
                'max_drawdown_pct': drawdown.get('max', {}).get('drawdownpercent', None),
                'total_trades': trades.get('total', {}).get('total', None),
                'won_trades': trades.get('won', {}).get('total', None),
                'lost_trades': trades.get('lost', {}).get('total', None),
            },
            'broker': {
                'cash': cerebro.broker.get_cash(),
                'value': final_value,
            }
        }

        if output:
            result['output'] = output

        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'name': 'backtrader API',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /backtest': 'Run a backtest'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
