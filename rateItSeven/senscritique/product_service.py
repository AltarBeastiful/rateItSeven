#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
#   Copyright 2015, Paolo de Vathaire <paolo.devathaire@gmail.com>
#
#   RateItSeven is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   RateItSeven is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with RateItSeven. If not, see <http://www.gnu.org/licenses/>.
#
import json

import re

from rateItSeven.senscritique.domain.product import Product, ProductType
from rateItSeven.senscritique.sc_api import ScRequester


class ProductService(ScRequester):
    _URL_SEARCH = "https://www.senscritique.com/sc2/search/autocomplete.json"

    def find_product(self, title: str, product_type: ProductType = None) -> list:
        response = self.send_get(url=self._URL_SEARCH, params={"query": title})
        content = json.loads(response.text)

        if not content["json"]:
            return None

        products = [self._product_from_url(product["url"], product["label"]) for product in content["json"]]

        if product_type is not None:
            products = [product for product in products if product.type == product_type]
        return products

    def _product_from_url(self, url: str, title: str) -> Product:
        m = re.search(".*senscritique\.com/(.*)/.*/(.*)", url)
        return Product(type=ProductType(m.group(1)), title=title, id=m.group(2))
