from decimal import Decimal
from .models import Key, KeyValue, Order, OrderCancellation, OrderItem, Product, Variation, Image, Tag, Category, Value, Discount
import random
from django.utils.text import slugify

INFO = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."

def UPLOAD_CATEGORIES():
    categories = [
        {"category":"Outdoors"},
        {"category":"Movies"},
        {"category":"Beauty"},
        {"category":"Beauty"},
        {"category":"Outdoors"},
        {"category":"Movies"},
        {"category":"Home"},
        {"category":"Movies"},
        {"category":"Sports"},
        {"category":"Jewelry"},
        {"category":"Computers"},
        {"category":"Grocery"},
        {"category":"Clothing"},
        {"category":"Electronics"},
        {"category":"Toys"},
        {"category":"Grocery"},
        {"category":"Automotive"},
        {"category":"Music"},
        {"category":"Outdoors"},
        {"category":"Books"},
        {"category":"Health"},
        {"category":"Computers"},
        {"category":"Sports"},
        {"category":"Sports"},
        {"category":"Baby"},
        {"category":"Beauty"},
        {"category":"Home"},
        {"category":"Grocery"},
        {"category":"Jewelry"},
        {"category":"Electronics"},
        {"category":"Automotive"},
        {"category":"Automotive"},
        {"category":"Electronics"},
        {"category":"Games"},
        {"category":"Tools"},
        {"category":"Electronics"},
        {"category":"Shoes"},
        {"category":"Industrial"},
        {"category":"Toys"},
        {"category":"Industrial"},
        {"category":"Music"},
        {"category":"Shoes"},
        {"category":"Grocery"},
        {"category":"Books"},
        {"category":"Automotive"},
        {"category":"Sports"},
        {"category":"Tools"},
        {"category":"Games"},
        {"category":"Books"},
        {"category":"Sports"}
    ]
    c = set()
    for category in categories:
        c.add(category["category"])
    
    for category in c:
        ct = Category(
            title=category,
            slug=slugify(category),
        )
        ct.save()


