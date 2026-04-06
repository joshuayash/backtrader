#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask API wrapper for backtrader backtesting engine.
"""
import os
import sys
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtrader Web UI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #00d4ff; margin-bottom: 30px; font-size: 2em; }
        .card { background: #16213e; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .card h2 { color: #00d4ff; margin-bottom: 16px; font-size: 1.2em; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }
        .form-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; color: #aaa; font-size: 0.9em; }
        input, select, textarea { width: 100%; padding: 12px; border: 1px solid #0f3460; border-radius: 8px; background: #0f3460; color: #fff; font-size: 1em; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #00d4ff; }
        textarea { height: 200px; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em; }
        .row { display: flex; gap: 16px; }
        .row .form-group { flex: 1; }
        button { width: 100%; padding: 16px; background: linear-gradient(135deg, #00d4ff, #0099cc); border: none; border-radius: 8px; color: #fff; font-size: 1.1em; font-weight: bold; cursor: pointer; transition: transform 0.2s; }
        button:hover { transform: scale(1.02); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .result { display: none; margin-top: 20px; }
        .result.show { display: block; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 20px; }
        .metric { background: #0f3460; padding: 16px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 1.8em; font-weight: bold; color: #00d4ff; }
        .metric-label { color: #888; font-size: 0.85em; margin-top: 4px; }
        .profit { color: #00ff88 !important; }
        .loss { color: #ff4757 !important; }
        .error { background: #2d1f1f; border: 1px solid #ff4757; padding: 16px; border-radius: 8px; color: #ff4757; }
        pre { background: #0f3460; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; }
        .loading { text-align: center; padding: 40px; display: none; }
        .loading.show { display: block; }
        .spinner { width: 40px; height: 40px; border: 4px solid #0f3460; border-top-color: #00d4ff; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .sample-code { font-size: 0.8em; color: #666; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Backtrader Web UI</h1>
        <form id="backtestForm">
            <div class="card">
                <h2>数据配置</h2>
                <div class="row">
                    <div class="form-group">
                        <label>数据源</label>
                        <select id="data_source" name="data_source">
                            <option value="yahoo">Yahoo Finance</option>
                            <option value="csv">CSV 文件</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>股票代码 / 符号</label>
                        <input type="text" id="data_symbol" name="data_symbol" value="AAPL" placeholder="如 AAPL, TSLA, BTC-USD">
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <label>开始日期</label>
                        <input type="date" id="fromdate" name="fromdate" value="2020-01-01">
                    </div>
                    <div class="form-group">
                        <label>结束日期</label>
                        <input type="date" id="todate" name="todate" value="2024-12-31">
                    </div>
                </div>
                <div class="form-group">
                    <label>初始资金</label>
                    <input type="number" id="initial_cash" name="initial_cash" value="10000">
                </div>
            </div>
            <div class="card">
                <h2>策略配置 (可选)</h2>
                <div class="form-group">
                    <label>自定义策略代码</label>
                    <textarea id="strategy_code" name="strategy_code" placeholder="class MyStrategy(bt.Strategy):
    params = dict(period=20)
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)
    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()"></textarea>
                    <div class="sample-code">留空则使用默认策略 (简单买入持有)</div>
                </div>
            </div>
            <button type="submit" id="submitBtn">运行回测</button>
        </form>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>回测运行中...</div>
        </div>
        <div class="result" id="result"></div>
    </div>
    <script>
        document.getElementById('backtestForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');

            submitBtn.disabled = true;
            loading.classList.add('show');
            result.classList.remove('show');

            const data = {
                data_source: form.data_source.value,
                data_symbol: form.data_symbol.value,
                fromdate: form.fromdate.value,
                todate: form.todate.value,
                initial_cash: parseFloat(form.initial_cash.value),
                strategy_code: form.strategy_code.value || null
            };

            try {
                const res = await fetch('/backtest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const json = await res.json();

                if (json.error) {
                    result.innerHTML = '<div class="error"><strong>错误:</strong><pre>' + json.error + '</pre><pre>' + (json.traceback || '') + '</pre></div>';
                } else {
                    const profit = json.profit;
                    const profitClass = profit >= 0 ? 'profit' : 'loss';
                    result.innerHTML = `
                        <div class="card">
                            <h2>回测结果</h2>
                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-value">$${json.final_value.toFixed(2)}</div>
                                    <div class="metric-label">最终价值</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value ${profitClass}">${profit >= 0 ? '+' : ''}$${profit.toFixed(2)}</div>
                                    <div class="metric-label">收益</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value ${profitClass}">${json.profit_pct.toFixed(2)}%</div>
                                    <div class="metric-label">收益率</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${json.analyzers.sharpe || 'N/A'}</div>
                                    <div class="metric-label">夏普比率</div>
                                </div>
                            </div>
                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-value">${json.analyzers.max_drawdown_pct ? json.analyzers.max_drawdown_pct.toFixed(2) + '%' : 'N/A'}</div>
                                    <div class="metric-label">最大回撤</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${json.analyzers.total_trades || 0}</div>
                                    <div class="metric-label">总交易</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value" style="color:#00ff88">${json.analyzers.won_trades || 0}</div>
                                    <div class="metric-label">盈利</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value" style="color:#ff4757">${json.analyzers.lost_trades || 0}</div>
                                    <div class="metric-label">亏损</div>
                                </div>
                            </div>
                        </div>
                    `;
                }
                result.classList.add('show');
            } catch (err) {
                result.innerHTML = '<div class="error">请求失败: ' + err.message + '</div>';
                result.classList.add('show');
            }

            submitBtn.disabled = false;
            loading.classList.remove('show');
        });
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/backtest', methods=['POST'])
def backtest():
    """
    Run a backtest with the provided configuration.
    """
    try:
        import backtrader as bt
        from datetime import datetime
        from io import StringIO

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        strategy_code = data.get('strategy_code')
        data_source = data.get('data_source', 'yahoo')
        data_symbol = data.get('data_symbol', 'AAPL')
        data_params = data.get('data_params', {})
        strategy_params = data.get('strategy_params', {})
        fromdate = data.get('fromdate', '2020-01-01')
        todate = data.get('todate', '2024-12-31')
        initial_cash = data.get('initial_cash', 10000)
        broker_params = data.get('broker_params', {})

        fromdate_dt = datetime.strptime(fromdate, '%Y-%m-%d')
        todate_dt = datetime.strptime(todate, '%Y-%m-%d')

        cerebro = bt.Cerebro()
        cerebro.broker.set_cash(initial_cash)
        for key, value in broker_params.items():
            getattr(cerebro.broker, f'set_{key}')(value)

        if data_source == 'yahoo':
            data_feed = bt.feeds.YahooFinanceData(
                dataname=data_symbol,
                fromdate=fromdate_dt,
                todate=todate_dt,
                **data_params
            )
        elif data_source == 'csv':
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

        if strategy_code:
            try:
                compiled = compile(strategy_code, '<strategy>', 'exec')
                strategy_globals = {'bt': bt, 'datetime': datetime}
                exec(compiled, strategy_globals)
                strategy_class = None
                for key, obj in strategy_globals.items():
                    if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                        strategy_class = obj
                if not strategy_class:
                    return jsonify({'error': 'No Strategy class found in strategy_code'}), 400
            except Exception as e:
                return jsonify({'error': f'Failed to compile strategy: {str(e)}'}), 400
        else:
            strategy_class = bt.Strategy

        cerebro.addstrategy(strategy_class, **strategy_params)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        results = cerebro.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        strategy = results[0]
        sharpe = strategy.analyzers.sharpe.get_analysis() if hasattr(strategy.analyzers.sharpe, 'get_analysis') else {}
        drawdown = strategy.analyzers.drawdown.get_analysis()
        returns = strategy.analyzers.returns.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
