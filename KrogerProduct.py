class Product:

    """represents a single grocery product"""

    def __init__(self, id, upc, brand, description, image, size, price):
        self.id = id
        self.upc = upc
        self.brand = brand
        self.description = description
        self.image = image
        self.size = size
        self.price = price #tuple (regular, promo)

    def __str__(self):
        verbose = False
        description = f"({self.brand}) {self.description}"
        if self.size:
            if self.price[1] == 0:
                description += f" - {self.size}: ${self.price[0]}"
            else:
                description += f" - {self.size}: ${self.price[0]} (regular), ${self.price[1]} (promo)"
        else:
            if self.price[1] == 0:
                description += f" - ${self.price[0]}"
            else:
                description += f" - ${self.price[0]} (regular), ${self.price[1]} (promo)"
        
        if verbose:
            description += f"\nProduct ID: {self.id}"
            description += f"\nUPC: {self.upc}"
            description += f"\nImage: {self.image}"
        return description
    
    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_json(cls, obj):
        id = obj.get("productId")
        upc = obj.get("upc")
        brand = obj.get("brand")
        description = obj.get("description")
        image = get_image_from_images(obj.get("images"))
        size = get_product_size(obj.get("items"))
        #price is a tuple
        price = get_product_price(obj.get("items"))

        return Product(id, upc, brand, description, image, size, price)

def get_image_from_images(images, perspective='front', size='medium'):
    front_image = next((image for image in images if image.get("perspective") == perspective), None)
    if front_image:
        sizes = front_image.get("sizes", [])
        front_image = next((s.get("url") for s in sizes if s.get("size") == size), None)
    return front_image

def get_product_size(items):

    if len(items) > 0:
        return items[0].get("size")
    else:
        return None

def get_product_price(items):
    
    if len(items) > 0:
        return (items[0].get("price", {}).get('regular'),items[0].get("price", {}).get('promo'))  #, items[0].get("price", {}).get('promo'))
    else:
        return None