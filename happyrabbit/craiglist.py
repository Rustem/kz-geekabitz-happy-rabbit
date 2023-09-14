import json
import os
import re
from dataclasses import dataclass, fields, field, asdict
from datetime import datetime, date
from enum import Enum
from pprint import pprint
from time import sleep
from typing import Optional, List, Set

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from fake_useragent import UserAgent


import csv


@dataclass
class CraigslistRecord:
    id: str
    title: str
    url: str


@dataclass
class AddressComponents:
    street: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    postalCode: Optional[str] = None


class HousingType(Enum):
    APARTMENT = "apartment"
    CONDO = "condo"
    COTTAGE_CABIN = "cottage/cabin"
    DUPLEX = "duplex"
    FLAT = "flat"
    HOUSE = "house"
    IN_LAW = "in-law"
    LOFT = "loft"
    TOWNHOUSE = "townhouse"


@dataclass
class Listing:
    postingId: str
    postingUrl: str
    createdAt: field(default_factory=datetime.now)
    updatedAt: field(default_factory=datetime.now)
    postingDate: Optional[datetime] = None
    address: Optional[AddressComponents] = None
    latLon: Optional[List[float]] = None
    housingType: Optional[HousingType] = None
    numberOfBedrooms: Optional[int] = None
    numberOfBathrooms: Optional[int] = None
    totalSquareFootage: Optional[int] = None
    numberOfParkingStalls: Optional[int] = None
    attrs: Set[str] = field(default_factory=set)
    advertisedRentPrice: Optional[float] = None
    advertisedRentPriceHistory: List[float] = field(default_factory=list)
    rentalStartDate: Optional[date] = None # tentative date when rental unit is available
    gallery: List[str] = field(default_factory=list)


class CsvWriter:
    def __init__(self, file_path="/Users/rustem/Downloads/craigslist_titles.csv"):
        self.file_path = file_path
        self.file = open(self.file_path, 'w', newline='')
        self.writer = csv.writer(self.file)
        # Write the header row by getting field names from CraigslistRecord dataclass
        self.writer.writerow([field.name for field in fields(CraigslistRecord)])

    def write_record(self, record: CraigslistRecord):
        self.writer.writerow([getattr(record, field.name) for field in fields(CraigslistRecord)])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()


