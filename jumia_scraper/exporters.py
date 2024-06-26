from scrapy.exporters import JsonItemExporter
from collections import OrderedDict

class PrettyJsonItemExporter(JsonItemExporter):
    def __init__(self, file, **kwargs):
        super(PrettyJsonItemExporter, self).__init__(file, indent=2, sort_keys=True, **kwargs)

    def export_item(self, item):
        if isinstance(item, dict):
            ordered_item = OrderedDict()
            for key in ['title', 'price', 'old_price', 'discount', 'rating', 'total_ratings', 'average_rating', 'seller', 'description', 'specifications', 'product_details', 'image_url', 'product_url', 'you_may_also_like']:
                if key in item:
                    ordered_item[key] = item[key]
            for key in item:
                if key not in ordered_item:
                    ordered_item[key] = item[key]
            item = ordered_item
        super(PrettyJsonItemExporter, self).export_item(item)
