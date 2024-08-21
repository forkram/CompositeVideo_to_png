# IMPORT'S and FROM'S
import csv
from datetime import datetime
import math
import numpy as np
from PIL import Image
# from statistics import median
from statistics import fmean
# from statistics import mode
# from statistics import median_low
# from statistics import median_high
from numpy import average
import os.path


# ========================================================
# FUNCTIONS
# ========================================================
def four_figs(value):
    return int(value * 1000) / 1000


def PostPixelData():
    return PostPixelDataRows.append([HsyncCount, pixelNumber, PixelRGBString,
                                     PixelGreyScaleString, avghilow,
                                     LumaIRE, four_figs(Y),
                                     four_figs(U), four_figs(V),
                                     max(PixelData), min(PixelData),
                                     four_figs(AmplitudeIRE),
                                     PixelStartIndex, PixelEndIndex,
                                     HighestColorIndex, HighestBurstIndex, phase,
                                     LowestColorIndex, LowestBurstIndex])


# ========================================================
# Library/Package versions at the time of creation
# ========================================================
# PIL (pillow) 9.50 to 10.0.1
# numpy 1.26.0

# ========================================================
# Special thanks to:
# Persune https://gumball2415.github.io/
# https://codeandlife.com/2012/10/09/composite-video-decoding-theory-and-practice/

# ========================================================
# FILE & SAMPLE RATE INFORMATION
# ========================================================
# SMB_1X_Fine_125MSa2.csv
# ColorBars_AC1X_Course_125MSa.csv
# SolidRed_AC1X_Course_125MSa.csv
# SolidBlack_AC1X_Course_125MSa.csv
# SolidBlue_AC1X_Course_125MSa.csv
# SolidWhite_AC1X_Course_125MSa.csv
# ^____^____^____^____^____^ sample rate is 125M Sa/s = 125 * 10 ** 6
# ======================================== ENTER MANUALLY ===========================
# SamplesPerSecond **********************\               /***************************
# filename *******************************\             /****************************
# SaveFileName ****************************\           /*****************************
# WritePrePixelDataToFile ******************\         /******************************
# WritePostPixelDataToFile ******************\       /*******************************
# DrawGreyImageFile **************************\     /********************************
# DrawColorImageFile **************************\   /*********************************
# **********************************************\ /**********************************
#
SamplesPerSecond = 125 * 10 ** 6
filename = "SMB_1X_Fine_125MSa2.csv"  # input  filename to open from the "InputFiles" folder
WritePrePixelDataToFile = False       # Append pre pixel data to write to csv file for debugging
WritePostPixelDataToFile = False      # Append post pixel data to write to csv file for debugging
DrawGreyImageFile = True              # Draw grey scale image to png file
DrawColorImageFile = True             # Draw color image to png file
# ========================================= ENTER MANUALLY ===========================
# **********************************************/ \**********************************
# *********************************************/   \*********************************
# ********************************************/     \********************************
FilenamePath = (os.path.abspath('./InputFiles/' + filename))
SaveFileName = ('_' + filename)  # output filename prefix saved to the "OutputFiles" folder
# print('Input filename Path = ' + FilenamePath)
SecondsPerSample = 1 / SamplesPerSecond
print("===================================")
print("CSV file name:")
print(">>", filename)
print("SamplesPerSecond    =", SamplesPerSecond)
print("SecondsPerSample    =", SecondsPerSample)