def UPLOAD_PRODUCTS():
    products = [
        {"title":"Potatoes - Parissienne"},
        {"title":"Wine - Dubouef Macon - Villages"},
        {"title":"Pastry - Mini French Pastries"},
        {"title":"Muffin - Carrot Individual Wrap"},
        {"title":"Kohlrabi"},
        {"title":"Gin - Gilbeys London, Dry"},
        {"title":"Flower - Daisies"},
        {"title":"Orange - Tangerine"},
        {"title":"Broom Handle"},
        {"title":"Sauce - Hollandaise"},
        {"title":"Salt - Table"},
        {"title":"Lid - 10,12,16 Oz"},
        {"title":"Pepper - Black, Whole"},
        {"title":"Bread - Onion Focaccia"},
        {"title":"Banana - Green"},
        {"title":"Ice Cream Bar - Rolo Cone"},
        {"title":"Sauce - Rosee"},
        {"title":"Transfer Sheets"},
        {"title":"Muffin - Zero Transfat"},
        {"title":"Champagne - Brights, Dry"},
        {"title":"Bread - 10 Grain Parisian"},
        {"title":"Nut - Walnut, Pieces"},
        {"title":"Muffin Batt - Ban Dream Zero"},
        {"title":"Vinegar - Cider"},
        {"title":"Soup - Campbells, Beef Barley"},
        {"title":"Table Cloth 53x69 White"},
        {"title":"Sorrel - Fresh"},
        {"title":"Beef - Rouladin, Sliced"},
        {"title":"Nantucket - Carrot Orange"},
        {"title":"Wine - Sherry Dry Sack, William"},
        {"title":"Food Colouring - Green"},
        {"title":"Beef - Bresaola"},
        {"title":"Lettuce - Green Leaf"},
        {"title":"Cake Circle, Paprus"},
        {"title":"Juice - Apple, 341 Ml"},
        {"title":"Rambutan"},
        {"title":"Coffee Cup 12oz 5342cd"},
        {"title":"Yukon Jack"},
        {"title":"Beer - Alexander Kieths, Pale Ale"},
        {"title":"Milk - 2%"},
        {"title":"Langers - Mango Nectar"},
        {"title":"Muffin Batt - Carrot Spice"},
        {"title":"Flour - Corn, Fine"},
        {"title":"Wine - Balbach Riverside"},
        {"title":"Huck White Towels"},
        {"title":"Asparagus - Green, Fresh"},
        {"title":"Guava"},
        {"title":"Juice - Apple, 1.36l"},
        {"title":"Pepper - Cayenne"},
        {"title":"Pastry - Baked Cinnamon Stick"},
        {"title":"Bread - Raisin"},
        {"title":"Barley - Pearl"},
        {"title":"Taro Leaves"},
        {"title":"Chicken Breast Halal"},
        {"title":"Wine - Chardonnay South"},
        {"title":"Mustard - Dry, Powder"},
        {"title":"Flour - So Mix Cake White"},
        {"title":"Melon - Cantaloupe"},
        {"title":"Chip - Potato Dill Pickle"},
        {"title":"Pate Pans Yellow"},
        {"title":"Poppy Seed"},
        {"title":"Beef - Kobe Striploin"},
        {"title":"Appetizer - Escargot Puff"},
        {"title":"Coconut - Creamed, Pure"},
        {"title":"Pail - 4l White, With Handle"},
        {"title":"Wine - Taylors Reserve"},
        {"title":"Bulgar"},
        {"title":"Beer - Moosehead"},
        {"title":"Soup - Cream Of Broccoli, Dry"},
        {"title":"Piping - Bags Quizna"},
        {"title":"Lettuce - Red Leaf"},
        {"title":"Silicone Parch. 16.3x24.3"},
        {"title":"Tomatoes - Diced, Canned"},
        {"title":"Muffin Orange Individual"},
        {"title":"Rum - Spiced, Captain Morgan"},
        {"title":"Fish - Artic Char, Cold Smoked"},
        {"title":"Cabbage - Green"},
        {"title":"Flour - Bran, Red"},
        {"title":"Cookies Cereal Nut"},
        {"title":"Table Cloth 81x81 Colour"},
        {"title":"Veal - Insides Provini"},
        {"title":"Soup - Knorr, Chicken Gumbo"},
        {"title":"Ice Cream - Turtles Stick Bar"},
        {"title":"Vacuum Bags 12x16"},
        {"title":"Bread - Assorted Rolls"},
        {"title":"Salsify, Organic"},
        {"title":"Turkey - Breast, Bone - In"},
        {"title":"Cup - 3.5oz, Foam"},
        {"title":"Veal - Shank, Pieces"},
        {"title":"Mace"},
        {"title":"Sausage - Andouille"},
        {"title":"C - Plus, Orange"},
        {"title":"Tarragon - Primerba, Paste"},
        {"title":"Pineapple - Canned, Rings"},
        {"title":"Grapes - Black"},
        {"title":"Milk - 1%"},
        {"title":"Coffee - Hazelnut Cream"},
        {"title":"Fish - Bones"},
        {"title":"Oregano - Dry, Rubbed"},
        {"title":"Lid - Oz"}
    ]

    p = set()
    for product in products:
        p.add(product["title"])
    
    for product in p:
        pd = Product(
            title=product,
            slug=slugify(product),
            info="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."
        )
        pd.save()


def UPLOAD_TAGS():
    tags = [
        {"tag":"yfiiew"},
        {"tag":"zicpwt"},
        {"tag":"keoewn"},
        {"tag":"bjztfz"},
        {"tag":"ucqgwv"},
        {"tag":"stneve"},
        {"tag":"yuexut"},
        {"tag":"lepsbk"},
        {"tag":"usfgki"},
        {"tag":"vrnqcn"},
        {"tag":"gqulmk"},
        {"tag":"hotjmr"},
        {"tag":"xmytvs"},
        {"tag":"vwkbxf"},
        {"tag":"eiqzzz"},
        {"tag":"mxeoic"},
        {"tag":"jgicpc"},
        {"tag":"xmvcgn"},
        {"tag":"asxyhw"},
        {"tag":"mszrlm"},
        {"tag":"sxnrjd"},
        {"tag":"veuxfu"},
        {"tag":"ceriaq"},
        {"tag":"ubwvlf"},
        {"tag":"jntmxu"},
        {"tag":"goaava"},
        {"tag":"szyqrj"},
        {"tag":"khwuzf"},
        {"tag":"lfzslz"},
        {"tag":"mbpyhk"},
        {"tag":"ckfcth"},
        {"tag":"zvicje"},
        {"tag":"qlappt"},
        {"tag":"xznjnf"},
        {"tag":"quqjvs"},
        {"tag":"noewsk"},
        {"tag":"kenbpi"},
        {"tag":"yqclak"},
        {"tag":"zjhtms"},
        {"tag":"oujsjn"},
        {"tag":"csynvf"},
        {"tag":"rshgly"},
        {"tag":"lbjfqh"},
        {"tag":"zxegcw"},
        {"tag":"ejlsrp"},
        {"tag":"twsaqo"},
        {"tag":"ocfoji"},
        {"tag":"uvubrg"},
        {"tag":"nggqwq"},
        {"tag":"wyooor"}
    ]

    t = set()
    for tag in tags:
        t.add(tag["tag"])
    
    for tag in t:
        tg = Tag(
            name=tag
        )
        tg.save()


