import os
import sys
import logging
import streamlit as st

print("Starting dashboard application...")  # Print statement for immediate feedback

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.info("Dashboard application initialized")

def main():
    """Simple Streamlit dashboard"""
    try:
        logging.info("Starting main function")

        # Basic page config
        st.set_page_config(
            page_title="نظام التداول الآلي",
            layout="wide"
        )
        logging.info("Page config set")

        # Simple header
        st.title("نظام التداول الآلي")
        st.write("مرحباً بك في نظام التداول")

        # إضافة قائمة جانبية بسيطة
        with st.sidebar:
            st.header("قائمة العملات")
            selected_symbol = st.selectbox(
                "اختر العملة",
                ["BTCUSDT", "ETHUSDT"]
            )

            trading_mode = st.radio(
                "نوع التداول",
                ["تداول آلي", "تداول يدوي"]
            )

        # عرض معلومات بسيطة
        st.subheader(f"تحليل {selected_symbol}")
        st.write("جاري تحميل البيانات...")

        logging.info("Basic UI elements rendered")

    except Exception as e:
        logging.error(f"Error in main function: {e}")
        st.error("حدث خطأ في تشغيل التطبيق")

if __name__ == "__main__":
    try:
        logging.info("Starting application")
        main()
        logging.info("Application started successfully")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)