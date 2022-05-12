import sys,os,re
from numpy import number
import pandas as pd
from flask import Flask, flash, request, redirect, render_template, session
from werkzeug.utils import secure_filename
from config import *
from json import dump
#import boto3
from S3Images import S3Images
from OCR2 import OCR2
from Kroger_Auth import *
from KrogerClient import KrogerClient
from KrogerProduct import Product
from PriceAnalysis import ComparePrices
from FindMatchesKroger import FindMatchesKroger

"""
user uploads image
image is uploaded to s3 bucket
image is sent to OCR class
"""

#AWS access info
ACCESS_KEY = 'AWS_ACCESS_KEY'
SECRET = 'AWS_SECRET_ACCESS_KEY'
BUCKET = 'S3_BUCKET_NAME'
REGION = 'SELECTED_REGION'

#global variables
UPLOAD = "upload"
OCR_OUT = 'outcsv'
retrieved = {}
app = Flask(__name__)
app.secret_key = 'penny'

if not os.path.isdir(upload_dest):
    os.mkdir(upload_dest)

app.config['MAX_CONTENT_LENGTH'] = file_mb_max * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

s3 = S3Images(aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET,
                          region_name=REGION)
file_path = ""

client = KrogerClient(client_key_secret_enc)

@app.route('/', methods=['GET'])
def home():
    return render_template('start.html')

@app.route("/upload")
def upload_zipcode():
    return render_template("upload_zipcode.html")

@app.route("/upload_select_store", methods = ['GET','POST'])
def upload_select_store():
    zip = request.form.get("zip")
    stores = client.get_locations(str(zip))

    names = []
    addresses = []

    for i in stores:
        names.append(i.name)
        addresses.append(i.address)
    link = "/upload_select_radius/" + zip
    return render_template("upload_select_store.html", link = link, names = names, addresses = addresses)

@app.route("/upload_select_radius/<zip>", methods = ['GET', 'POST'])
def upload_search_radius(zip):
    selected_store = request.form.get("store")
    link = "/upload/" + zip + "/" + selected_store
    return render_template("search_radius.html", link = link)

@app.route("/output/<zip>/<selected_store>/<radius>", methods=['GET', 'POST'])
def output(zip, selected_store, radius):
    if 'files[]' not in request.files:
            flash('No files found, try again.')
            return redirect(request.url)
    files = request.files.getlist('files[]')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img_path = os.path.join(upload_dest, filename)
            #save in local folder
            file.save(img_path)
            #save in s3 bucket
            file_path = os.path.join(UPLOAD, filename)
            s3.to_s3(img_path, BUCKET, file_path)
            ocr_object = OCR2(s3, file_path, BUCKET)

            #method 1, return item and value csv files
            key_values, line_items =  ocr_object.process_text_detection()
            key_values.seek(0)
            line_items.seek(0)
            df1 = pd.read_csv(key_values)
            df1.pop("Unnamed: 0")
            df2 = pd.read_csv(line_items)
            df2.pop("Unnamed: 0")
            #method2
            #ocr_object.process_text_analysis()
            match = FindMatchesKroger(df2,str(zip))
            locations = match.findStores()
            match.selectedStore = locations[int(selected_store)-1].id
            matched = match.findmatches()

    flash('File(s) uploaded')
    dict_df2 = df2.to_dict(orient="list")
    global retrieved
    retrieved= dict_df2
    link = "/comparison/" + zip + "/" + selected_store + "/" + radius
    return render_template("output.html", df1=df1, df2=df2, link = link)

@app.route('/comparison/<zip>/<selected_store>/<radius>', methods = ['GET', 'POST'])
def priceComparisonResults(zip, selected_store, radius):
    global retrieved
    item_data = retrieved
    #print(retrieved)
    amt_paid = []
    mean_price = []
    stdev_price = []
    item_str = []
    min_item = []
    #print(item_data)

    for item in item_data['matches']:
        if item != None:
            #id is a key in dictionary
            selectedItemId = item.id
            stores = client.get_locations(str(zip))
            locations = client.get_locations(str(zip), within_miles = radius, limit = 20)

            selectedStoreID = stores[int(selected_store)-1].id
            selectedStoreInfo = stores[int(selected_store)-1]


            # search_results = client.search_products(selected_item, selectedStoreID)
            # selectedItemId = search_results[int(selected_item) - 1].id

            #changes
            selectedItemPrice = item.price
            amt_paid.append(selectedItemPrice)
            selectedItemInfo = item
            #print(selectedItemInfo)

            nearby_results = {}

            for i in locations:
                ans = client.search_products(None, i.id, selectedItemId)
                if ans == []:
                    continue
                if ans[0].price != (None, None):
                    nearby_results[i] = ans[0]

            if selectedItemPrice[1] != 0:
                selectedPriceNew = selectedItemPrice[1]
            else:
                selectedPriceNew = selectedItemPrice[0]

            #print(nearby_results)

            analysis = ComparePrices(selectedItemInfo, selectedPriceNew, selectedStoreInfo, nearby_results)

            min_item_info = analysis.get_min_item()
            mean = analysis.get_mean()
            stdev = analysis.get_standard_dev()

            mean_price.append(analysis.get_mean_str(mean))
            stdev_price.append(analysis.get_stdev_str(stdev))
            item_str.append(analysis.get_item_str())
            min_item.append(analysis.get_min_item_str(radius, min_item_info))
        else:
            amt_paid.append(None)
            mean_price.append(None)
            stdev_price.append(None)
            item_str.append(None)
            min_item.append(None)

    data = pd.DataFrame()
    data["Amount Paid"] = item_data['price']
    data["Mean Price"] = mean_price
    data["Sd Price"] = stdev_price
    data["Item"] = item_str
    data["Min Item"] = min_item

    return render_template("upload_comparison_results.html", data = data)

