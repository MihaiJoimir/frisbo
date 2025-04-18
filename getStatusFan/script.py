import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_tracking_status(tracking_number):
    url = f"https://www.fancourier.ro/awb-tracking/?tracking={tracking_number}"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        time.sleep(3)  # Allow time for the page to load
        
        # Corrected XPath to specifically target the shipment status span
        status_element = driver.find_element(By.XPATH, "//p[@class='whitecol'][span[contains(text(), 'Status expediție:')]]/span[last()]")
        status = status_element.text.strip()
    except Exception as e:
        print(f"Error fetching status for {tracking_number}: {e}")
        status = "Error"
    finally:
        driver.quit()
    
    return status

def main(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    
    # Assuming first two columns are the ones to keep
    df['shipment_status'] = ""
    
    for index, row in df.iterrows():
        time.sleep(1)  # Delay between requests
        df.at[index, 'shipment_status'] = get_tracking_status(row['shipping_tracking_number'])
        
        # Save progress after each crawl
        df.iloc[:, [0, 1, -1]].to_csv(output_csv, index=False)
        print(f"Updated entry {index+1}/{len(df)} saved to {output_csv}")

if __name__ == "__main__":
    input_file = "input.csv"
    output_file = "output.csv"
    main(input_file, output_file)
