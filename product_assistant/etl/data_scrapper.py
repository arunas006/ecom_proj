import csv
import os
import time
import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class FlipkartScraper:
    
    def __init__(self,output_dir="data"):
        self.output_dir=output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_flipkart_products(self,search_query="laptop",max_product=1,max_review=2):

        options=uc.ChromeOptions()
        driver=uc.Chrome(options=options,use_subprocess=True)
        search_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(5)

        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
        except Exception as e:
            print("No login popup found or error closing it:", e)

        time.sleep(2)
        products=[]

        items=driver.find_elements(By.CSS_SELECTOR,"div[data-id]")[:max_product]
        for item in items:
            try:
                title=item.find_element(By.CSS_SELECTOR,"div.KzDlHZ").text.strip()
                price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text.strip()
                rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
                reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0) if match else "N/A"

                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"
            except Exception as e:
                print(f"Error occurred while processing item: {e}")
                continue

            top_reviews = self.get_top_reviews(product_link, count=max_review) if "flipkart.com" in product_link else "Invalid product URL"
            products.append([product_id, title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products
    
    def get_top_reviews(self,product_url,count=2):

        options=uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options,use_subprocess=True)
        

        if not product_url.startswith("http"):
            return "Invalid product URL"
        
        try:
            driver.get(product_url)
            time.sleep(5)
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
            except Exception as e:
                print("No login popup found or error closing it:", e)

            for _ in range(4):
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(2)

            soup=BeautifulSoup(driver.page_source, 'html.parser')
            review_elements = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")
            seen=set()
            reviews=[]

            for block in review_elements:
                text = block.get_text(separator=" ", strip=True)
                if text and text not in seen:
                    seen.add(text)
                    reviews.append(text)

                if len(reviews) >= count:
                    break
        except Exception as e:
            reviews = []
        
        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"
    
              
    def save_to_csv(self,data,filename="flipkart_products.csv"):
        if os.path.abspath(filename):
            filepath=filename
        elif os.path.dirname(filename):
            filepath=filename
            os.makedirs(os.path.dirname(filepath),exist_ok=True)
        else:
            filepath=os.path.join(self.output_dir,filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
            writer.writerows(data)
                