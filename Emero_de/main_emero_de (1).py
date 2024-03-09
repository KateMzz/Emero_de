import time
from urllib.request import urlretrieve

from scrapy.selector import Selector
import csv
# //////
import re
import urllib3
import json
from seleniumbase import Driver
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from datetime import datetime
#from playwright.sync_api import sync_playwright, Playwright


class EmEro_De():
    count = 0
    output_data = []

    def start(self):
        self.driver = Driver(uc=True)



    # def fetch_package(self):
    # """
    # Downloads ChromeDriver from source
    #
    # :return: path to downloaded file
    # """
    # zip_name = f"chromedriver_{self.platform_name}.zip"
    # if self.is_old_chromedriver:
    #     download_url = "%s/%s/%s" % (self.url_repo, self.version_full.vstring, zip_name)
    # else:
    #     zip_name = zip_name.replace("_", "-", 1)
    #     #download_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/%s/%s/%s"
    #     download_url = "https://storage.googleapis.com/chrome-for-testing-public/%s/%s/%s"
    #     download_url %= (self.version_full.vstring, self.platform_name, zip_name)
    #
    # logger.debug("downloading from %s" % download_url)
    # return urlretrieve(download_url)[0]

    # def start(self):
    #     options = Options()
    #     options.add_experimental_option("detach", True)
    #     options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    #     #options.add_argument("--headless")
    #     # options.add_argument("--no-sandbox")
    #     # options.add_argument('--disable-gpu')
    #     # prefs = {
    #     #     'download.default_directory': download_directory,
    #     #     'download.prompt_for_download': False,
    #     #     'download.directory_upgrade': True,
    #     #     'safebrowsing.enabled': False
    #     # }


    #     # options.add_experimental_option('prefs', prefs)
    #     options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')
    #     options.add_argument("user-data-dir=C:/Users/GNG/AppData/Local/Google/Chrome/User Data")
    #     options.add_argument("profile-directory=Profile 1")
    #     options.add_argument("start-maximized")
    #     options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #     options.add_experimental_option('useAutomationExtension', False)
    #     options.add_argument("--disable-blink-features=AutomationControlled")
    #     self.driver = webdriver.Chrome(options=options)
    
    links = {}
    
    def target_url(self, url):
        self.start()
        print("Main_links", url)
        self.driver.open(url)
        time.sleep(10)  

        html = self.driver.page_source
        resp = Selector(text=html)
        all_catagoery_links = resp.xpath("//li[contains(@class,'c-megamenu__item is-dropdown-submenu-parent opens-right')]/a/@href").getall()
        for all_link in all_catagoery_links:
            all_link = "https://www.emero.de" + str(all_link)
            if "brands" not in all_link:
                print("Current Scraping Url",all_link)
                self.next_page(all_link)
                self.extract_sub_categories(all_link)

    def extract_sub_categories(self, url):
        match = re.search(r'\/([A-Za-z0-9-]*)\.html', str(url))
        name = match.group(1)
        name = name.replace('-', ' ').title()
        print("Extracted Main Links", url)
        print("Extracted Main Links Name", name)
        
        if not self.links:
            self.links[name] = url
            self.driver.open(url)       
            time.sleep(5)
        elif url not in self.links.values():
            self.links[name] = url
            self.driver.open(url)
            time.sleep(5)

        html = self.driver.page_source
        resp = Selector(text=html)
        all_category_links = resp.xpath('//a[@class="c-category-menu__item-default"]/@href').getall()
        for all_link in all_category_links:
            match = re.search(r'\/([A-Za-z0-9-]*)\.html', str(all_link))
            name = match.group(1)
            name = name.replace('-', ' ').title()
            all_link = "https://www.emero.de" + str(all_link)
            print("Extracted Subcategory Links", all_link)
            
            # if not self.links or all_link not in self.links.values(): 
            if all_link not in self.links.values(): 
                self.links[name] = all_link
                self.extract_sub_categories(all_link)
        
    
    def save_links_to_csv(self):
        with open("../../catagories.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Link'])
            for name, link in self.links.items():
                writer.writerow([name, link])


    def next_page(self,all_links):
        self.driver.open(all_links)
        time.sleep(5)
        html = self.driver.page_source
        resp = Selector(text=html)
        self.link_scrap(resp)
        
        next_button = resp.xpath('//a[@class="c-ajax-pagination__next "]/@href').extract_first()
        print()
        print("Next Button",next_button)
        print()
        if next_button:
            next_button = "https://www.emero.de"+str(next_button).strip()
            self.next_page(next_button)

    def link_scrap(self,resp):
        product_links = resp.xpath('//a[@class="c-product-tile__link"]/@href').getall()
        for pro in product_links:
            pro = "https://www.emero.de"+str(pro)
            print("Saving Link: ",pro)
            with open("../../Emero_de_links.csv", 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([pro])
        
    def run_main(self):
        
        link = "https://www.emero.de/en/evineo-ineo-illuminated-mirror-touchless-w-70-cm-a974198.php"
        with open("Emero_de_links.csv", 'r') as input_file:
            reader = csv.reader(input_file,delimiter=",")
            for i in reader:
                link = i[0]
                print("Curently Scraping: ",link)
                self.start()  
                self.driver.open(link)
                time.sleep(5)
                self.scrap(link)

    

    def scrap(self, link):
        html = self.driver.page_source
        resp = Selector(text=html)
        name = resp.xpath('normalize-space(//h1/span/text())').extract_first()
        brand = resp.xpath('normalize-space(//div[@id="js-product"]/@data-manufacturer-name)').extract_first()
        externalId = link
        description = resp.xpath('//div[@id="product_details"]//div[@class="small-12  small-order-2 large-order-1 columns"]/div[@class="o-pseudo-h3 margin-bottom-2" or@class="margin-bottom-2 margin-top-1"]//text()').getall()
        description = [item.strip() for item in description if item.strip()]
        description = ''.join(description).strip()
        # en = {}
        # de = {}
        
        rubrics = []
        variations_en = []
        specification = {}
        parent_url = None
        breadcrumb = resp.xpath('//li[@class="c-breadcrumb__item show-for-medium"]/span[@property="itemListElement"]/a/span')
        for bd in breadcrumb:
            breadcrumb_name = bd.xpath('.//text()').extract_first()
            breadcrumb_url = bd.xpath('.//parent::a/@href').extract_first()
            if parent_url is not None:
                rubrics.append({"id": breadcrumb_url, "name": breadcrumb_name, "parentId": parent_url})
            else:
                rubrics.append({"id": breadcrumb_url, "name": breadcrumb_name, "parentId": None})
            parent_url = breadcrumb_url

        # keys = resp.xpath('//div[@class="c-details-block__text-column c-details-block__text-column--title columns small-6"]')
        # for key in keys:
        #     key_name = key.xpath('normalize-space(.//text())').extract_first()
        #     key_value = key.xpath('normalize-space(.//following-sibling::div/div/span/text())').extract_first()
        #     en[key_name] = key_value

        sku = resp.xpath('normalize-space(//div[@id="js-product"]/@data-sku)').extract_first()
        # parent_sku = resp.xpath('normalize-space(//div[@id="js-product"]/@data-parent-nav-id)').extract_first()

        specs = resp.xpath('//dl[@class="c-definition-list c-definition-list--light column"]')
        for spec in specs:
            key = spec.xpath('normalize-space(.//dt/text())').extract_first()
            value = spec.xpath('normalize-space(.//dd/text())').extract_first()
            specification[key] = value

        item_number = resp.xpath('normalize-space(//div[@id="js-product"]/@data-art-id)').extract_first()
        color = resp.xpath(
            'normalize-space(//div[contains(text(),"Colour:")]/following-sibling::div//span/text())'
        ).extract_first()

        if not color:
            color = resp.xpath(
                'normalize-space(//div[contains(text(),"Colour")]/following-sibling::div//span/text())'
            ).extract_first()

        active_price = resp.xpath('normalize-space(//div[@id="js-product"]/@data-price)').extract_first()
        regular_price_dollar = resp.xpath(
            'normalize-space(//strike[@class="c-price-block__price--strikethrough"]/text()[1])'
        ).extract_first()
        if regular_price_dollar:
            regular_price_cents = resp.xpath(
                'normalize-space(//strike[@class="c-price-block__price--strikethrough"]/sup/text())'
            ).extract_first()
            regular_price = str(regular_price_dollar).replace(",", "") + "." + str(regular_price_cents)
        else:
            regular_price = active_price

        variant_name = resp.xpath('normalize-space(//div[@id="js-product"]/@data-product-name)').extract_first()
        img_src = resp.xpath('//img[@class="c-thumbnail-grid__image"]/@src').getall()
        currency = "EUR"
        params = {
            "Colour":color,
            "ItemNumber":item_number
        }
        properties = {"":specification}
        variations_en.append(
            {
                "sku": item_number,
                "Name": variant_name,
                "price": active_price,
                "currency":currency,
                "oldPrice": regular_price,
                "properties":properties,
                "images": img_src,
                "params": params,
                "description":description,
            }
        )
        
        total_variants_check = resp.xpath('normalize-space(//li[contains(@id,"option") and @class="option-title "])').extract_first()
        total_variants = resp.xpath('//li[@class="option-title "]/@data-value').getall()
        print("Total length of variants", len(total_variants))
        self.close()
        if total_variants_check:
            small_count = 0
            for i in total_variants:
                val_link = "https://www.emero.de/en/catalogsearch/?q="+str(i)
                
                print("Search Variant Url",val_link)
                self.start()
                self.driver.open(val_link)

                time.sleep(5)
                html = self.driver.page_source
                resp = Selector(text=html)

                link_valo = resp.xpath('//a[@class="c-product-tile__link"]/@href').extract_first()
                if link_valo:
                    link_valo = "https://www.emero.de/en"+str(link_valo)
                    self.driver.open(link_valo)
                    time.sleep(5)
                    small_count = small_count+1
                    html = self.driver.page_source
                    resp = Selector(text=html)

                    description = resp.xpath('//div[@id="product_details"]//div[@class="small-12  small-order-2 large-order-1 columns"]/div[@class="o-pseudo-h3 margin-bottom-2" or@class="margin-bottom-2 margin-top-1"]//text()').getall()
                    description = [item.strip() for item in description if item.strip()]
                    description = ''.join(description).strip()
                    specs = resp.xpath('//dl[@class="c-definition-list c-definition-list--light column"]')
                    specification = {}
                    for spec in specs:
                        key = spec.xpath('normalize-space(.//dt/text())').extract_first()
                        value = spec.xpath('normalize-space(.//dd/text())').extract_first()
                        specification[key] = value

                    item_number = resp.xpath('normalize-space(//div[@id="js-product"]/@data-art-id)').extract_first()

                    
                    color = resp.xpath(
                        'normalize-space(//div[contains(text(),"Colour:")]/following-sibling::div//span/text())'
                    ).extract_first()
                    if not color:
                        color = resp.xpath(
                            'normalize-space(//div[contains(text(),"Colour")]/following-sibling::div//span/text())'
                        ).extract_first()
                    
                    params = {
                        "Colour":color,
                        "ItemNumber":item_number
                    }
                    active_price = resp.xpath('normalize-space(//div[@id="js-product"]/@data-price)').extract_first()
                    regular_price_dollar = resp.xpath(
                        'normalize-space(//strike[@class="c-price-block__price--strikethrough"]/text()[1])'
                    ).extract_first()
                    if regular_price_dollar:
                        regular_price_cents = resp.xpath(
                            'normalize-space(//strike[@class="c-price-block__price--strikethrough"]/sup/text())'
                        ).extract_first()
                        regular_price = str(regular_price_dollar).replace(",", "") + "." + str(regular_price_cents)
                    else:
                        regular_price = active_price

                    variant_name = resp.xpath('normalize-space(//div[@id="js-product"]/@data-product-name)').extract_first()
                    img_src = resp.xpath('//img[@class="c-thumbnail-grid__image"]/@src').getall()
                    currency = "EUR"
                    properties = {"":specification}
                    variations_en.append(
                        {
                            "sku": item_number,
                            "Name": variant_name,
                            "price": float(active_price),
                            "currency":currency,
                            "oldPrice": float(regular_price),
                            "properties":properties,
                            "images": img_src,
                            "params": params,
                            "description":description,
                        }
                    )
                self.close()

        alternativeRubrics = {}
        data = {
            "name":name,
            "brand":brand,
            "externalId":externalId,
            "variations":variations_en, 
            "rubrics": rubrics
        }


        if self.count == 10:
            filename = datetime.now().strftime(f"Import_%Y_%m_%d_%H_%M.json")
            with open(filename, "w") as outfile:
                json.dump(self.output_data, outfile, indent=4)
                self.output_data = []
                self.count = 1
                print("-------------------------------------------------------------------")
                print()
                print("Sucessfully saved json with this name: ",filename)
                print()
                print("-------------------------------------------------------------------")
        else:
            self.output_data.append(data)
            print()
            self.count = self.count+1
            print("Number of records saved in excel: ",self.count)
            print()
        

    

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    scraper = EmEro_De()
    url ="https://www.emero.de/en/"
    #scraper.target_url(url)
    #scraper.save_links_to_csv()
    scraper.run_main()


