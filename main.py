import cv2
import os
from vidgear.gears import CamGear
import time
import read_pic_to_text as rd_pic


def start_stream(youtube):
    stream = CamGear(
        source= youtube,
        stream_mode=True,
        time_delay=1,
        logging=True,
    ).start()
    path = "pic"
    currentframe = 0
    while True:

        frame = stream.read()  ### using functions from vidGear module
        if frame is None:
            break
        cv2.imshow("Output Frame", frame)  # optional if u want to show the frames
       # name = path + "./frames" + str(currentframe) + ".jpg"
        name = path + "./frames" + str(currentframe) + ".jpg"
        # print("Creating..." + name)
        cv2.imwrite(name, frame)
        # currentframe += 0  ##chnage 5 with the number of frames. Here 5 means capture frame after every 5 frames
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        # try:
        #     print(rd_pic.readpic(name))
        # except IndexError:
        #     continue
        #
        #
        # time.sleep(2)

    cv2.destroyAllWindows()
    stream.stop()

if __name__ == "__main__":
    start_stream("https://www.youtube.com/live/wDQSnyivEJs")
