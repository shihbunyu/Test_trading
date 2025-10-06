import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from trading_strategy import get_stock_data, calculate_moving_averages, identify_golden_cross, implement_strategy, analyze_results

st.set_page_config(page_title="Golden Cross Trading Strategy", layout="wide")

# Get and process data
@st.cache_data
def load_data():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    positions = implement_strategy(data)
    return data, positions

data, positions = load_data()

# Calculate statistics
if not positions.empty:
    total_trades = len(positions)
    win_trades = len(positions[positions['ProfitPct'] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0
    avg_profit = positions['ProfitPct'].mean()
    avg_win = positions[positions['ProfitPct'] > 0]['ProfitPct'].mean() if win_trades > 0 else 0
    avg_loss = positions[positions['ProfitPct'] <= 0]['ProfitPct'].mean() if loss_trades > 0 else 0
    avg_holding = positions['HoldingDays'].mean()
    target_reached = len(positions[positions['SellReason'] == 'Target reached'])
    max_period = len(positions[positions['SellReason'] == 'Max holding period'])
else:
    total_trades = win_trades = loss_trades = win_rate = avg_profit = avg_win = avg_loss = avg_holding = target_reached = max_period = 0

# Sidebar navigation
page = st.sidebar.radio("Select Page", ["Price Chart", "Trade Statistics", "Detailed Trades"])

if page == "Price Chart":
    st.title("Price Chart with Golden Cross Signals")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='MA50'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], mode='lines', name='MA200'))
    # Buy and sell points
    if not positions.empty:
        fig.add_trace(go.Scatter(x=positions['BuyDate'], y=positions['BuyPrice'], mode='markers', name='Buy', marker=dict(color='green', size=10, symbol='circle')))
        fig.add_trace(go.Scatter(x=positions['SellDate'], y=positions['SellPrice'], mode='markers', name='Sell', marker=dict(color='red', size=10, symbol='x')))
    fig.update_layout(height=600, width=1100, xaxis_title='Date', yaxis_title='Price (USD)')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Trade Statistics":
    st.title("Trade Statistics Summary")
    st.markdown(f"**Total Trades:** {total_trades}")
    st.markdown(f"**Winning Trades:** {win_trades} ({win_rate:.2f}%)")
    st.markdown(f"**Losing Trades:** {loss_trades}")
    st.markdown(f"**Average Profit:** {avg_profit:.2f}%")
    st.markdown(f"**Average Win:** {avg_win:.2f}%")
    st.markdown(f"**Average Loss:** {avg_loss:.2f}%")
    st.markdown(f"**Average Holding Period:** {avg_holding:.2f} days")
    st.markdown(f"**Target Reached Sells:** {target_reached}")
    st.markdown(f"**Max Holding Period Sells:** {max_period}")

elif page == "Detailed Trades":
    st.title("Detailed Trades Record")
    if not positions.empty:
        st.dataframe(positions)
    else:
        st.write("No trades to display.")