def UPDATE_PROUCTS():    
    images = Image.objects.all()
    tags = Tag.objects.all()
    categories = Category.objects.all()

    products = Product.objects.all()
    for product in products:
        a, b = 1, 1
        while a == b:
            a = random.randint(0, 6)
            b = random.randint(0, 6)
        product.images.add(images[a], images[b])
        
        a, b = 1, 1
        while a == b:
            a = random.randint(0, 19)
            b = random.randint(0, 19)
        product.categories.add(categories[a], categories[b])

        a, b = 1, 1
        while a == b:
            a = random.randint(0, 49)
            b = random.randint(0, 49)
        product.tags.add(tags[a], tags[b])
        product.save()
    return


def UPDATE_KEYVALUE():
    companies = [
        {"tag":"Ainyx"},
        {"tag":"Facebook"},
        {"tag":"Twitter"},
        {"tag":"Voomm"},
        {"tag":"Google"},
        {"tag":"Feedfire"},
        {"tag":"Microsoft"},
        {"tag":"Muxo"}
    ]
    k = Key(key="Company")
    k.save()

    c = set()
    for company in companies:
        c.add(company["tag"])
    
    for company in c:
        v = Value(value=company)
        v.save()
        
        kv = KeyValue(key=k, value=v)
        kv.save()

    brands = [
        {"tag":"OXYGEN"},
        {"tag":"Epithelium"},
        {"tag":"RIDAURA"},
        {"tag":"SEROQUEL"},
        {"tag":"HOUSE DUST"},
        {"tag":"Hydrochlorothiazide"},
        {"tag":"Nicardipine"},
        {"tag":"Naproxen Sodium"},
        {"tag":"Hydrocortisone"},
        {"tag":"Methylphenidate"}
    ]

    k = Key(key="Brand")
    k.save()

    c = set()
    for brand in brands:
        c.add(brand["tag"])
    
    for brand in c:
        v = Value(value=brand)
        v.save()
        
        kv = KeyValue(key=k, value=v)
        kv.save()

    colors = [
        {"tag":"Fuscia"},
        {"tag":"Teal"},
        {"tag":"Green"},
        {"tag":"Mauv"},
        {"tag":"Turquoise"},
        {"tag":"Fuscia"},
        {"tag":"Turquoise"},
        {"tag":"Aquamarine"},
        {"tag":"Goldenrod"},
        {"tag":"Pink"}
    ]

    k = Key(key="Color")
    k.save()

    c = set()
    for color in colors:
        c.add(color["tag"])
    
    for color in c:
        v = Value(value=color)
        v.save()
        
        kv = KeyValue(key=k, value=v)
        kv.save()


def UPDATE_VARIATIONS():
    keyvalues = KeyValue.objects.all()
    images = Image.objects.all()

    products = Product.objects.all()
    for product in products:
        for _ in range(3):
            v = Variation(
                product=product,
                price=Decimal(random.randint(200, 500)),
                availability=True,
                info=INFO
            )
            v.save()

            a, b, c = 1, 1, 1
            while a == b or a == c or b == c:
                a = random.randint(0, 25)
                b = random.randint(0, 25)
                c = random.randint(0, 25)
            v.keyvalues.add(keyvalues[a], keyvalues[b], keyvalues[c])
    
            a, b = 1, 1
            while a == b:
                a = random.randint(0, 6)
                b = random.randint(0, 6)
            v.images.add(images[a], images[b])
    return


def clear_all_but_images():
    oc = OrderCancellation.objects.all().delete()
    odi = OrderItem.objects.all().delete()
    o = Order.objects.all().delete()
    d = Discount.objects.all().delete()
    v = Variation.objects.all().delete()
    kv = KeyValue.objects.all().delete()
    v = Value.objects.all().delete()
    k = Key.objects.all().delete()
    p = Product.objects.all().delete()
    c = Category.objects.all().delete()
    t = Tag.objects.all().delete()


def clear_images():
    i = Image.objects.all().delete()


def inventory():
    variations = Variation.objects.all()
    for variation in variations:
        variation.inventory = random.randint(0, 50)
        variation.save()
    return
