import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List
import logging
from config import Config
from trading.trade_manager import TradeManager

class Dashboard:
    def __init__(self, trade_manager: TradeManager):
        self.trade_manager = trade_manager
        st.set_page_config(
            page_title="نظام التداول الآلي",
            layout="wide"
        )

    def render_main_page(self, ranked_pairs: List[Dict]):
        """عرض الصفحة الرئيسية"""
        st.title("نظام التداول الآلي الذكي")

        # القائمة الجانبية
        with st.sidebar:
            st.header("قائمة العملات")
            selected_symbol = st.selectbox(
                "اختر العملة",
                [pair['symbol'] for pair in ranked_pairs]
            )

            # خيار نوع التداول
            trading_mode = st.radio(
                "نوع التداول",
                ["تداول آلي", "تداول يدوي"]
            )

        # عرض معلومات العملة المختارة
        selected_data = next(
            (pair for pair in ranked_pairs if pair['symbol'] == selected_symbol),
            None
        )

        if selected_data:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader(f"تحليل {selected_symbol}")
                self._render_price_chart(selected_data)

            with col2:
                self._render_analysis_details(selected_data)

            if trading_mode == "تداول يدوي":
                self._render_manual_trading_controls(selected_data)

    def _render_price_chart(self, data: Dict):
        """عرض الرسم البياني للسعر"""
        df = data['market_data']

        fig = go.Figure(data=[
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        ])

        fig.update_layout(
            title=f"سعر {data['symbol']}",
            yaxis_title="السعر",
            xaxis_title="التاريخ"
        )

        st.plotly_chart(fig, use_container_width=True)

        if data.get('ml_prediction'):
            self._render_prediction_chart(df, data['ml_prediction'])

    def _render_prediction_chart(self, df: pd.DataFrame, prediction: float):
        """عرض رسم التوقعات"""
        last_prices = df['close'].tail(30)
        dates = pd.date_range(
            start=last_prices.index[-1],
            periods=2,
            freq='H'
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=last_prices.index,
            y=last_prices,
            name="السعر الحالي"
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=[last_prices.iloc[-1], prediction],
            name="التوقع",
            line=dict(dash='dash')
        ))

        fig.update_layout(
            title="توقع السعر",
            yaxis_title="السعر",
            xaxis_title="التاريخ"
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_analysis_details(self, data: Dict):
        """عرض تفاصيل التحليل"""
        st.subheader("تفاصيل التحليل")

        # المؤشرات الفنية
        tech_analysis = data['strategy_analysis']
        st.write("التحليل الفني:")
        st.write(f"- نوع الاتجاه: {tech_analysis.get('trend', 'غير محدد')}")
        st.write(f"- قوة الإشارة: {tech_analysis.get('signal_strength', 0):.2f}")

        # تحليل الأخبار
        news = data['news_sentiment']
        st.write("تحليل الأخبار:")
        st.write(f"- التوجه: {news.get('sentiment', 'محايد')}")
        st.write(f"- درجة الثقة: {news.get('confidence', 0):.2f}")

        # توقع التعلم الآلي
        if data.get('ml_prediction'):
            st.write("توقع التعلم الآلي:")
            current_price = data['current_price']
            predicted_price = data['ml_prediction']
            change = ((predicted_price - current_price) / current_price) * 100
            st.write(f"- السعر المتوقع: {predicted_price:.2f}")
            st.write(f"- نسبة التغير المتوقعة: {change:.2f}%")

    def _render_manual_trading_controls(self, data: Dict):
        """عرض أدوات التداول اليدوي"""
        st.subheader("التداول اليدوي")

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "كمية التداول",
                min_value=0.0,
                step=0.01
            )

        with col2:
            available_balance = 10000  # يجب جلبه من الحساب
            st.write(f"الرصيد المتاح: {available_balance} USDT")

        if st.button("شراء"):
            if amount > 0:
                # تنفيذ أمر الشراء
                order = self.trade_manager.place_limit_order(
                    data['symbol'],
                    "BUY",
                    amount,
                    data['current_price']
                )
                if order:
                    st.success("تم تنفيذ أمر الشراء بنجاح")
                else:
                    st.error("فشل تنفيذ أمر الشراء")
            else:
                st.warning("يرجى إدخال كمية صحيحة")

        if st.button("بيع"):
            if amount > 0:
                # تنفيذ أمر البيع
                order = self.trade_manager.place_limit_order(
                    data['symbol'],
                    "SELL",
                    amount,
                    data['current_price']
                )
                if order:
                    st.success("تم تنفيذ أمر البيع بنجاح")
                else:
                    st.error("فشل تنفيذ أمر البيع")
            else:
                st.warning("يرجى إدخال كمية صحيحة")