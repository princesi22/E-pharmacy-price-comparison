

import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import re

st.set_page_config(page_title="E-Pharmacy Price Comparison", layout="wide")

# ================= HEADER =================
c1, c2 = st.columns([1, 5])
with c1:
    st.image("e_pharmacy.png", width=120)
with c2:
    st.title("💊 E-Pharmacy Price Comparison")

st.divider()

# ================= SIDEBAR =================
st.sidebar.title("Search Medicine")
med_name = st.sidebar.text_input("Enter medicine name")
number = st.sidebar.number_input("Number of options", 1, 10, 5)
search_btn = st.sidebar.button("Compare Prices")

# ================= API FUNCTION =================
def fetch_results(medicine):
    params = {
        "engine": "google_shopping",
        "q": medicine,
        "api_key": "dfcec42572c150565a8175261921e161d787275288fa2840400d806860103aed",  # replace
        "gl": "in",
        "hl": "en"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("shopping_results", [])

# ================= PRICE CLEANER =================
def extract_price(price_text):
    if not price_text:
        return None
    nums = re.findall(r"\d+\.?\d*", price_text.replace(",", ""))
    return float(nums[0]) if nums else None

# ================= MAIN =================
if search_btn and med_name:
    results = fetch_results(med_name)

    if results:
        st.success(f"Top {number} results for '{med_name}'")

        data = []

        # Collect structured data
        for item in results[:number]:
            title = item.get("title")
            price = item.get("price")
            store = item.get("source")

            numeric_price = extract_price(price)

            link = (
                item.get("product_link") or
                item.get("serpapi_product_api") or
                item.get("link")
            )

            image = item.get("thumbnail") or item.get("image")

            data.append({
                "Title": title,
                "Store": store,
                "Price": price,
                "Numeric": numeric_price,
                "Link": link,
                "Image": image
            })

        df = pd.DataFrame(data)

        # ================= BEST OPTION =================
        best = df[df["Numeric"] == df["Numeric"].min()].iloc[0]

        st.header("🏆 Best Price Option")
        col1, col2 = st.columns([1, 3])

        with col1:
            if best["Image"]:
                st.image(best["Image"], width=150)

        with col2:
            st.success(f"Cheapest: {best['Price']}")
            st.write(f"**Store:** {best['Store']}")
            st.write(f"**Title:** {best['Title']}")

            if best["Link"]:
                st.markdown(
                    f'<a href="{best["Link"]}" target="_blank">🛒 Buy Cheapest</a>',
                    unsafe_allow_html=True
                )

        st.divider()

        # ================= ALL OPTIONS =================
        st.header("📦 All Options")

        for i, row in df.iterrows():
            st.subheader(f"Option {i+1}")
            c1, c2 = st.columns([1, 3])

            with c1:
                if row["Image"]:
                    st.image(row["Image"], width=130)

            with c2:
                st.write(f"**Store:** {row['Store']}")
                st.write(f"**Title:** {row['Title']}")
                st.write(f"**Price:** {row['Price']}")

                if row["Link"]:
                    st.markdown(
                        f'<a href="{row["Link"]}" target="_blank">Buy Now</a>',
                        unsafe_allow_html=True
                    )
            st.divider()

        # ================= BAR CHART =================
        st.header("📊 Price Comparison Chart")

        chart_df = df.dropna(subset=["Numeric"])
        chart_df = chart_df.sort_values("Numeric")

        st.bar_chart(
            data=chart_df.set_index("Store")["Numeric"]
        )

    else:
        st.error("No results found")
