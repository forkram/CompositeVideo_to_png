import csv
from PIL import Image

with open('grayramp_line28_NoHblank.csv', newline='') as f:
    reader = csv.reader(f)
    sum_ = 0
    count = 0
    pixelNumber = 0
    avgVoltagePerNESpixel = 0.0
    PixelRGBValue = []

    for row in reader:
        sum_ += float(row[0])
        count += 1
        if count >= 186:
            pixelNumber += 1
            avgVoltagePerNESpixel = (sum_ / count)
            # if reader.line_num == 186:#reader is the indexer!!
            #  print(type(avgVoltagePerNESpixel))
            #  print(avgVoltagePerNESpixel)
            if -0.20 < avgVoltagePerNESpixel <= -0.0217:
                # print("Pixel Number ", pixelNumber, "is black")
                PixelRGBValue.append((0, 0, 0))
            elif -0.0217 < avgVoltagePerNESpixel <= 0.17743:
                # print("Pixel Number ", pixelNumber, "is DimGray")
                PixelRGBValue.append((105, 105, 105))
            elif 0.17743 < avgVoltagePerNESpixel <= 0.26982:
                # print("Pixel Number ", pixelNumber, "is Gray")
                PixelRGBValue.append((128, 128, 128))
            elif 0.26982 < avgVoltagePerNESpixel <= 0.35853:
                # print("Pixel Number ", pixelNumber, "is DarkGray")
                PixelRGBValue.append((169, 169, 169))
            elif 0.35853 < avgVoltagePerNESpixel <= 0.44725:
                # print("Pixel Number ", pixelNumber, "is Silver")
                PixelRGBValue.append((192, 192, 192))
            elif 0.44725 < avgVoltagePerNESpixel <= 0.53963:
                # print("Pixel Number ", pixelNumber, "is LightGray")
                PixelRGBValue.append((211, 211, 211))
            elif 0.53963 < avgVoltagePerNESpixel <= 0.63178:
                # print("Pixel Number ", pixelNumber, "is Gainsboro")
                PixelRGBValue.append((220, 220, 220))
            elif avgVoltagePerNESpixel > 0.63178:
                # print("Pixel Number ", pixelNumber, "is White")
                PixelRGBValue.append((255, 255, 255))

            # reset average
            sum_ = 0
            count = 0
    # Are there any samples left over? Add to list if so
    if count > 0:
        pixelNumber += 1
        avgVoltagePerNESpixel = (sum_ / count)
        if -0.20 < avgVoltagePerNESpixel <= -0.0217:
            # print("Pixel Number ", pixelNumber, "is black")
            PixelRGBValue.append((0, 0, 0))
        elif -0.0217 < avgVoltagePerNESpixel <= 0.17743:
            # print("Pixel Number ", pixelNumber, "is DimGray")
            PixelRGBValue.append((105, 105, 105))
        elif 0.17743 < avgVoltagePerNESpixel <= 0.26982:
            # print("Pixel Number ", pixelNumber, "is Gray")
            PixelRGBValue.append((128, 128, 128))
        elif 0.26982 < avgVoltagePerNESpixel <= 0.35853:
            # print("Pixel Number ", pixelNumber, "is DarkGray")
            PixelRGBValue.append((169, 169, 169))
        elif 0.35853 < avgVoltagePerNESpixel <= 0.44725:
            # print("Pixel Number ", pixelNumber, "is Silver")
            PixelRGBValue.append((192, 192, 192))
        elif 0.44725 < avgVoltagePerNESpixel <= 0.53963:
            # print("Pixel Number ", pixelNumber, "is LightGray")
            PixelRGBValue.append((211, 211, 211))
        elif 0.53963 < avgVoltagePerNESpixel <= 0.63178:
            # print("Pixel Number ", pixelNumber, "is Gainsboro")
            PixelRGBValue.append((220, 220, 220))
        elif avgVoltagePerNESpixel > 0.63178:
            # print("Pixel Number ", pixelNumber, "is White")
            PixelRGBValue.append((255, 255, 255))

# print(PixelRGBValue)
# print(type(PixelRGBValue))

img = Image.new('RGB', (pixelNumber, 1), 255)
img.putdata(PixelRGBValue)
img.save('OneScanline_1.png')
