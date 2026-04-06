#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backtrader Full-Featured Web UI
"""
import os
import sys
import json
import io
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtrader 全功能 Web UI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f23; color: #eee; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px; border-bottom: 1px solid #0f3460; }
        .header h1 { color: #00d4ff; font-size: 1.8em; text-align: center; }
        .nav { display: flex; background: #16213e; padding: 0 20px; overflow-x: auto; border-bottom: 1px solid #0f3460; }
        .nav button { background: none; border: none; color: #888; padding: 16px 24px; cursor: pointer; font-size: 1em; white-space: nowrap; transition: all 0.3s; }
        .nav button:hover { color: #00d4ff; }
        .nav button.active { color: #00d4ff; border-bottom: 2px solid #00d4ff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .section { display: none; }
        .section.active { display: block; }
        .card { background: #16213e; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .card h2 { color: #00d4ff; margin-bottom: 16px; font-size: 1.2em; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }
        .card h3 { color: #00d4ff; margin: 16px 0 12px; font-size: 1em; }
        .form-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; color: #aaa; font-size: 0.9em; }
        input, select, textarea { width: 100%; padding: 12px; border: 1px solid #0f3460; border-radius: 8px; background: #0f3460; color: #fff; font-size: 1em; transition: border-color 0.3s; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #00d4ff; }
        textarea { font-family: 'Monaco', 'Menlo', monospace; font-size: 0.85em; resize: vertical; }
        .row { display: flex; gap: 16px; flex-wrap: wrap; }
        .col { flex: 1; min-width: 200px; }
        button { padding: 12px 24px; background: linear-gradient(135deg, #00d4ff, #0099cc); border: none; border-radius: 8px; color: #fff; font-size: 1em; font-weight: bold; cursor: pointer; transition: transform 0.2s, opacity 0.2s; }
        button:hover { transform: scale(1.02); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        button.secondary { background: linear-gradient(135deg, #555, #333); }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px; }
        .metric { background: #0f3460; padding: 16px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 1.5em; font-weight: bold; color: #00d4ff; }
        .metric-label { color: #888; font-size: 0.8em; margin-top: 4px; }
        .profit { color: #00ff88 !important; }
        .loss { color: #ff4757 !important; }
        .error { background: #2d1f1f; border: 1px solid #ff4757; padding: 16px; border-radius: 8px; color: #ff4757; }
        pre { background: #0f3460; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 0.8em; max-height: 300px; }
        .loading { text-align: center; padding: 40px; display: none; }
        .loading.show { display: block; }
        .spinner { width: 40px; height: 40px; border: 4px solid #0f3460; border-top-color: #00d4ff; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { color: #00d4ff; font-weight: 600; }
        tr:hover { background: #0f3460; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .indicator-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
        .indicator-card { background: #0f3460; padding: 16px; border-radius: 8px; cursor: pointer; transition: transform 0.2s; }
        .indicator-card:hover { transform: scale(1.02); }
        .indicator-card h4 { color: #00d4ff; margin-bottom: 8px; }
        .indicator-card p { color: #888; font-size: 0.85em; }
        .chart-container { background: #0f3460; border-radius: 8px; padding: 16px; margin-top: 16px; min-height: 300px; }
        .optimization-results { max-height: 400px; overflow-y: auto; }
        .result-item { background: #0f3460; padding: 12px; margin-bottom: 8px; border-radius: 8px; cursor: pointer; transition: background 0.2s; }
        .result-item:hover { background: #1a4a7a; }
        .result-item.best { border: 2px solid #00ff88; }
        .strategy-template { cursor: pointer; background: #0f3460; padding: 12px; border-radius: 8px; margin-bottom: 8px; transition: background 0.2s; }
        .strategy-template:hover { background: #1a4a7a; }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
        .nav-tab { padding: 8px 16px; background: #0f3460; border: none; border-radius: 6px; color: #888; cursor: pointer; font-size: 0.9em; }
        .nav-tab.active { background: #00d4ff; color: #fff; }
        .data-table { font-size: 0.85em; }
        .data-table th { position: sticky; top: 0; background: #16213e; }
        .footer { text-align: center; padding: 20px; color: #555; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Backtrader 全功能 Web UI</h1>
    </div>
    <nav class="nav">
        <button class="active" onclick="showSection('dashboard')">Dashboard</button>
        <button onclick="showSection('data')">数据查看</button>
        <button onclick="showSection('indicators')">技术指标</button>
        <button onclick="showSection('backtest')">回测</button>
        <button onclick="showSection('optimize')">参数优化</button>
        <button onclick="showSection('analyzers')">分析器</button>
        <button onclick="showSection('strategies')">策略库</button>
    </nav>

    <div class="container">
        <!-- Dashboard Section -->
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>系统概览</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">7</div>
                        <div class="metric-label">可用指标</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">4</div>
                        <div class="metric-label">策略模板</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">8</div>
                        <div class="metric-label">分析器</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">1</div>
                        <div class="metric-label">数据源</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h2>快速开始</h2>
                <p style="color:#888; margin-bottom:16px;">选择一个功能开始，或者使用右侧的快捷操作</p>
                <div class="row">
                    <button onclick="showSection('backtest')">运行回测</button>
                    <button class="secondary" onclick="showSection('data')">查看数据</button>
                    <button class="secondary" onclick="showSection('indicators')">计算指标</button>
                </div>
            </div>
            <div class="card">
                <h2>最近回测结果</h2>
                <div id="recentResults">
                    <p style="color:#888;">运行回测后会显示在这里</p>
                </div>
            </div>
        </div>

        <!-- Data Viewer Section -->
        <div id="data" class="section">
            <div class="card">
                <h2>数据查看器</h2>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>股票代码</label>
                            <input type="text" id="dataSymbol" value="AAPL" placeholder="AAPL, TSLA, BTC-USD">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>数据范围</label>
                            <select id="dataRange">
                                <option value="1mo">1个月</option>
                                <option value="3mo">3个月</option>
                                <option value="6mo">6个月</option>
                                <option value="1y" selected>1年</option>
                                <option value="2y">2年</option>
                                <option value="5y">5年</option>
                                <option value="10y">10年</option>
                            </select>
                        </div>
                    </div>
                </div>
                <button onclick="loadData()">加载数据</button>
            </div>
            <div class="card">
                <h2>OHLCV 数据</h2>
                <div style="max-height: 400px; overflow-y: auto;">
                    <table class="data-table" id="dataTable">
                        <thead>
                            <tr><th>日期</th><th>开盘</th><th>最高</th><th>最低</th><th>收盘</th><th>成交量</th></tr>
                        </thead>
                        <tbody id="dataTableBody">
                            <tr><td colspan="6" style="text-align:center;color:#888;">加载数据...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="card">
                <h2>数据统计</h2>
                <div id="dataStats" class="metrics"></div>
            </div>
        </div>

        <!-- Indicators Section -->
        <div id="indicators" class="section">
            <div class="card">
                <h2>技术指标计算器</h2>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>股票代码</label>
                            <input type="text" id="indSymbol" value="AAPL" placeholder="AAPL, TSLA">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>时间范围</label>
                            <select id="indRange">
                                <option value="1y" selected>1年</option>
                                <option value="2y">2年</option>
                                <option value="5y">5年</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="indicator-grid">
                    <div class="indicator-card" onclick="calculateIndicator('SMA')">
                        <h4>SMA - 简单移动平均</h4>
                        <p>计算N日简单移动平均线</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('EMA')">
                        <h4>EMA - 指数移动平均</h4>
                        <p>计算N日指数移动平均线</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('RSI')">
                        <h4>RSI - 相对强弱指数</h4>
                        <p>衡量价格变动的速度和幅度</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('MACD')">
                        <h4>MACD - 指数平滑异同移动平均线</h4>
                        <p>趋势跟踪动量指标</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('BBANDS')">
                        <h4>BBANDS - 布林带</h4>
                        <p>价格波动的上中下轨</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('STOCH')">
                        <h4>STOCH - 随机指标</h4>
                        <p>超买超卖指标</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('ATR')">
                        <h4>ATR - 平均真实波幅</h4>
                        <p>衡量市场波动性</p>
                    </div>
                    <div class="indicator-card" onclick="calculateIndicator('ADX')">
                        <h4>ADX - 平均趋向指数</h4>
                        <p>趋势强度指标</p>
                    </div>
                </div>
            </div>
            <div class="card">
                <h2 id="indResultTitle">指标结果</h2>
                <div id="indResult" class="chart-container">
                    <p style="color:#888;">选择一个指标开始计算</p>
                </div>
            </div>
        </div>

        <!-- Backtest Section -->
        <div id="backtest" class="section">
            <div class="card">
                <h2>回测配置</h2>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>股票代码</label>
                            <input type="text" id="btSymbol" value="AAPL">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>时间范围</label>
                            <select id="btRange">
                                <option value="1y">1年</option>
                                <option value="2y" selected>2年</option>
                                <option value="5y">5年</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>初始资金</label>
                            <input type="number" id="btCash" value="10000">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>策略</label>
                            <select id="btStrategy" onchange="onStrategyChange()">
                                <option value="">默认策略(买入持有)</option>
                                <option value="sma_cross">均线交叉</option>
                                <option value="rsi_策略">RSI策略</option>
                                <option value="macd_cross">MACD交叉</option>
                                <option value="custom">自定义策略</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="form-group" id="customStrategyGroup" style="display:none;">
                    <label>自定义策略代码</label>
                    <textarea id="btCustomStrategy" placeholder="class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=20)
    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()"></textarea>
                </div>
                <div id="strategyParams" class="row" style="display:none;"></div>
                <button onclick="runBacktest()" id="btRunBtn">运行回测</button>
            </div>
            <div class="loading" id="btLoading">
                <div class="spinner"></div>
                <div>回测运行中...</div>
            </div>
            <div id="btResult"></div>
        </div>

        <!-- Optimization Section -->
        <div id="optimize" class="section">
            <div class="card">
                <h2>参数优化</h2>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>股票代码</label>
                            <input type="text" id="optSymbol" value="AAPL">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>时间范围</label>
                            <select id="optRange">
                                <option value="1y" selected>1年</option>
                                <option value="2y">2年</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label>优化策略</label>
                    <select id="optStrategy">
                        <option value="sma_cross">均线交叉</option>
                        <option value="rsi_strategy">RSI策略</option>
                    </select>
                </div>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>参数1范围 (如 period=10-50)</label>
                            <input type="text" id="optParam1" value="10,20,30,40,50">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>参数2范围</label>
                            <input type="text" id="optParam2" value="20,30,40,60,90">
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label>优化目标</label>
                    <select id="optGoal">
                        <option value="sharperatio">夏普比率</option>
                        <option value="profit">收益率</option>
                        <option value="profitfactor">利润因子</option>
                    </select>
                </div>
                <button onclick="runOptimization()" id="optRunBtn">开始优化</button>
            </div>
            <div class="loading" id="optLoading">
                <div class="spinner"></div>
                <div>参数优化中，请稍候...</div>
            </div>
            <div id="optResult"></div>
        </div>

        <!-- Analyzers Section -->
        <div id="analyzers" class="section">
            <div class="card">
                <h2>分析器</h2>
                <div class="nav-tabs">
                    <button class="nav-tab active" onclick="showAnalyzerTab('summary')">概览</button>
                    <button class="nav-tab" onclick="showAnalyzerTab('trades')">交易分析</button>
                    <button class="nav-tab" onclick="showAnalyzerTab('returns')">收益分析</button>
                    <button class="nav-tab" onclick="showAnalyzerTab('risk')">风险分析</button>
                </div>
                <div id="analyzerSummary" class="tab-content active">
                    <p style="color:#888;">运行回测后查看分析结果</p>
                </div>
                <div id="analyzerTrades" class="tab-content">
                    <p style="color:#888;">运行回测后查看交易详情</p>
                </div>
                <div id="analyzerReturns" class="tab-content">
                    <p style="color:#888;">运行回测后查看收益分析</p>
                </div>
                <div id="analyzerRisk" class="tab-content">
                    <p style="color:#888;">运行回测后查看风险指标</p>
                </div>
            </div>
        </div>

        <!-- Strategies Section -->
        <div id="strategies" class="section">
            <div class="card">
                <h2>策略库</h2>
                <p style="color:#888; margin-bottom:16px;">点击一个策略模板查看详情并使用</p>
                <div class="strategy-template" onclick="loadStrategyTemplate('sma_cross')">
                    <h4>均线交叉策略</h4>
                    <p style="color:#888;font-size:0.85em;">短期均线与长期均线交叉时买入/卖出</p>
                </div>
                <div class="strategy-template" onclick="loadStrategyTemplate('rsi_strategy')">
                    <h4>RSI 策略</h4>
                    <p style="color:#888;font-size:0.85em;">RSI超卖时买入，超买时卖出</p>
                </div>
                <div class="strategy-template" onclick="loadStrategyTemplate('macd_cross')">
                    <h4>MACD 交叉策略</h4>
                    <p style="color:#888;font-size:0.85em;">MACD与信号线交叉时交易</p>
                </div>
                <div class="strategy-template" onclick="loadStrategyTemplate('bollinger_rsi')">
                    <h4>布林带 + RSI 策略</h4>
                    <p style="color:#888;font-size:0.85em;">结合布林带和RSI指标</p>
                </div>
            </div>
            <div class="card">
                <h2>策略代码预览</h2>
                <pre id="strategyPreview" style="min-height:200px;">选择一个策略模板查看代码</pre>
            </div>
        </div>
    </div>

    <div class="footer">
        Backtrader Web UI | Powered by Flask & backtrader
    </div>

<script>
// Utility functions
function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    document.getElementById(name).classList.add('active');
    event.target.classList.add('active');
}

function showAnalyzerTab(name) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
    document.getElementById('analyzer' + name.charAt(0).toUpperCase() + name.slice(1)).classList.add('active');
    event.target.classList.add('active');
}

function formatNumber(n, decimals=2) {
    if (n === null || n === undefined) return 'N/A';
    return Number(n).toFixed(decimals);
}

function formatDate(d) {
    return new Date(d).toLocaleDateString('zh-CN');
}

// API calls
async function apiCall(endpoint, data) {
    const res = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    return res.json();
}

// Data Viewer
async function loadData() {
    const symbol = document.getElementById('dataSymbol').value;
    const range = document.getElementById('dataRange').value;
    const result = await apiCall('/api/data', {symbol, range});

    if (result.error) {
        document.getElementById('dataTableBody').innerHTML = `<tr><td colspan="6" style="color:#ff4757;">${result.error}</td></tr>`;
        return;
    }

    const tbody = document.getElementById('dataTableBody');
    tbody.innerHTML = result.data.slice(0, 100).map(row => `
        <tr>
            <td>${formatDate(row.date)}</td>
            <td>${row.open.toFixed(2)}</td>
            <td>${row.high.toFixed(2)}</td>
            <td>${row.low.toFixed(2)}</td>
            <td>${row.close.toFixed(2)}</td>
            <td>${row.volume.toLocaleString()}</td>
        </tr>
    `).join('');

    const stats = document.getElementById('dataStats');
    stats.innerHTML = `
        <div class="metric"><div class="metric-value">${result.stats.count}</div><div class="metric-label">数据点数</div></div>
        <div class="metric"><div class="metric-value">$${formatNumber(result.stats.meanClose)}</div><div class="metric-label">平均收盘价</div></div>
        <div class="metric"><div class="metric-value">$${formatNumber(result.stats.maxHigh)}</div><div class="metric-label">最高价</div></div>
        <div class="metric"><div class="metric-value">$${formatNumber(result.stats.minLow)}</div><div class="metric-label">最低价</div></div>
    `;
}

// Indicators
async function calculateIndicator(type) {
    const symbol = document.getElementById('indSymbol').value;
    const range = document.getElementById('indRange').value;
    const result = await apiCall('/api/indicator', {symbol, range, type});

    if (result.error) {
        document.getElementById('indResult').innerHTML = `<div class="error">${result.error}</div>`;
        return;
    }

    document.getElementById('indResultTitle').textContent = `${type} 结果`;
    const container = document.getElementById('indResult');

    if (result.chart) {
        container.innerHTML = `<pre>${result.chart}</pre>`;
    } else {
        container.innerHTML = `<pre>${JSON.stringify(result.data, null, 2)}</pre>`;
    }
}

// Backtest
function onStrategyChange() {
    const strategy = document.getElementById('btStrategy').value;
    const customGroup = document.getElementById('customStrategyGroup');
    customGroup.style.display = strategy === 'custom' ? 'block' : 'none';
}

async function runBacktest() {
    const symbol = document.getElementById('btSymbol').value;
    const range = document.getElementById('btRange').value;
    const cash = parseFloat(document.getElementById('btCash').value);
    const strategy = document.getElementById('btStrategy').value;
    const customCode = document.getElementById('btCustomStrategy').value;

    document.getElementById('btLoading').classList.add('show');
    document.getElementById('btResult').innerHTML = '';

    const data = {symbol, range, cash, strategy: strategy || 'default'};
    if (strategy === 'custom') data.custom_code = customCode;

    const result = await apiCall('/api/backtest', data);

    document.getElementById('btLoading').classList.remove('show');

    if (result.error) {
        document.getElementById('btResult').innerHTML = `<div class="card"><div class="error">${result.error}</div></div>`;
        return;
    }

    displayBacktestResult(result);
    displayAnalyzerResults(result);
}

function displayBacktestResult(r) {
    const profit = r.profit;
    const profitClass = profit >= 0 ? 'profit' : 'loss';
    document.getElementById('btResult').innerHTML = `
        <div class="card">
            <h2>回测结果</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">$${formatNumber(r.final_value)}</div>
                    <div class="metric-label">最终价值</div>
                </div>
                <div class="metric">
                    <div class="metric-value ${profitClass}">${profit >= 0 ? '+' : ''}$${formatNumber(profit)}</div>
                    <div class="metric-label">收益</div>
                </div>
                <div class="metric">
                    <div class="metric-value ${profitClass}">${formatNumber(r.profit_pct)}%</div>
                    <div class="metric-label">收益率</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${formatNumber(r.analyzers.sharpe)}</div>
                    <div class="metric-label">夏普比率</div>
                </div>
            </div>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">${formatNumber(r.analyzers.max_drawdown_pct)}%</div>
                    <div class="metric-label">最大回撤</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${r.analyzers.total_trades || 0}</div>
                    <div class="metric-label">总交易</div>
                </div>
                <div class="metric">
                    <div class="metric-value" style="color:#00ff88">${r.analyzers.won_trades || 0}</div>
                    <div class="metric-label">盈利</div>
                </div>
                <div class="metric">
                    <div class="metric-value" style="color:#ff4757">${r.analyzers.lost_trades || 0}</div>
                    <div class="metric-label">亏损</div>
                </div>
            </div>
        </div>
    `;

    // Update recent results on dashboard
    document.getElementById('recentResults').innerHTML = `
        <div class="result-item">
            <strong>${document.getElementById('btSymbol').value}</strong> |
            最终: $${formatNumber(r.final_value)} |
            收益: <span class="${profitClass}">${profit >= 0 ? '+' : ''}$${formatNumber(profit)} (${formatNumber(r.profit_pct)}%)</span>
        </div>
    `;
}

function displayAnalyzerResults(r) {
    const a = r.analyzers;
    document.getElementById('analyzerSummary').innerHTML = `
        <div class="metrics">
            <div class="metric"><div class="metric-value">${formatNumber(r.profit_pct)}%</div><div class="metric-label">总收益率</div></div>
            <div class="metric"><div class="metric-value">${formatNumber(a.sharpe)}</div><div class="metric-label">夏普比率</div></div>
            <div class="metric"><div class="metric-value">${formatNumber(a.max_drawdown_pct)}%</div><div class="metric-label">最大回撤</div></div>
            <div class="metric"><div class="metric-value">${formatNumber(a.calmar || 0)}</div><div class="metric-label">Calmar比率</div></div>
        </div>
    `;

    document.getElementById('analyzerTrades').innerHTML = `
        <table>
            <tr><th>指标</th><th>数值</th></tr>
            <tr><td>总交易数</td><td>${a.total_trades || 0}</td></tr>
            <tr><td>盈利交易</td><td style="color:#00ff88">${a.won_trades || 0}</td></tr>
            <tr><td>亏损交易</td><td style="color:#ff4757">${a.lost_trades || 0}</td></tr>
            <tr><td>胜率</td><td>${a.win_rate || 0}%</td></tr>
            <tr><td>平均盈利</td><td>$${formatNumber(a.avg_win || 0)}</td></tr>
            <tr><td>平均亏损</td><td>$${formatNumber(a.avg_loss || 0)}</td></tr>
            <tr><td>利润因子</td><td>${formatNumber(a.profit_factor || 0)}</td></tr>
        </table>
    `;

    document.getElementById('analyzerReturns').innerHTML = `
        <table>
            <tr><th>指标</th><th>数值</th></tr>
            <tr><td>总收益率</td><td>${formatNumber(r.profit_pct)}%</td></tr>
            <tr><td>年化收益率</td><td>${formatNumber(a.annual_return || 0)}%</td></tr>
            <tr><td>日均收益率</td><td>${formatNumber(a.daily_return || 0)}%</td></tr>
            <tr><td>波动率</td><td>${formatNumber(a.volatility || 0)}%</td></tr>
        </table>
    `;

    document.getElementById('analyzerRisk').innerHTML = `
        <table>
            <tr><th>指标</th><th>数值</th></tr>
            <tr><td>最大回撤</td><td>${formatNumber(a.max_drawdown_pct)}%</td></tr>
            <tr><td>最大回撤持续时间</td><td>${a.max_drawdown_len || 0}天</td></tr>
            <tr><td>夏普比率</td><td>${formatNumber(a.sharpe)}</td></tr>
            <tr><td>Sortino比率</td><td>${formatNumber(a.sortino || 0)}</td></tr>
            <tr><td>Calmar比率</td><td>${formatNumber(a.calmar || 0)}</td></div></tr>
            <tr><td>VaR (95%)</td><td>${formatNumber(a.var || 0)}%</td></tr>
        </table>
    `;
}

// Optimization
async function runOptimization() {
    const symbol = document.getElementById('optSymbol').value;
    const range = document.getElementById('optRange').value;
    const strategy = document.getElementById('optStrategy').value;
    const param1 = document.getElementById('optParam1').value.split(',').map(Number);
    const param2 = document.getElementById('optParam2').value.split(',').map(Number);
    const goal = document.getElementById('optGoal').value;

    document.getElementById('optLoading').classList.add('show');
    document.getElementById('optResult').innerHTML = '';

    const result = await apiCall('/api/optimize', {symbol, range, strategy, param1, param2, goal});

    document.getElementById('optLoading').classList.remove('show');

    if (result.error) {
        document.getElementById('optResult').innerHTML = `<div class="card"><div class="error">${result.error}</div></div>`;
        return;
    }

    const best = result.results[0];
    let html = `<div class="card"><h2>优化结果 (共${result.results.length}组)</h2>`;
    html += `<div class="metrics" style="margin-bottom:16px;">
        <div class="metric"><div class="metric-value" style="color:#00ff88">${best.params[0]}</div><div class="metric-label">最优参数1</div></div>
        <div class="metric"><div class="metric-value" style="color:#00ff88">${best.params[1]}</div><div class="metric-label">最优参数2</div></div>
        <div class="metric"><div class="metric-value" style="color:#00ff88">${formatNumber(best.value)}</div><div class="metric-label">${goal}</div></div>
    </div>`;
    html += `<div class="optimization-results">`;

    result.results.forEach((r, i) => {
        html += `<div class="result-item ${i === 0 ? 'best' : ''}">
            参数: ${r.params} | 收益率: ${formatNumber(r.profit_pct)}% | 夏普: ${formatNumber(r.sharpe)} | 交易数: ${r.total_trades}
        </div>`;
    });

    html += `</div></div>`;
    document.getElementById('optResult').innerHTML = html;
}

// Strategy Templates
const strategyTemplates = {
    sma_cross: `class SmaCross(bt.SignalStrategy):
    params = dict(fast=10, slow=30)
    def __init__(self):
        sma_fast = bt.indicators.SMA(self.data.close, period=self.p.fast)
        sma_slow = bt.indicators.SMA(self.data.close, period=self.p.slow)
        crossover = bt.indicators.CrossOver(sma_fast, sma_slow)
        self.signal_add(bt.SIGNAL_LONG, crossover)`,

    rsi_strategy: `class RsiStrategy(bt.Strategy):
    params = dict(rsi_period=14, rsi_upper=70, rsi_lower=30)
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
    def next(self):
        if self.rsi < self.p.rsi_lower and not self.position:
            self.buy()
        elif self.rsi > self.p.rsi_upper and self.position:
            self.sell()`,

    macd_cross: `class MacdCross(bt.SignalStrategy):
    params = dict()
    def __init__(self):
        macd = bt.indicators.MACD()
        signal = bt.indicators.SignalAFactor(macd)
        crossover = bt.indicators.CrossOver(macd, signal)
        self.signal_add(bt.SIGNAL_LONG, crossover)`,

    bollinger_rsi: `class BollingerRsiStrategy(bt.Strategy):
    params = dict(period=20, dev=2, rsi_period=14)
    def __init__(self):
        self.boll = bt.indicators.BollingerBands(self.data.close, period=self.p.period, devfactor=self.p.dev)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
    def next(self):
        if self.data.close < self.boll.lines.bot and self.rsi < 30 and not self.position:
            self.buy()
        elif self.data.close > self.boll.lines.top and self.rsi > 70 and self.position:
            self.sell()`
};

function loadStrategyTemplate(name) {
    const template = strategyTemplates[name];
    if (!template) return;

    document.getElementById('strategyPreview').textContent = template;

    // Fill backtest form
    document.getElementById('btStrategy').value = 'custom';
    document.getElementById('btCustomStrategy').value = template;
    document.getElementById('customStrategyGroup').style.display = 'block';

    showSection('backtest');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load recent data for dashboard
    loadData();
});
</script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/data', methods=['POST'])
def get_data():
    """Get historical OHLCV data"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL')
        period = data.get('range', '1y')

        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 400

        ohlcv = []
        for idx, row in hist.iterrows():
            ohlcv.append({
                'date': idx.isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })

        stats = {
            'count': len(ohlcv),
            'meanClose': sum(d['close'] for d in ohlcv) / len(ohlcv),
            'maxHigh': max(d['high'] for d in ohlcv),
            'minLow': min(d['low'] for d in ohlcv)
        }

        return jsonify({'data': ohlcv, 'stats': stats})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/indicator', methods=['POST'])
