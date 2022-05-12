# project-penny

## About

Python flask webapp connected to Kroger API, with integrated receipt scanner and item lookup, and price comparison functionalities.

## Features 

### Item Lookup
Users can lookup an item by first entering a zip code, selecting a store, searching for an item in that store, and then setting a search radius. The app will search the prices for the selected item within that radius and reveal price statistics about the item within the selected geographical boundary.

### Receipt Upload
Users can upload an image of receipt, the app will extract relevant text from the receipt, display it on the screen and find the best match using the API. Next, the app allows users to set a search radius to price comaprison on each item.

## Requirements

1. Python3
2. AWS
3. Kroger API client id and secret key
4. base64
5. os
6. unicodedata
7. requests
8. simple_cache
9. pandas
10. fuzzywuzzy
11. jmespath
12. json
13. boto3
14. io
15. sys
16. PIL
17. math
18. textractprettyprinter.t_pretty_print_expense
19. trp
20. logging
21. statistics
22. flask
23. werkzeug.utils
24. abbreviations.csv
25. raw_web_joined.csv

## Run

`$ python3 app.py`

## Kroger API

### Homepage
https://developer.kroger.com/reference/

### Quick Start Guide
https://developer.kroger.com/documentation/public/getting-started/quick-start

## AWS 

### Getting Started - https://docs.aws.amazon.com/textract/latest/dg/getting-started.html

### Analyzing Invoices and Receipt Documents - https://docs.aws.amazon.com/textract/latest/dg/analyzing-document-expense.html

## Files

1. Kroger_Auth.py - gets client access token

2. KrogerClient.py - `KrogerClient` class instantiates an access token using Kroger_Auth.py and contains methods for making get requests to KrogerAPI, searching for products, and getting location information.

3. KrogerLocation.py - Used to create an object representing a single Kroger Location. Each location object contains the store id, name, and address.

4. KrogerProduct.py - Userd to create an object representing a single product. Each product object contains data on the product id, UPC code, brand, description, image, size, and price.
 
5. FindMatchesKroger.py - `FindMatchesKroger` class receives a dataframe of item information extracted from a receipt, and a zipcode. It finds stores close to the zipcode, expands the abbreviations on the receipt using the `Abbreviations.csv` file, and finds product matches in the Kroger inventory.

6. OCR2.py - Uses AWS textract to conduct OCR on uploaded receipt image. Contains 2 different methods. We found method 1 works best on receipts.

7. PriceAnalysis.py -   `ComparePrices` class receives a selected item info, its price, a selected store, and a list of nearby results. Its methods allows for finding lowest priced item at nearby stores, the mean price for the selected item, a list of prices, the standard deviation of prices, and contains various string formating methods for displaying price statistics.

8. S3Images.py - `S3Images` class allows for file upload and download to AWS S3 bucket.

9. helper.py  - helper functions to clean up AWS textract OCR output json objects and reformat into dataframes

10. Abbreviations.csv - csv with commonly found abbreviations

11. raw_web_joined.csv - csv with scraped abbreviations from receipts

## Reflections and Future Work
While we have made significant progress toward our goal product, there are a few aspects that require future work:

1. More filtering can be done to refine product search using API (chain, brand)
2. More research into natural language understanding for abbreviations and utimately item matching from uploaded recipts.
   We recently found a paper that used Apache Lucene which could be a good starting point (linked in references). Others have used CNN models too. 
3. We would like to link the application with multiple APIs (i.e. Walmart, Stop & Shop, etc)
4. Including some parallel processing might help with speed of item and matching and lookup
5. Formatting the application into an ios or android app with live photo capture capability
6. Improving the accuracy of the matches
7. Speed up the computation through parallel processing
8. More accurately displaying store information (i.e. Store Name, address). This has been a challenge because some receipt only include the store name within a logo with different typeface than the remainder of the text on the receipt.   

We also have a few ideas for future growth of the project:

1. Understanding consumer sentiments from the data collected through the app
2. Offering a "smart shopping" feature that recommends similar products for lower prices or healthier products

## References:

1. https://github.com/jtbricker/python-kroger-client/tree/master/python_kroger_client
2. https://developer.kroger.com/reference/
3. https://github.com/srcecde/aws-tutorial-code/blob/master/textract/analyze-expense/sync/lambda_function.py
4. https://gist.github.com/ghandic/a48f450f3c011f44d42eea16a0c7014d
5. https://deepai.org/publication/understanding-scanned-receipts
6. https://github.com/ericmelz/XCS224U-Project





