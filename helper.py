import sys
import io
import json
import traceback
import pandas as pd
from fuzzywuzzy import fuzz
import csv


def extract_lineitems(lineitemgroups):
    items, price, row, qty = [], [], [], []
    t_items, t_price, t_row, t_qty = [], [], [], []
    t_items, t_price, t_row, t_qty = None, None, None, None
    for lines in lineitemgroups:
        for item in lines["LineItems"]:
            for line in item["LineItemExpenseFields"]:
                if line.get("Type").get("Text") == "ITEM":
                    # t_items.append(line.get("ValueDetection").get("Text", ""))
                    t_items = line.get("ValueDetection").get("Text", "")

                if line.get("Type").get("Text") == "PRICE":
                    # t_price.append(line.get("ValueDetection").get("Text", ""))
                    t_price = line.get("ValueDetection").get("Text", "")

                if line.get("Type").get("Text") == "QUANTITY":
                    # t_qty.append(line.get("ValueDetection").get("Text", ""))
                    t_qty = line.get("ValueDetection").get("Text", "")

                if line.get("Type").get("Text") == "EXPENSE_ROW":
                    # t_row.append(line.get("ValueDetection").get("Text", ""))
                    t_row = line.get("ValueDetection").get("Text", "")

            if t_items:
                items.append(t_items)
            else:
                items.append("")
            if t_price:
                price.append(t_price)
            else:
                price.append("")
            if t_row:
                row.append(t_row)
            else:
                row.append("")
            if t_qty:
                qty.append(t_qty)
            else:
                qty.append("")
            t_items, t_price, t_row, t_qty = None, None, None, None

    #expanded = expand(items)
    #matches = find_matches(expanded)

    df = pd.DataFrame()
    df["items"] = items
    #df["expanded"] = expanded
    df["price"] = price

    df.drop(df.index[-1], inplace=True)
    

    #df["quantity"] = qty
    #df["row"] = row
    #print(df)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    df.to_csv("line_items.csv")

    

    return csv_buffer
    #upload_to_s3(s3_client, csv_buffer, BUCKET_NAME, key)


def extract_kv(summaryfields):
    field_type, label, value = [], [], []
    for item in summaryfields:
        try:
            field_type.append(item.get("Type").get("Text", ""))
        except:
            field_type.append("")
        try:
            label.append(item.get("LabelDetection", "").get("Text", ""))
        except:
            label.append("")
        try:
            value.append(item.get("ValueDetection", "").get("Text", ""))
        except:
            value.append("")

    df = pd.DataFrame()
    #df["Type"] = field_type
    df["Key"] = label
    df["Value"] = value

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    df.to_csv("key_value.csv")

    return csv_buffer
    #upload_to_s3(s3_client, csv_buffer, BUCKET_NAME, key)

def process_error():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(ex_type, ex_value, ex_traceback)
    error_msg = json.dumps(
        {
            "errorType": ex_type.__name__,
            "errorMessage": str(ex_value),
            "stackTrace": traceback_string,
        }
    )
    return error_msg