@app.route('/upload/<zip>/<selected_store>', methods=['GET', 'POST'])
def upload_file(zip, selected_store):
    radius = request.form.get("radius")
    link = "/output/" + zip + "/" + selected_store + "/" + radius
    return render_template("upload.html", link = link)


@app.route("/lookup", methods = ['GET','POST'])
def lookup():
    return render_template("lookup.html")

@app.route("/storeSelect", methods = ['GET', 'POST'])
def storeSelect():
    zip = request.form.get("zip")
    stores = client.get_locations(str(zip))

    names = []
    addresses = []

    for i in stores:
        names.append(i.name)
        addresses.append(i.address)
    link = "/searchRadius/" + zip
    return render_template("store_select.html", link = link, names = names, addresses = addresses)

@app.route("/searchRadius/<zip>", methods = ['GET', 'POST'])
def searchRadius(zip):
    selected_store = request.form.get("store")
    # selectedStoreID = nearby[int(selected_store)].id
    # selectedStoreInfo = nearby[int(selected_store)]
    link = "/itemLookup/" + zip + "/" + selected_store
    return render_template("search_radius.html", link = link)

@app.route("/itemLookup/<zip>/<selected_store>", methods = ['GET', 'POST'])
def itemLookup(zip, selected_store):
    radius = request.form.get("radius")
    link = "/itemSelect/" + zip + "/" + selected_store + "/" + radius
    return render_template("item_lookup.html", link = link)


@app.route("/itemSelect/<zip>/<selected_store>/<radius>", methods = ['GET', 'POST'])
def searchResults(zip, selected_store, radius):
    item = request.form.get("item")
    stores = client.get_locations(str(zip))
    selectedStoreID = stores[int(selected_store)-1].id
    search_results = client.search_products(item, selectedStoreID)
    link = "/comparisonResults/" + zip + "/" + selected_store + "/" + radius + "/" + item
    return render_template("search_results.html", link = link, results = search_results)

#I have gotten here
@app.route("/comparisonResults/<zip>/<selected_store>/<radius>/<item>", methods = ['GET', 'POST'])
def comparisonResults(zip, selected_store, radius, item):
    selected_item = request.form.get("item")
    stores = client.get_locations(str(zip))
    locations = client.get_locations(str(zip), within_miles = radius, limit = 20)

    selectedStoreID = stores[int(selected_store)-1].id
    selectedStoreInfo = stores[int(selected_store)-1]

    search_results = client.search_products(item, selectedStoreID)
    selectedItemId = search_results[int(selected_item) - 1].id

    selectedItemPrice = search_results[int(selected_item) - 1].price
    selectedItemInfo = search_results[int(selected_item) - 1]

    nearby_results = {}

    for i in locations:
        ans = client.search_products(None, i.id, selectedItemId)
        if ans == []:
            continue
        if ans[0].price != (None, None):
            nearby_results[i] = ans[0]

    if selectedItemPrice[1] != 0:
        selectedPriceNew = selectedItemPrice[1]
    else:
        selectedPriceNew = selectedItemPrice[0]


    analysis = ComparePrices(selectedItemInfo, selectedPriceNew, selectedStoreInfo, nearby_results)

    min_item_info = analysis.get_min_item()
    mean = analysis.get_mean()
    stdev = analysis.get_standard_dev()

    mean_price = analysis.get_mean_str(mean)
    stdev_price = analysis.get_stdev_str(stdev)
    item_str = analysis.get_item_str()
    min_item = analysis.get_min_item_str(radius, min_item_info)

    return render_template("comparison_results.html", mean = mean_price, stdev = stdev_price, item = item_str, min = min_item)


if __name__ == "__main__":
    print('to upload files navigate to http://127.0.0.1:4000/')
    app.run(host='127.0.0.1',port=4000,debug=True,threaded=True)
