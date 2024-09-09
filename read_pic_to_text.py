# Import the necessary libraries
import time
from PIL import Image
import pytesseract

def readpic(picname):
    pytesseract.pytesseract.tesseract_cmd = r"tesseract-ocr\tesseract.exe"
    img = Image.open(picname)
    text = pytesseract.image_to_string(img)
    return text

def write_data_to_file(filename):
    datalist = []
    valueforstrip =".,_|--"
    with open(filename, "w", encoding="utf-8") as file:
        while True:
            try:
                text = readpic(r"pic\frames0.jpg")
                # print(text)
                textsplit = text.split("Comment")[1].split("Balance")[0]
                # print(textsplit)
                data_into_list = textsplit.split("\n")

                for i in data_into_list:
                    data_split = i.split(" ")
                    if len(data_split) > 10:
                        # print(data_split)
                        if int(data_split[1]):
                            # print(data_split[1].strip(valueforstrip),
                            #       data_split[4].strip(valueforstrip),
                            #       data_split[6].strip(valueforstrip),
                            #       data_split[2].strip(valueforstrip),
                            #       data_split[3].strip(valueforstrip))
                            datalist = [data_split[1].strip(valueforstrip),
                                             data_split[4].strip(valueforstrip),
                                             data_split[6].strip(valueforstrip),
                                             data_split[2].strip(valueforstrip),
                                             data_split[3].strip(valueforstrip)]
                            file.write(str(datalist) + "\n")
                            print(datalist)
                # file.write(str(data_into_list) + "\n")
                # print(data_into_list)
            except OSError:
                continue
            else:
                continue
            finally:
                continue
        time.sleep(2)

if __name__ == "__main__":
   write_data_to_file("text_from_pic.txt")

