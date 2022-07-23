import cv2, numpy
from PIL import Image

def Resize(image, width, height):
    img = Image.open(image)
    img = img.resize((width, height)).save(image, quality=95)
    return True

def Paste(image1, image2, x_y):
    im1 = Image.open(image1)
    im2 = Image.open(image2)
    im2 = im2.resize((20, 20))
    im1.paste(im2, (x_y[0], x_y[1]), im2)
    im1.save(image1, quality=95)
    return True

def Is_selected(image, x, y, radius):
    img = cv2.imread(image)
    position = [x, y]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_range = numpy.array([110, 50, 50])
    upper_range = numpy.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_range, upper_range)
    kernel = numpy.ones((7, 7), numpy.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pixels = {}
    for ch in range(len(contours)):
        data = []
        for sw in range(len(contours[ch])):
            data.append([contours[ch][sw][0][0], contours[ch][sw][0][1]])
            pixels[ch + 1] = data
    for key, ch in pixels.items():
        correct = []
        for sw in ch:
            if abs(sw[0] - position[0]) < 30 and abs(sw[1] - position[1]) < 30:
                correct.append(sw)
        if len(ch) == len(correct):
            position.append(True)
            break
    if len(position) < 3: position.append(False)
    return position

def Find_Circles(image, circle_image, size):
    Circles = []
    Resize(image, size[0], size[1])
    src = cv2.imread(cv2.samples.findFile(image), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 300, param1=100, param2=40, minRadius=7, maxRadius=90)
    if circles is not None:
        circles = numpy.uint16(numpy.around(circles))
        for i in circles[0, :]:
            x = i[0]
            y = i[1]
            radius = i[2]
            center = (i[0], i[1])
            check = Is_selected(image, x, y, radius)
            Circles.append(check)
            if circle_image:
                if check[2]: cv2.circle(src, center, radius, (0, 255, 0), 3)
                else: cv2.circle(src, center, radius, (0, 0, 255), 3)
    if circle_image:
        cv2.imwrite(circle_image, src)
        cv2.waitKey(0)
    return Circles

def Circles(circles):
    return [ch+1 for ch in range(len(circles))]

def Answers(circles):
    return [ch+1 for ch in range(len(circles)) if circles[ch][2]]

def Sort_Column(List):
    for ch in range(len(List)):
        for sw in range(len(List)):
            if List[ch][1] < List[sw][1]:
                tag = List[ch]
                List[ch] = List[sw]
                List[sw] = tag
    return List

def Sort_Row(List, sep, free=True):
    Result, Data = [], []
    for ch in range(len(List)):
        if ch % sep == 0 and ch != 0 or ch == len(List) - 1:
            if ch == len(List) - 1: Data.append(List[ch])
            for ch1 in range(len(Data)):
                for sw in range(len(Data)):
                    if Data[ch1][0] < Data[sw][0]:
                        tag = Data[ch1]
                        Data[ch1] = Data[sw]
                        Data[sw] = tag
            if free:
                for sw in Data: Result.append(sw)
            else: Result.append(Data)
            Data = []
        Data.append(List[ch])
    return Result

def Last_Rows(List, last=2, choice=4):
    Row = []
    for ch in range(len(List)):
        if ch >= len(List) - last and ch < len(List):
            for sw in List[ch]: Row.append(sw)
    Row = Sort_Column(Row)
    Row = Sort_Row(Row, choice, False)
    counter = 0
    for ch in range(len(List)):
        if ch >= len(List) - last and ch < len(List):
            List[ch] = Row[counter]
            counter += 1
    return List

def Sort(list_circles, direction):
    first, second = [], []
    for ch in range(len(list_circles)):
        if (ch + 1) % 2 != 0:
            pre = int(list_circles[ch-2][0][0])
            cur = int(list_circles[ch][0][0])
            if cur - pre < 100:
                first.append(list_circles[ch])
            else: second.append(list_circles[ch])
        else: second.append(list_circles[ch])
    if direction == "ltr": return first + second
    return second + first

def Scann(image, result, direction, q_num, choice):
    if q_num < 20: size = (1282, 1712)
    else: size = (1284, 1712)
    list_circles = Find_Circles(image, result, size)
    list_circles = Sort_Column(list_circles)
    list_circles = Sort_Row(list_circles, choice * 2, True)
    list_circles = Sort_Row(list_circles, choice, False)
    if q_num % 2 != 0: list_circles = Last_Rows(list_circles, 1, choice)
    if q_num == 6: list_circles = Last_Rows(list_circles, 2, choice)

    list_circles = Sort(list_circles, direction)
    List = {}
    for ch in range(len(list_circles)):
        answer = ch + 1
        add = 0
        if direction != "ltr": list_circles[ch].reverse()
        for sw in range(len(list_circles[ch])):
            if list_circles[ch][sw][2]:
                List[answer] = sw + 1
                add += 1
        if not add or add > 1: List[answer] = "-"
    return List