def calculate_indicator():
    """Calculate technical indicators"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL')
        period = data.get('range', '1y')
        ind_type = data.get('type', 'SMA')

        import yfinance as yf
        import backtrader as bt

        # Download data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            return jsonify({'error': f'No data for {symbol}'}), 400

        # Create Cerebro
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data_feed)

        # Calculate indicator based on type
        if ind_type == 'SMA':
            cerebro.addindicator('SMA20', bt.indicators.SMA, period=20)
            cerebro.addindicator('SMA50', bt.indicators.SMA, period=50)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'EMA':
            cerebro.addindicator('EMA12', bt.indicators.EMA, period=12)
            cerebro.addindicator('EMA26', bt.indicators.EMA, period=26)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'RSI':
            cerebro.addindicator('RSI', bt.indicators.RSI, period=14)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'MACD':
            cerebro.addindicator('MACD', bt.indicators.MACD)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'BBANDS':
            cerebro.addindicator('BBANDS', bt.indicators.BollingerBands, period=20)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'STOCH':
            cerebro.addindicator('STOCH', bt.indicators.Stochastic)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'ATR':
            cerebro.addindicator('ATR', bt.indicators.ATR, period=14)
            cerebro.addstrategy(bt.Strategy)

        elif ind_type == 'ADX':
            cerebro.addindicator('ADX', bt.indicators.ADX, period=14)
            cerebro.addstrategy(bt.Strategy)

        results = cerebro.run()
        strategy = results[0]

        # Build chart data
        lines = []
        for name in dir(strategy):
            if not name.startswith('_'):
                obj = getattr(strategy, name)
                if hasattr(obj, '__len__') and hasattr(obj, 'lines'):
                    lines.append(name)

        chart = f"Indicator: {ind_type}\n"
        chart += f"Symbol: {symbol}\n"
        chart += f"Data points: {len(df)}\n"
        chart += f"Indicators found: {', '.join(lines) if lines else 'None'}\n"
        chart += "\nLast values:\n"

        for line_name in lines[:5]:
            obj = getattr(strategy, line_name)
            if hasattr(obj, 'lines'):
                for i in range(min(3, len(obj.lines[0]))):
                    chart += f"  {line_name}[-{i}]: {obj.lines[0][-i-1]:.4f}\n"

        return jsonify({'data': {'type': ind_type, 'symbol': symbol}, 'chart': chart})

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL')
        period = data.get('range', '2y')
        cash = data.get('cash', 10000)
        strategy_name = data.get('strategy', 'default')
        custom_code = data.get('custom_code')

        import yfinance as yf
        import backtrader as bt
        from datetime import datetime

        # Get ticker info for date calculation
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        if period == '1y': start_date = datetime(end_date.year - 1, end_date.month, end_date.day)
        elif period == '2y': start_date = datetime(end_date.year - 2, end_date.month, end_date.day)
        elif period == '5y': start_date = datetime(end_date.year - 5, end_date.month, end_date.day)
        else: start_date = datetime(end_date.year - 1, end_date.month, end_date.day)

        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            return jsonify({'error': f'No data for {symbol}'}), 400

        cerebro = bt.Cerebro()
        cerebro.broker.set_cash(cash)
        data_feed = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data_feed)

        # Select strategy
        if strategy_name == 'sma_cross' or custom_code and 'SMA' in custom_code.upper():
            strategy_code = custom_code or '''class SmaCross(bt.SignalStrategy):
    params = dict(fast=10, slow=30)
    def __init__(self):
        sma_fast = bt.indicators.SMA(self.data.close, period=self.p.fast)
        sma_slow = bt.indicators.SMA(self.data.close, period=self.p.slow)
        crossover = bt.indicators.CrossOver(sma_fast, sma_slow)
        self.signal_add(bt.SIGNAL_LONG, crossover)'''
        elif strategy_name == 'rsi_strategy':
            strategy_code = custom_code or '''class RsiStrategy(bt.Strategy):
    params = dict(rsi_period=14, rsi_upper=70, rsi_lower=30)
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
    def next(self):
        if self.rsi < self.p.rsi_lower and not self.position:
            self.buy()
        elif self.rsi > self.p.rsi_upper and self.position:
            self.sell()'''
        elif strategy_name == 'macd_cross':
            strategy_code = custom_code or '''class MacdCross(bt.SignalStrategy):
    def __init__(self):
        macd = bt.indicators.MACD()
        signal = bt.indicators.SignalAFactor(macd)
        crossover = bt.indicators.CrossOver(macd, signal)
        self.signal_add(bt.SIGNAL_LONG, crossover)'''
        else:
            strategy_code = custom_code or None

        # Compile strategy
        if strategy_code:
            compiled = compile(strategy_code, '<strategy>', 'exec')
            strategy_globals = {'bt': bt}
            exec(compiled, strategy_globals)
            for key, obj in strategy_globals.items():
                if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                    cerebro.addstrategy(obj)
                    break
            else:
                cerebro.addstrategy(bt.Strategy)
        else:
            cerebro.addstrategy(bt.Strategy)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Calmar, _name='calmar')

        results = cerebro.run()
        strategy = results[0]

        sharpe = strategy.analyzers.sharpe.get_analysis()
        drawdown = strategy.analyzers.drawdown.get_analysis()
        returns = strategy.analyzers.returns.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()
        calmar = strategy.analyzers.calmar.get_analysis()

        final_value = cerebro.broker.getvalue()
        profit = final_value - cash

        won = trades.get('won', {}).get('total', 0)
        lost = trades.get('lost', {}).get('total', 0)
        total = won + lost
        win_rate = (won / total * 100) if total > 0 else 0

        avg_win = trades.get('won', {}).get('pnl', {}).get('average', 0) or 0
        avg_loss = abs(trades.get('lost', {}).get('pnl', {}).get('average', 0) or 0)
        profit_factor = (avg_win * won / avg_loss) if avg_loss > 0 else 0

        return jsonify({
            'status': 'success',
            'final_value': final_value,
            'cash': cerebro.broker.get_cash(),
            'profit': profit,
            'profit_pct': (profit / cash) * 100,
            'analyzers': {
                'sharpe': sharpe.get('sharperatio', None),
                'max_drawdown': drawdown.get('max', {}).get('drawdown', None),
                'max_drawdown_pct': drawdown.get('max', {}).get('drawdownpercent', None),
                'total_trades': total,
                'won_trades': won,
                'lost_trades': lost,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'annual_return': returns.get('rnorm100', None),
                'daily_return': returns.get('rnorm', None),
                'calmar': calmar.get('calmar', None) if isinstance(calmar, dict) else None,
            }
        })

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_strategy():
    """Optimize strategy parameters"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL')
        period = data.get('range', '1y')
        strategy_name = data.get('strategy', 'sma_cross')
        param1_values = data.get('param1', [10, 20, 30])
        param2_values = data.get('param2', [20, 40, 60])
        goal = data.get('goal', 'sharperatio')

        import yfinance as yf
        import backtrader as bt
        from datetime import datetime

        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        if period == '1y': start_date = datetime(end_date.year - 1, end_date.month, end_date.day)
        elif period == '2y': start_date = datetime(end_date.year - 2, end_date.month, end_date.day)
        else: start_date = datetime(end_date.year - 1, end_date.month, end_date.day)

        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            return jsonify({'error': f'No data for {symbol}'}), 400

        results = []
        cash = 10000

        for p1 in param1_values:
            for p2 in param2_values:
                if p2 <= p1:
                    continue

                cerebro = bt.Cerebro()
                cerebro.broker.set_cash(cash)
                data_feed = bt.feeds.PandasData(dataname=df)
                cerebro.adddata(data_feed)

                if strategy_name == 'sma_cross':
                    cerebro.addstrategy(bt.SignalStrategy)
                    # Add SMA indicator
                    sma_fast = bt.indicators.SMA(df['close'], period=p1)
                    sma_slow = bt.indicators.SMA(df['close'], period=p2)
                    # Would need custom strategy for proper optimization

                cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
                cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

                try:
                    backtest_results = cerebro.run()
                    strategy = backtest_results[0]

                    sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0) or 0
                    trades = strategy.analyzers.trades.get_analysis()
                    final_value = cerebro.broker.getvalue()
                    profit = final_value - cash

                    won = trades.get('won', {}).get('total', 0)
                    lost = trades.get('lost', {}).get('total', 0)

                    results.append({
                        'params': [p1, p2],
                        'sharpe': sharpe,
                        'profit': profit,
                        'profit_pct': (profit / cash) * 100,
                        'total_trades': won + lost,
                        'value': sharpe if goal == 'sharperatio' else (profit / cash * 100 if goal == 'profit' else 0)
                    })
                except:
                    results.append({
                        'params': [p1, p2],
                        'sharpe': 0,
                        'profit': 0,
                        'profit_pct': 0,
                        'total_trades': 0,
                        'value': 0
                    })

        # Sort by goal
        results.sort(key=lambda x: x['value'] if x['value'] is not None else 0, reverse=True)

        return jsonify({'results': results[:50]})

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