# ========================================================
# NES TIMING CONSTANTS
# ========================================================
SecondsPerPixel = 1.862434 * 10 ** -7  # PPU CLOCK RATE
PixelsPerSecond = 1 / SecondsPerPixel
SamplesPerPixel = SamplesPerSecond * SecondsPerPixel
# Color burst frequency (fsc) 3.579545...MHz +-10 Hz ((1 / fsc) * SamplesPerSecond)
fsc = (5 * 10 ** 6) * (63 / 88)
print("SamplesPerPixel                =", four_figs(SamplesPerPixel))
print("fsc colorburst (MHz)           =", four_figs(fsc / 1000000))
print("PixelsPerSecond (MHz)          =", four_figs(PixelsPerSecond / 1000000))
SamplesPerBurstCycle = int(((1 / fsc) * SamplesPerSecond))
print("Samples needed per busrt cycle =", SamplesPerBurstCycle)
print("===================================")
# exit()
# ========================================================
# SYNC VARIABLES
# ========================================================
HsyncSampleCounter = 0
HsyncCount = 0
HSync_sum = 0
EndOfHsyncIndex = 0
SyncVoltageAvg = 0
Sync_sum = 0
VsyncCount = 0
VsyncSampleCounter = 0
EndOfVsyncIndex = 0
Vsync_sum = 0
VSyncVoltageAvg = 0
# HOW MANY SAMPLES DO WE NEED TO IDENTIFY THE HSYNC PULSE?
#   HSync pulse is ~25 NES pixels long -or- ~4.7 ±1µs -or- ~4.656085 E-06s
#   Let's do 5% less samples needed ---> 25-5% = 23.75
MinimumHsyncSamples = 23.75 * SamplesPerPixel
# HOW MANY SAMPLES DO WE NEED TO IDENTIFY THE VSYNC PULSE?
#   VSync pulse is ~59 µs -or- ~59 E-06s
#   Let's do 5% less samples needed ---> 56 µs -or- ~56 E-06s
MinimumVsyncSamples = SamplesPerSecond * (56 * 10 ** -6)
# print("MinimumVsyncSamples        =", int(MinimumVsyncSamples))
# print("MinimumHsyncSamples        =", four_figs(MinimumHsyncSamples))
RBPLCount = 0  # RBPL = Remaining Blanking Period Lines
RBLSync_sum = 0
RBPLSampleCounter = 0

# ========================================================
# unsorted variables
# ========================================================
VBIcount = 0
LowestValueFound = False
LumaIRE = 0
PreLumaIRE = 0
ColorCycleCounter = 0
timestamp = datetime.now().strftime("_%m_%d_%Y-%I_%M_%p")
# print("timestamp =", timestamp)
PostPixelDebugFileName = SaveFileName + "Post" + timestamp + ".csv"
PrePixelDebugFileName = SaveFileName + "Pre" + timestamp + ".csv"
BurstDebugFileName = SaveFileName + "Burst" + timestamp + ".csv"
U_window_average = 0
U_moving_average = []
V_window_average = 0
V_moving_average = []
BurstDataDebug = []
# ========================================================
# BURST VARIABLES
# ========================================================
BurstData = []
HighestBurstValue = -99999
HighestBurstIndex = 0
LowestBurstValue = 99999
LowestBurstIndex = -1
BusrtSinDebug = 0
BusrtCosDebug = 0
# exit()

# ========================================================
# PIXEL VARIABLES
# ========================================================
PixelData = []
avgVoltagePerNESpixel = 0.0

PixelRGBList = []
PixelRGBString = ""
PixelGreyScaleList = []
PixelGreyScaleString = ""
PreviousOddPixel_x = 0
MixedPixel = 0
pixelNumber = 0
SamplesPerPixelCounter = 0
PixelStartIndex = 0
PixelEndIndex = 0
# exit()
HighestColorValue = -99999
HighestColorIndex = 0
LowestColorValue = -99999
LowestColorIndex = 0
U_buffermul1 = []
U_buffermul1Debug = 0.0
V_bufferDebug = 0.0
V_buffer = []
U = 0
Y = 0

t = 0  # Time counter for burst lock
nIRE = 0  # voltage to IRE
RGB_per_pixel = [0.0, 0.0, 0.0]
R = 0
G = 0
B = 0

# ========================================================
# Debug variables, lists, arrays
# ========================================================
# TODO add voltage min + max / 2
PrePixelDataHeader = ['Line', 'Cycle', 'Raw V', 'VGA V', 'N(IRE)', 't', 'BurstSin',
                      'mul1', 'U', 'BurstCos', 'mul2', 'V', 'index']
PrePixelDataRows = []

PostPixelDataHeader = ["Line", 'Pixel', 'RGB', 'Grey', 'LumaVGA', 'LumaIRE', 'Y', 'U', 'V',
                       'VrawHi', 'VrawLow', 'AmpIRE', 'PixelIndexBegin', 'PixelIndexEnd',
                       'HiCIndex', 'HiBIndex', 'phaseDeg', 'LoCIndex', 'LoBIndex', ]

PostPixelDataRows = []

