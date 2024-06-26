import scrapy
import re

class JumiaGrocerySpider(scrapy.Spider):
    name = 'jumia_grocery'
    start_urls = ['https://www.jumia.co.ke/groceries/']

    def parse(self, response):
        products = response.css('article.prd')
        for product in products:
            product_url = response.urljoin(product.css('a.core::attr(href)').get())
            yield scrapy.Request(product_url, callback=self.parse_product, meta={
                'title': product.css('h3.name::text').get(),
                'price': product.css('.prc::text').get(),
                'old_price': product.css('.old::text').get(),
                'discount': product.css('._dsct::text').get(),
                'rating': product.css('.stars::attr(data-stars)').get(),
                'image_url': product.css('img.img::attr(data-src)').get(),
                'product_url': product_url,
            })
        
        next_page = response.css('a.pg[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        product_data = response.meta

        # Product details
        product_data['product_details'] = self.clean_text_list(response.css('#product-details .markup.-mhm::text').getall())
        
        # Specifications
        specifications = {}
        spec_table = response.css('div.markup.-pam')
        for row in spec_table.css('li.-pvxs'):
            key = row.css('span.-w60.-pts::text').get()
            value = row.css('span.-w40::text').get()
            if key and value:
                specifications[self.clean_text(key)] = self.clean_text(value)
        product_data['specifications'] = specifications

        # Description
        product_data['description'] = self.clean_text(' '.join(response.css('div.markup.-mhm p::text').getall()))

        # Seller information
        product_data['seller'] = self.clean_text(response.css('div.-phs a.sdName::text').get())

        # Customer ratings
        ratings = response.css('div.rev-w')
        if ratings:
            product_data['total_ratings'] = self.extract_number(ratings.css('p.title::text').get())
            product_data['average_rating'] = ratings.css('div.stars::attr(data-stars)').get()

        # You may also like
        you_may_like = []
        for item in response.css('section.-fw.-phs div.-pvxs'):
            you_may_like.append({
                'title': self.clean_text(item.css('h3.name::text').get()),
                'price': self.clean_text(item.css('div.prc::text').get()),
                'url': response.urljoin(item.css('a::attr(href)').get()),
            })
        product_data['you_may_also_like'] = you_may_like

        yield product_data

    def clean_text(self, text):
        if text:
            return re.sub(r'\s+', ' ', text.strip())
        return text

    def clean_text_list(self, text_list):
        return [self.clean_text(text) for text in text_list if text.strip()]

    def extract_number(self, text):
        if text:
            return re.search(r'\d+', text).group()
        return None
