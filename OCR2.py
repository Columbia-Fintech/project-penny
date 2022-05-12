import boto3
import io
from io import BytesIO
import sys
import math
from PIL import Image, ImageDraw, ImageFont
from S3Images import S3Images
import json
from textractprettyprinter.t_pretty_print_expense import get_string, get_expenselineitemgroups_string
from textractprettyprinter.t_pretty_print_expense import Textract_Expense_Pretty_Print, Pretty_Print_Table_Format
from trp import Document
from helper import process_error, extract_kv, extract_lineitems 
import os
import logging

#Install the latest version of amazon textract response parser 
#python3 -m pip install amazon-textract-response-parser --upgrade
#python3 -m pip install amazon-textract-prettyprinter --upgrade

#OCR class

OCR_OUT = 'outcsv'

class OCR2:

    def __init__(self, s3, image, bucket):

        self.s3 = s3
        self.img = image
        self.bucket = bucket
    
    #Method 1

    def draw_bounding_box(self, key, val, width, height, draw):
    # If a key is Geometry, draw the bounding box info in it
        if "Geometry" in key:
            # Draw bounding box information
            box = val["BoundingBox"]
            left = width * box['Left']
            top = height * box['Top']
            draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])],
                        outline='black')

    # Takes a field as an argument and prints out the detected labels and values
    def print_labels_and_values(self, field):
        # Only if labels are detected and returned
        if "LabelDetection" in field:
            print("Summary Label Detection - Confidence: {}".format(
                str(field.get("LabelDetection")["Confidence"])) + ", "
                + "Summary Values: {}".format(str(field.get("LabelDetection")["Text"])))
            print(field.get("LabelDetection")["Geometry"])
        else:
            print("Label Detection - No labels returned.")
        if "ValueDetection" in field:
            print("Summary Value Detection - Confidence: {}".format(
                str(field.get("ValueDetection")["Confidence"])) + ", "
                + "Summary Values: {}".format(str(field.get("ValueDetection")["Text"])))
            print(field.get("ValueDetection")["Geometry"])
        else:
            print("Value Detection - No values returned")

    
    def process_text_detection(self):

        image, stream = self.s3.from_s3_object(self.bucket, self.img)

        # Detect text in the document
        client = boto3.client('textract', region_name="us-east-1")

        # process using S3 object
        response = client.analyze_expense(
            Document={'S3Object': {'Bucket': self.bucket, 'Name': self.img}})

        
        #print(json.dumps(response))
        for i in response["ExpenseDocuments"]:
            try:
                key_values_csv = extract_kv(i["SummaryFields"])

                key_path = os.path.join(OCR_OUT, "key_value.csv")

                self.s3.to_s3_csv(key_values_csv, self.bucket, key_path)

            except Exception as e:
                error_msg = process_error()
                logging.error(error_msg)
            try:
                line_items_csv = extract_lineitems(i["LineItemGroups"])

                key_path = os.path.join(OCR_OUT, "line_items.csv")

                self.s3.to_s3_csv(line_items_csv, self.bucket, key_path)

            except Exception as e:
                error_msg = process_error()
                logging.error(error_msg)


        """width, height = image.size
        draw = ImageDraw.Draw(image)
        for expense_doc in response["ExpenseDocuments"]:
            for line_item_group in expense_doc["LineItemGroups"]:
                for line_items in line_item_group["LineItems"]:
                    for expense_fields in line_items["LineItemExpenseFields"]:
                        self.print_labels_and_values(expense_fields)
                        print()
            print("Summary:")
            for summary_field in expense_doc["SummaryFields"]:
                self.print_labels_and_values(summary_field)
                print()
            #For draw bounding boxes
            for line_item_group in expense_doc["LineItemGroups"]:
                for line_items in line_item_group["LineItems"]:
                    for expense_fields in line_items["LineItemExpenseFields"]:
                        for key, val in expense_fields["ValueDetection"].items():
                            if "Geometry" in key:
                                self.draw_bounding_box(key, val, width, height, draw)
            for label in expense_doc["SummaryFields"]:
                if "LabelDetection" in label:
                    for key, val in label["LabelDetection"].items():
                        self.draw_bounding_box(key, val, width, height, draw)"""
        #show image
        #image.show()
        #print(response)

        return key_values_csv, line_items_csv


    
    #METHOD 2
    def ShowBoundingBox(self, draw,box,width,height,boxColor):
             
        left = width * box['Left']
        top = height * box['Top'] 
        draw.rectangle([left,top, left + (width * box['Width']), top +(height * box['Height'])],outline=boxColor)   


    def ShowSelectedElement(self, draw,box,width,height,boxColor):
                
        left = width * box['Left']
        top = height * box['Top'] 
        draw.rectangle([left,top, left + (width * box['Width']), top +(height * box['Height'])],fill=boxColor)  

    # Displays information about a block returned by text detection and text analysis
    def DisplayBlockInformation(self, block):
        print('Id: {}'.format(block['Id']))
        if 'Text' in block:
            print('    Detected: ' + block['Text'])
        print('    Type: ' + block['BlockType'])
    
        if 'Confidence' in block:
            print('    Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

        if block['BlockType'] == 'CELL':
            print("    Cell information")
            print("        Column:" + str(block['ColumnIndex']))
            print("        Row:" + str(block['RowIndex']))
            print("        Column Span:" + str(block['ColumnSpan']))
            print("        RowSpan:" + str(block['ColumnSpan']))    
        
        if 'Relationships' in block:
            print('    Relationships: {}'.format(block['Relationships']))
        print('    Geometry: ')
        print('        Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
        print('        Polygon: {}'.format(block['Geometry']['Polygon']))
        
        if block['BlockType'] == "KEY_VALUE_SET":
            print ('    Entity Type: ' + block['EntityTypes'][0])
        
        if block['BlockType'] == 'SELECTION_ELEMENT':
            print('    Selection element detected: ', end='')

            if block['SelectionStatus'] =='SELECTED':
                print('Selected')
            else:
                print('Not selected')    
        
        if 'Page' in block:
            print('Page: ' + block['Page'])
        print()


    def process_text_analysis(self):

        #Get the document from S3
        image, stream = self.s3.from_s3_object(self.bucket, self.image)

        # Analyze the document
        client = boto3.client('textract')
        
        image_binary = stream.getvalue()
        response = client.analyze_document(Document={'Bytes': image_binary},
            FeatureTypes=["TABLES", "FORMS"])
        
        #Get the text blocks
        blocks=response['Blocks']
        width, height =image.size  
        draw = ImageDraw.Draw(image)  
        print ('Detected Document Text')
        
        # Create image showing bounding box/polygon the detected lines/text
        for block in blocks:

            self.DisplayBlockInformation(block)
                
            draw=ImageDraw.Draw(image)
            if block['BlockType'] == "KEY_VALUE_SET":
                if block['EntityTypes'][0] == "KEY":
                    self.ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height,'red')
                else:
                    self.ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height,'green')  
                
            if block['BlockType'] == 'TABLE':
                self.ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height, 'blue')

            if block['BlockType'] == 'CELL':
                self.ShowBoundingBox(draw, block['Geometry']['BoundingBox'],width,height, 'yellow')
            if block['BlockType'] == 'SELECTION_ELEMENT':
                if block['SelectionStatus'] =='SELECTED':
                    self.ShowSelectedElement(draw, block['Geometry']['BoundingBox'],width,height, 'blue')    
    
                #uncomment to draw polygon for all Blocks
                #points=[]
                #for polygon in block['Geometry']['Polygon']:
                #    points.append((width * polygon['X'], height * polygon['Y']))
                #draw.polygon((points), outline='blue')
                
        # Display the image
        image.show()
        #return len(blocks)