# ========================================================
# OPEN OSCILLOSCOPE DATA CSV FILE TO ESTABLISH SYNC LEVELS
# ========================================================
SyncSampleCounter = 0
SyncLevelVoltageAvg = 0
SyncVoltageAvgTotal = 0
SyncLevelCount = 0
NewList = []
with open(FilenamePath, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        # let's scan a few scanlines worth of data only
        # Full scanline is ~63.5 µs -or- ~63.5 E-06s
        if reader.line_num < (SamplesPerSecond * (320 * 10 ** -6)):
            NewList.append(float(row[0]))
        if reader.line_num == (SamplesPerSecond * (320 * 10 ** -6)):
            NewList.sort(reverse=False)
            sort10 = NewList[:10]
            AvgLowestValue = sum(sort10) / len(sort10)
            # ******************************************************
            # ******************************************************
            # ******************************************************
            # TODO: REDO HOW I FIND AvgLowestValue VALUE USING STATISTICS
            # ******************************************************
            # ******************************************************
            # ******************************************************
            # print("average of 10 lowest sync voltages =", four_figs(AvgLowestValue))
        if reader.line_num >= (SamplesPerSecond * (320 * 10 ** -6)):
            # ---------------------------------------
            # Find sync level average voltage
            # ---------------------------------------
            if float(row[0]) <= AvgLowestValue:
                LowestValueFound = True
            if LowestValueFound:
                if SyncSampleCounter < MinimumHsyncSamples:
                    Sync_sum += float(row[0])
                    SyncSampleCounter += 1
                elif SyncSampleCounter >= MinimumHsyncSamples:
                    # Found the first Hsync with minimum samples needed
                    SyncLevelVoltageAvg = (Sync_sum / SyncSampleCounter)
                    SyncLevelCount += 1
                    SyncVoltageAvgTotal += SyncLevelVoltageAvg
                    SyncVoltageAvg = (SyncVoltageAvgTotal / SyncLevelCount)
                    # reset counters
                    SyncSampleCounter = 0
                    SyncLevelVoltageAvg = 0
                    Sync_sum = 0
                    LowestValueFound = False
            if SyncLevelCount == 100:
                break
print("SyncLevelCount             =", SyncLevelCount)
print("SyncVoltageAvg             =", four_figs(SyncVoltageAvg))
# ========================================================
# Adjust voltage gain for proper IRE usage
# ========================================================
VoltageGainAdjust = four_figs(float((-0.286) - SyncVoltageAvg))
print("VoltageGainAdjustment(VGA) =", four_figs(VoltageGainAdjust))
print("VGA Sync Value             =", four_figs((SyncVoltageAvg + VoltageGainAdjust)))
# exit()
# ========================================================
# SYNC VOLTAGE THRESHOLD
# ========================================================
#   is the value BELOW this level to look for Hsync samples
#   The bottom level of the color burst should be at 20 IRE, which is 20% from Sync level IRE 40
SyncThreshold = SyncVoltageAvg + (abs(SyncVoltageAvg) * 0.20)
BlankLevel = SyncVoltageAvg + 0.286
print("SyncThreshold              =", four_figs(SyncThreshold))
print("Blank level                ~", four_figs(BlankLevel))
print("VGA Blank level            =", four_figs((BlankLevel + VoltageGainAdjust)))
# exit()
# ===============================================
# OPEN OSCILLOSCOPE DATA CSV FILE FOR PROCESSING
# ===============================================
with (open(FilenamePath, newline='') as f):
    reader = csv.reader(f)
    for row in reader:  # LOOP THROUGH EACH VALUE IN THE CSV FILE
        if float(row[0]) < SyncThreshold and VsyncSampleCounter < MinimumVsyncSamples and \
                VsyncCount <= 3 and EndOfVsyncIndex == 0:
            Vsync_sum += float(row[0])
            VsyncSampleCounter += 1
        elif VsyncSampleCounter >= MinimumVsyncSamples and VsyncCount < 3:
            VsyncCount += 1
            VsyncSampleCounter = 0
            Vsync_sum = 0
            # if VsyncCount == 1:
            #     print(" ")
            #     print("At the end of the first Vsync")
            #     print("Index number =", reader.line_num)
            #     # print("Voltage value found at this index =", row[0])
            # if VsyncCount == 2:
            #     print(" ")
            #     print("At the end of the second Vsync")
            #     print("Index number =", reader.line_num)
            #     # print("Voltage value found at this index =", row[0])
            if VsyncCount == 3:
                VBIcount += 1
        elif float(row[0]) > SyncThreshold and VsyncCount < 3 and EndOfVsyncIndex == 0:
            Vsync_sum = 0
            VsyncSampleCounter = 0
        elif float(row[0]) > SyncThreshold and VsyncCount == 3 and EndOfVsyncIndex == 0:
            # THE END OF FIELD SYNC PERIOD
            # print("--------------------------------------------")
            EndOfVsyncIndex = reader.line_num
            print("EndOfVsyncIndex            =", EndOfVsyncIndex)
            print("===================================")
        elif EndOfVsyncIndex > 0:
            #     # NEED TO GET TO THE END OF THE FIELD BLANKING PERIOD
            #     # NEED TO SKIP 14 VBI SCANLINES (14 Hsync pulses)
            #     # THE NEXT (15th) SCANLINE IS THE START OF THE FIELD
            #     # RBPL = Remaining Blanking Period Lines
            if float(row[0]) < SyncThreshold and RBPLSampleCounter < MinimumHsyncSamples and RBPLCount < 14:
                RBLSync_sum += float(row[0])
                RBPLSampleCounter += 1
            elif float(row[0]) < SyncThreshold and RBPLSampleCounter >= MinimumHsyncSamples and RBPLCount < 14:
                RBLSync_sum += float(row[0])
                RBPLSampleCounter += 1
            elif float(row[0]) > SyncThreshold and RBPLSampleCounter >= MinimumHsyncSamples and RBPLCount < 14:
                RBPLCount += 1
                RBPLSampleCounter = 0
            elif RBPLCount == 14:  # Now start the field at the next Hsync pulse
                # ==========================================================================
                # HsyncCount = 0 is the first scanline of the field
                # ==========================================================================
                if HsyncCount <= 242:  # 262 total lines minus 20 vertical blanking lines
                    if float(row[0]) < SyncThreshold and HsyncSampleCounter < MinimumHsyncSamples:
                        HSync_sum += float(row[0])
                        HsyncSampleCounter += 1
                    elif float(row[0]) < SyncThreshold and HsyncSampleCounter >= MinimumHsyncSamples \
                            and EndOfHsyncIndex == 0:
                        # Found the first Hsync with minimum samples needed
                        HSync_sum += float(row[0])
                        HsyncSampleCounter += 1
                    elif float(row[0]) > SyncThreshold and HsyncSampleCounter >= MinimumHsyncSamples \
                            and EndOfHsyncIndex == 0:
                        HsyncCount += 1  # Now count Hsync found
                        # ===================================================
                        # END OF H-SYNC (or the beginning of the back porch)
                        # ===================================================
                        EndOfHsyncIndex = reader.line_num
                        HSync_sum = 0
                        # BurstDataDebug = []
                    elif EndOfHsyncIndex > 0 and reader.line_num < (EndOfHsyncIndex + int(24 * SamplesPerPixel)):
                        # ===================================================
                        # BURST SIGNAL
                        # ===================================================
                        if float(row[0]) > HighestBurstValue:
                            HighestBurstIndex = reader.line_num  # SIN(PI/2)
                            LastHighBurstIndex = reader.line_num  # FIXME I don't think im using this
                        if float(row[0]) < LowestBurstValue:
                            LowestBurstIndex = reader.line_num
                            LastLowBurstIndex = reader.line_num  # FIXME I don't think im using this
                        BurstData.append(float(row[0]))
                        HighestBurstValue = max(BurstData)
                        LowestBurstValue = min(BurstData)
                        if WritePrePixelDataToFile and HsyncCount == 42:
                            # BurstDataDebug.append([HsyncCount, reader.line_num, float(row[0])])
                            BurstDataDebug.append([float(row[0])])
                    elif EndOfHsyncIndex > 0 and reader.line_num >= (EndOfHsyncIndex + int(24 * SamplesPerPixel)):
                        # ==========================================================================
                        # This is the beginning of the first pixel
                        # ==========================================================================
                        t = ((reader.line_num - HighestBurstIndex) * SecondsPerSample) + 3 / (fsc * 4)  # FIXME
                        nIRE = (float(row[0]) + VoltageGainAdjust) * 140.06
                        if SamplesPerPixelCounter == 0:
                            PixelStartIndex = reader.line_num
                        SamplesPerPixelCounter += 1
                        if SamplesPerPixelCounter <= SamplesPerBurstCycle:
                            if float(row[0]) >= HighestColorValue:
                                HighestColorIndex = reader.line_num
                            if float(row[0]) <= LowestColorValue:
                                LowestColorIndex = reader.line_num  # FIXME I don't think im using this
                            PixelData.append(float(row[0]))
                            HighestColorValue = max(PixelData)
                            LowestColorValue = min(PixelData)
                            # ===================================================
                            #  Find U
                            # ===================================================
                            BusrtSinDebug = math.sin(2 * math.pi * fsc * t)
                            # U_buffermul1.append(nIRE * math.sin(2 * math.pi * fsc * t))
                            U_buffermul1Debug = four_figs(nIRE * math.sin(2 * math.pi * fsc * t))
                            # calculate moving average of U_buffermul1 in window size SamplesPerBurstCycle
                            window_size = int(SamplesPerBurstCycle)
                            U_moving_average.append(U_buffermul1Debug)
                            if len(U_moving_average) > window_size:
                                # U_moving_average.pop(0)
                                del U_moving_average[0]
                            U_window_average = average(U_moving_average)
                            # print("array", U_moving_average)
                            # print("array length", len(U_moving_average))
                            # print("array sum", sum(U_moving_average))
                            # print("array avg", average(U_moving_average))
                            # exit()
                            # ===================================================
                            #  Find V
                            # ===================================================
                            BusrtCosDebug = math.cos(2 * math.pi * fsc * t)
                            # V_buffer.append(nIRE * math.cos(2 * math.pi * fsc * t))
                            V_bufferDebug = four_figs(nIRE * math.cos(2 * math.pi * fsc * t))
                            V_moving_average.append(V_bufferDebug)
                            if len(V_moving_average) > window_size:
                                # V_moving_average.pop(0)
                                del V_moving_average[0]
                            V_window_average = average(V_moving_average)
                            if WritePrePixelDataToFile and HsyncCount == 42:
                                # ===================================================
                                # Append pre pixel data to write to csv file for debugging
                                # ===================================================
                                PrePixelDataRows.append([HsyncCount, ColorCycleCounter + 1, four_figs(float(row[0])),
                                                         four_figs(float(row[0])) + four_figs(VoltageGainAdjust),
                                                         nIRE, t, BusrtSinDebug,
                                                         U_buffermul1Debug,
                                                         U_window_average * 4 * 1.097, BusrtCosDebug,
                                                         V_bufferDebug,
                                                         V_window_average * 2 * 1.232, reader.line_num])
                            if SamplesPerPixelCounter == SamplesPerBurstCycle:
                                # ==========================================================================
                                # This is the end of each chroma cycle
                                # There are 3 pixels per 2 chroma cycles.
                                # Pixel 2 of 3 shares chroma info from each chroma cycle
                                # ==========================================================================
                                ColorCycleCounter += 1
                                phase = int((HighestColorIndex - HighestBurstIndex) * fsc * 360)
                                avgVoltagePerNESpixel = fmean(PixelData)
                                PixelEndIndex = reader.line_num
                                x = int((avgVoltagePerNESpixel + VoltageGainAdjust) * 1.4006 * 255)
                                # x = Greyscale RGB integer value
                                # 1.4006 is the IRE multiplier/100
                                # 255 is the grey scale multiplier
                                if x < 0:
                                    x = 0
                                AmplitudeIRE = (((max(PixelData) + VoltageGainAdjust) -
                                                 (min(PixelData) + VoltageGainAdjust)) * 140.06)
                                if AmplitudeIRE < 0:
                                    AmplitudeIRE = 0
                                # TODO get rid of avghilow - same as LumaIRE
                                avghilow = four_figs(
                                    ((max(PixelData) + min(PixelData) + (2 * VoltageGainAdjust)) / 2))
                                # ===================================================
                                #  Find Luma
                                # ===================================================
                                LumaIRE = four_figs(
                                    ((max(PixelData) + min(PixelData) + (2 * VoltageGainAdjust)) / 2)
                                    * 140.06)
                                if LumaIRE < 0:
                                    LumaIRE = 0
                                if LumaIRE > 100:
                                    LumaIRE = 100
                                # ===================================================
                                #  Assign Y, U, V
                                # ===================================================
                                Y = (LumaIRE - 7.5) / 0.925
                                # Y = (35.2 - 7.5) / 0.925
                                # Tried hard coding Luma for all red screen to figure out streaks
                                # Hard coding luma values didn't make a difference 10-23-23
                                U = U_window_average * 4 * 1.097
                                V = V_window_average * 2 * 1.232
                                YUVmatrix = np.array([Y, U, V])
                                # # YUV to RGB matrix
                                RGBmatrix = np.array([
                                    [1, 0, 1],
                                    [1, -0.194, -0.509],
                                    [1, 1, 0]
                                ], np.float64)
                                # Perform matrix operation to find RGB
                                RGB_per_pixel = np.matmul(RGBmatrix, YUVmatrix)
                                # normalize
                                RGB_per_pixel -= 7.5
                                RGB_per_pixel /= 92.5
                                # clip if values are below zero or above 1
                                RGB_per_pixel = np.clip(RGB_per_pixel, [0], [1])
                                RGB_per_pixel *= 255
                                RGB_per_pixel = RGB_per_pixel.astype(int)
                                # split to individual values to get in list-form for image processing
                                R = RGB_per_pixel[0]
                                G = RGB_per_pixel[1]
                                B = RGB_per_pixel[2]
                                # Process individual pixel RGB values
                                if (ColorCycleCounter % 2) == 0:  # this is even numbered chroma cycle
                                    # -----------------------------------------
                                    # This is the middle pixel that shares chroma info
                                    # -----------------------------------------
                                    pixelNumber = ColorCycleCounter * 1.5 - 1
                                    MixedPixel = int((x + PreviousOddPixel_x) / 2)
                                    # print("pixelNumber =", pixelNumber)
                                    # print("Current pixel x =", x)
                                    # print("PreviousOddPixel_x =", PreviousOddPixel_x)
                                    # print("MixedPixel =", MixedPixel)
                                    # exit()
                                    PixelGreyScaleList.append((MixedPixel, MixedPixel, MixedPixel))
                                    PixelGreyScaleString = (
                                        "{0}-{1}-{2}".format(str(MixedPixel), str(MixedPixel), str(MixedPixel)))
                                    Rr = int((R + PreviousOddPixel_R) / 2)
                                    Gg = int((G + PreviousOddPixel_G) / 2)
                                    Bb = int((B + PreviousOddPixel_B) / 2)
                                    # Append pixel RGB data for picture processing
                                    PixelRGBList.append((Rr, Gg, Bb))
                                    PixelRGBString = str(Rr) + "-" + str(Gg) + "-" + str(Bb)
                                    if WritePostPixelDataToFile:
                                        # Append post pixel data to write to csv file for debugging
                                        PostPixelData()
                                    # -----------------------------------------
                                    # This is the third pixel that uses info from chroma cycle 2
                                    # -----------------------------------------
                                    pixelNumber = ColorCycleCounter * 1.5
                                    PixelGreyScaleList.append((x, x, x))
                                    PixelGreyScaleString = str(x) + "-" + str(x) + "-" + str(x)
                                    # Append pixel RGB data for picture processing
                                    PixelRGBList.append((R, G, B))
                                    PixelRGBString = str(R) + "-" + str(G) + "-" + str(B)
                                    if WritePostPixelDataToFile:
                                        # Append post pixel data to write to csv file for debugging
                                        PostPixelData()
                                if (ColorCycleCounter % 2) != 0:  # this is odd numbered chroma cycle
                                    # -----------------------------------------
                                    # This is the first pixel that uses info from chroma cycle 1
                                    # ----------------------------------------
                                    PreviousOddPixel_x = x
                                    PreviousOddPixel_R = R
                                    PreviousOddPixel_G = G
                                    PreviousOddPixel_B = B
                                    pixelNumber = ColorCycleCounter + int(ColorCycleCounter / 2)
                                    PixelGreyScaleList.append((x, x, x))
                                    PixelGreyScaleString = str(x) + "-" + str(x) + "-" + str(x)
                                    # Append pixel RGB data for picture processing
                                    PixelRGBList.append((R, G, B))
                                    PixelRGBString = str(R) + "-" + str(G) + "-" + str(B)
                                    if WritePostPixelDataToFile:
                                        # Append post pixel data to write to csv file for debugging
                                        PostPixelData()
                                # --------------------------------------------------------------------------
                                # ===================================================
                                # Done processing a single chroma cycle. Reset for next cycle.
                                # ===================================================
                                SamplesPerPixelCounter = 0
                                PixelData = []
                                HighestColorValue = -99999
                                HighestColorIndex = 0
                                LowestColorValue = 99999
                                LowestColorIndex = 0
                                PixelStartIndex = 0
                                PixelEndIndex = 0
                                # MixedPixel = 0
                                # PreviousOddPixel_x = 0
                                # PreviousOddPixel = 0
                                # Luma0to1 = 0
                                # PixelRGBString = ""
                                # HueAngle = 0
                                avghilow = 0
                                LumaIRE = 0
                                # HueAngleRad = 999
                                # U_buffermul1 = []
                                # V_buffer = []
                                U = 0
                                Y = 0
                                t = 0
                                nIRE = 0
                                RGB_per_pixel = [0.0, 0.0, 0.0]
                                # if pixelNumber == 17:
                                #     exit()
                                if ColorCycleCounter == 188:  # if pixelNumber == 282:
                                    # 188 * 1.5 = 282
                                    # print("   At pixel 282 - exiting to next row")
                                    # print("   pixelNumber Index =", reader.line_num)
                                    # print("   Voltage value found at this index =", row[0])
                                    # print("   avgVoltagePerNESpixel =", avgVoltagePerNESpixel)
                                    # print(" ")
                                    # print("******************************")
                                    # print("pixelNumber =", pixelNumber)
                                    # print("PixelRGBList =", PixelRGBList)
                                    # exit()
                                    # ===================================================
                                    # Done processing a single line. Reset counters for next line.
                                    # ===================================================
                                    EndOfHsyncIndex = 0
                                    HsyncSampleCounter = 0
                                    pixelNumber = 0
                                    HighestBurstValue = -99999.99
                                    HighestBurstIndex = 0
                                    LastHighBurstIndex = 0
                                    BurstData = []
                                    # BurstDataDebug = []
                                    LowestBurstValue = 99999
                                    LowestBurstIndex = 99999
                                    LastLowBurstIndex = 0
                                    ColorCycleCounter = 0
                                    U_moving_average = []
                                    V_moving_average = []
                                # End if pixelNumber == 262
                            # End if SamplesPerPixelCounter >= SamplesPerPixel:
                    # End elif EndOfBackPorchIndex > 0
                else:
                    break
                # End if HsyncCount <= 262:
            # End elif RBPLCount == 14
        # End if EndOfVsyncIndex == 0
        # End looking for field sync period
    # End for row in reader
# =========================================
# noinspection PyTypeChecker
# DRAW IMAGE FILE
if DrawGreyImageFile:
    img = Image.new('RGB', (282, HsyncCount - 1), 255)
    img.putdata(PixelGreyScaleList)
    # img.save(SaveFileName + timestamp + '_grey.png')
    img.save((os.path.abspath('./OutputFiles/' + SaveFileName)) + timestamp + '_grey.png')
if DrawColorImageFile:
    imgc = Image.new('RGB', (282, HsyncCount - 1), 255)
    imgc.putdata(PixelRGBList)
    # imgc.save(SaveFileName + timestamp + '_color.png')
    imgc.save((os.path.abspath('./OutputFiles/' + SaveFileName)) + timestamp + '_color.png')
    # print("******************************")
    # print(imgc.size, len(PixelRGBList))

# =========================================
# WRITE PIXEL DEBUG FILEs
if WritePostPixelDataToFile:
    with open((os.path.abspath('./OutputFiles/' + PostPixelDebugFileName)), 'w') as f:
        # with open(PostPixelDebugFileName, 'w') as f:
        write = csv.writer(f, lineterminator='\n')
        write.writerow(PostPixelDataHeader)
        write.writerows(PostPixelDataRows)
if WritePrePixelDataToFile:
    with open((os.path.abspath('./OutputFiles/' + PrePixelDebugFileName)), 'w') as f:
        # with open(PrePixelDebugFileName, 'w') as f:
        write = csv.writer(f, lineterminator='\n')
        write.writerow(PrePixelDataHeader)
        write.writerows(PrePixelDataRows)
    with open((os.path.abspath('./OutputFiles/' + BurstDebugFileName)), 'w') as f:
        # with open(BurstDebugFileName, 'w') as f:
        write = csv.writer(f, lineterminator='\n')
        write.writerows(BurstDataDebug)
# print("******************************")
# print("VBIcount =", VBIcount)
# print("Number of Hsync =", HsyncCount-1)