class ListingCsvWriter:

    def __init__(self, file_path="/Users/rustem/Downloads/craigslist_listings.csv"):
        # Get field names for both classes
        fieldnames = self.get_field_names()

        self.file_path = file_path
        file_exists = os.path.exists(self.file_path)
        self.file = open(self.file_path, 'a', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
        # Write the header row by getting field names from CraigslistRecord dataclass
        # Do it only for the first time
        if not file_exists:
            self.writer.writeheader()

    def get_field_names(self):
        listing_fields = self._get_fieldnames(Listing)
        address_component_fields = self._get_fieldnames(AddressComponents)
        # Create a combined list of field names, prefixing address component fields with 'address_'
        # and removing the 'address' field from listing_fields
        fieldnames = [field for field in listing_fields if field != 'address'] + \
                     ['address_' + field for field in address_component_fields]
        return fieldnames

    def listing_to_dict(self, listing):
        result = {}

        # Convert AddressComponents to dictionary
        if listing.address:
            address_dict = asdict(listing.address)
            result.update({f'address_{key}': value for key, value in address_dict.items()})

        # Convert attrs set to comma-separated string
        result['attrs'] = ", ".join(listing.attrs) if listing.attrs else None

        # Convert enums to string values
        result['housingType'] = listing.housingType.name if listing.housingType else None

        # Adding other fields
        result['latLon'] = listing.latLon
        result['postingId'] = listing.postingId
        result['postingUrl'] = listing.postingUrl
        result['createdAt'] = listing.createdAt
        result['updatedAt'] = listing.updatedAt
        result['postingDate'] = listing.postingDate
        result['numberOfBedrooms'] = listing.numberOfBedrooms
        result['numberOfBathrooms'] = listing.numberOfBathrooms
        result['totalSquareFootage'] = listing.totalSquareFootage
        result['numberOfParkingStalls'] = listing.numberOfParkingStalls
        result['advertisedRentPrice'] = listing.advertisedRentPrice
        result['advertisedRentPriceHistory'] = ', '.join(map(str, listing.advertisedRentPriceHistory))
        result['rentalStartDate'] = listing.rentalStartDate
        result['gallery'] = ', '.join(listing.gallery)

        return result

    def _get_fieldnames(self, cls):
        return [field.name for field in fields(cls)]

    def write_record(self, listing: Listing):
        self.writer.writerow(self.listing_to_dict(listing))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()


class CraigslistScraper:
    # params = has image & search titles only
    VANCOUVER_BASE_URL = 'https://vancouver.craigslist.org/search/rds/apa?hasPic=1&srchType=T#search=1~gallery~0~0'
    # VANCOUVER_BASE_URL = 'https://vancouver.craigslist.org/d/apartments-housing-for-rent/search/apa'

    def __init__(self, path_to_webdriver):
        self.path_to_webdriver = path_to_webdriver
        self.driver = self.setup_driver()
        self.all_records = []
        self.page_count = 0
        # track field presence statistics across scraped listings
        # should help to exclude certain fields from consideration or improve parsing
        self.field_statistics = {field.name: {'filled': 0, 'empty': 0} for field in fields(Listing)}

    def setup_driver(self):
        service = Service(executable_path=self.path_to_webdriver)
        options = webdriver.ChromeOptions()
        ua = UserAgent() # fake user agent to avoid beign blocked by craiglist
        options.add_argument(f"user-agent={ua.random}")
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
        return driver

    def scrape_craigslist_titles(self, max_pages=10):
        self.page_count = 0

        self.driver.get(self.VANCOUVER_BASE_URL)

        while self.page_count < max_pages:
            try:
                listings = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.cl-search-result'))
                ) or []

                for listing in listings:
                    soup = BeautifulSoup(listing.get_attribute('outerHTML'), 'html.parser')
                    data_pid = soup.li['data-pid']
                    url = soup.find('a', {'class': 'cl-app-anchor'})['href']

                    title = soup.li.get('title')
                    if not title:
                        title_tag = soup.select_one('a.posting-title > span.label')
                        if title_tag:
                            title = title_tag.get_text()
                        else:
                            title = 'Title not found'

                    record = CraigslistRecord(
                        id=data_pid,
                        title=title,
                        url=url,
                    )

                    self.all_records.append(record)

                next_button = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'button.bd-button.cl-next-page.icon-only'))
                )
                next_button.click()

                self.page_count += 1

            except Exception as e:
                print(f"An error occurred: {e}")
                break

        print("Closing the driver and shut down the browser")
        self.driver.quit()

    def scrape_listings(self, max_items=20, page_size=100):
        scraped = []
        print(f"Extracting listing details")
        current_date = datetime.now().strftime('%Y_%m_%d')

        with open(f"/Users/rustem/Downloads/craigslist_titles.csv", 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                sleep(0.5)
                if max_items and i > max_items:
                    break
                if i == 0: # skip head
                    continue

                id, _, url = row
                listing = self.scrape_listing_detail(id, url)
                if listing is None:
                    continue
                scraped.append(listing)

                if len(scraped) % page_size == 0:
                    # store listing in another csv
                    file_path = f"/Users/rustem/Downloads/craigslist_listings_{current_date}.csv"
                    with ListingCsvWriter(file_path=file_path) as writer:
                        print(f"Storing {len(scraped)} listings in csv file: {writer.file_path}: \n\n")
                        for listing in scraped:
                            writer.write_record(listing)
                    del scraped
                    scraped = []
                    self.driver.quit()
                    self.driver = self.setup_driver()

        pprint(self.field_statistics)

    def scrape_listing_detail(self, posting_id, url):
        self.driver.get(url)

        WebDriverWait(self.driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body.posting'))
        )

        # WebDriverWait(self.driver, 3).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, '//script[@type="application/ld+json" and @id="ld_posting_data"]'))
        # )

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        if soup.select_one("div.removed") is not None:
            print(f"Posting for id={posting_id} is removed")
            return

        # Extract JSON script data for some attributes
        json_data = soup.find('script', {'id': 'ld_posting_data'}).string
        json_data = json.loads(json_data)

        posting_date_str = soup.select_one("p#display-date > time.date")["datetime"]
        available_from_str = self.getAvailableFromDate(soup)

        address = self.getAddress(soup, json_data)
        housingType = self.getHousingType(soup)
        square_feet = self.getTotalSquareFootage(soup)
        price = self.getPrice(soup)
        attrs = self.getAttrs(soup)
        gallery = self.getImages(soup)

        latLon = []
        mapTag = soup.select_one("div.mapAndAttrs div#map")
        if mapTag and mapTag.get('data-latitude'):
            latLon = [float(mapTag.get('data-latitude')), float(mapTag.get('data-longitude'))]

        listing = Listing(
            postingId=posting_id,
            postingUrl=url,
            postingDate=datetime.strptime(posting_date_str, "%Y-%m-%dT%H:%M:%S%z"),
            rentalStartDate=None if available_from_str is None else datetime.strptime(available_from_str, "%Y-%m-%d").date(),
            address=address,
            latLon=latLon,
            housingType=housingType,
            numberOfBedrooms=json_data.get("numberOfBedrooms"),
            numberOfBathrooms=json_data.get("numberOfBathroomsTotal"),
            totalSquareFootage=square_feet,
            advertisedRentPrice=price,
            advertisedRentPriceHistory=[price],  # Add the appropriate method to fetch rent history as a list of ints
            attrs=attrs,  # amenities
            gallery=gallery,
            numberOfParkingStalls=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )

        self.update_field_statistics(listing)
        return listing

    @staticmethod
    def getPrice(soup):
        # Select the price element and get its text content
        price_tag = soup.select_one(".price")
        if not price_tag or not price_tag.text:
            return None
        return float(re.sub(r'[,$]', '', price_tag.text))

    @staticmethod
    def getAddress(soup, json_data):
        json_address = json_data.get("address", {})
        return AddressComponents(
            street=json_address.get("streetAddress"),
            district=json_address.get("streetAddress"),
            city=json_address.get("addressLocality"),
            province=json_address.get("addressRegion"),
            country=json_address.get("addressCountry"),
            postalCode=json_address.get("postalCode"))

    @staticmethod
    def getHousingType(soup):
        # Search in all potential attribute groups
        attr_groups = soup.select('div.mapAndAttrs > p.attrgroup')

        for group in attr_groups:
            for item in group.find_all(['span', 'p'], recursive=True):  # Search in span and directly in p
                text_content = item.get_text()
                for housing_type in HousingType:
                    if housing_type.value in text_content.lower():  # Check if any of the enum values are in the text
                        return housing_type
        return None  # Return None if not found

    @staticmethod
    def getTotalSquareFootage(soup):
        housing_tag = soup.select_one("h1.postingtitle span.housing")
        if not housing_tag or not housing_tag.text:
            return None
        housing_text = housing_tag.text
        match = re.search(r'(\d+(\.\d+)?)ft', housing_text)
        square_feet = None
        if match:
            square_feet = float(match.group(1))
        return square_feet

    @staticmethod
    def getAttrs(soup):
        # Initialize a set to hold the found attributes
        found_attributes = set()

        # Select the posting body and map and attrs section and get all the text
        # TODO we can also parse text in postingBody to obtain more tags
        tags = soup.select('div.mapAndAttrs p.attrgroup span')

        for tag in tags:
            attr = tag.get_text().strip().lower()
            if not attr:
                continue
            found_attributes.add(attr)
        return found_attributes

    @staticmethod
    def getAvailableFromDate(soup):
        element = soup.select_one("div.mapAndAttrs span.housing_movein_now")
        return None if element is None else element.get("data-date")

    @staticmethod
    def getImages(soup):
        thumbs = soup.select('section.userbody div#thumbs a.thumb') or []
        image_urls = [thumb['href'] for thumb in thumbs if thumb.has_attr('href')]
        return image_urls

    def dump_titles(self):
        print(f"Found {len(self.all_records)} records in total by going through {self.page_count} pages.")

        with CsvWriter() as writer:
            print(f"Storing them in csv file: {writer.file_path}: \n\n")
            for record in self.all_records:
                writer.write_record(record)

    def update_field_statistics(self, listing: Listing):
        for field in fields(listing):
            field_value = getattr(listing, field.name)
            if field_value is None:
                self.field_statistics[field.name]['empty'] += 1
            else:
                self.field_statistics[field.name]['filled'] += 1


# Usage

if __name__ == "__main__":
    path_to_webdriver = "/Users/rustem/code/drivers/chromedriver"
    scraper = CraigslistScraper(path_to_webdriver)
    scraper.scrape_listings(max_items=0, page_size=20)
    # scraper.scrape_craigslist_titles(max_pages=20)
    # scraper.dump_titles()

    # data = """
    # 7664335588	New 750 SQFT 1Bed 1Bath Basement	https://vancouver.craigslist.org/bnc/apa/d/burnaby-new-750-sqft-1bed-1bath-basement/7664335588.html
    # 7664336998	Renovated small garden suite with yard and patio	https://vancouver.craigslist.org/nvn/apa/d/north-vancouver-renovated-small-garden/7664336998.html
    # 7660019038	One and two bedroom suites, On-Site Management, 1 BD	https://vancouver.craigslist.org/rds/apa/d/langley-city-one-and-two-bedroom-suites/7660019038.html
    # 7657825692	1 bedroom suite maple ridge	https://vancouver.craigslist.org/pml/apa/d/maple-ridge-bedroom-suite-maple-ridge/7657825692.html
    # 7664333185	One bedroom&Den for rent in Vancouver Yaletown	https://vancouver.craigslist.org/van/apa/d/vancouver-one-bedroomden-for-rent-in/7664333185.html
    # 7661061101	Bright Newer 3 bedrooms with an exclusive big yard	https://vancouver.craigslist.org/rch/apa/d/richmond-bright-newer-bedrooms-with-an/7661061101.html
    # 7664336379	1BR TOWNHOUSE SUITE FOR RENT	https://vancouver.craigslist.org/van/apa/d/vancouver-1br-townhouse-suite-for-rent/7664336379.html
    # 7659526449	New 3 Bedroom Laneway House	https://vancouver.craigslist.org/van/apa/d/vancouver-new-bedroom-laneway-house/7659526449.html
    # 7654068754	South Granville Georgian	https://vancouver.craigslist.org/van/apa/d/vancouver-south-granville-georgian/7654068754.html
    # 7663564902	本那比Brentwood全新公寓出租 2室2卫1Den	https://vancouver.craigslist.org/van/apa/d/burnaby-brentwood-221den/7663564902.html
    # 7664333218	Brand new 3 Bedroom 2.5 Bath Townhouse in Delta Tsawwassen	https://vancouver.craigslist.org/van/apa/d/tsawwassen-brand-new-bedroom-25-bath/7664333218.html
    # 7664335771	Brand new unit	https://vancouver.craigslist.org/bnc/apa/d/burnaby-brand-new-unit/7664335771.html
    # 7664335603	North Burnaby Duplex - Convenient, Bright, Spacious 3BR 2Ba	https://vancouver.craigslist.org/bnc/apa/d/burnaby-north-burnaby-duplex-convenient/7664335603.html
    #
    # """
    # lines = data.strip().split("\n")
    # for i, line in enumerate(lines):
    #     # Split each line into id, description, and url
    #     id, _, url = line.split("\t")
    #     scraped_listing = scraper.scrape_listing_detail(id, url)
    #     print(scraped_listing)
    #     if i > 1:
    #         break
