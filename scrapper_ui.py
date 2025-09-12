import streamlit as st  
from product_assistant.etl.data_scrapper import FlipkartScraper
import pandas as pd
import os

flipkart_scraper = FlipkartScraper()
output_path="data/product_reviews.csv"

st.title("📦 Product Review Scraper")

if "product_inputs" not in st.session_state:
    st.session_state.product_inputs = [""]

def add_product_input():
    st.session_state.product_inputs.append("")

st.subheader("🛒 Product Names")
updated_input=[]
for i, product in enumerate(st.session_state.product_inputs):
    new_product = st.text_input(f"Product {i+1}", value=product, key=f"product_{i}")
    updated_input.append(new_product)
st.session_state.product_inputs = updated_input


st.button("➕ Add Another Product", on_click=add_product_input)
max_products = st.number_input("How many products per search?", min_value=1, max_value=10, value=1)
review_count = st.number_input("How many reviews per product?", min_value=1, max_value=10, value=2)

if isinstance(st.session_state.product_inputs, list):
    df = pd.DataFrame(st.session_state.product_inputs,columns=["Queried_Product"])
    st.dataframe(df, use_container_width=True)

if st.button("🚀 Scrape Reviews"):
    product_input = [p.strip() for p in st.session_state.product_inputs if p.strip()]
    if not product_input:
        st.warning("⚠️ Please enter at least one product name or a product description.")

    else:
        final_data=[]
        for query in product_input:
            st.write(f"Scraping reviews for: **{query}**")
            result= flipkart_scraper.scrape_flipkart_products(search_query=query, 
                                                              max_product=max_products, 
                                                              max_review=review_count)
            final_data.extend(result)

        unique_product_list={}
        for item in final_data:
            if item[1] not in unique_product_list:
                unique_product_list[item[1]]=item

        final_data=list(unique_product_list.values())
        st.session_state["scraped_data"]=final_data
        flipkart_scraper.save_to_csv(final_data,output_path)
        st.success("✅ Data saved to `data/product_reviews.csv`")
        st.download_button("📥 Download CSV", data=open(output_path, "rb"), file_name="product_reviews.csv")


    
    