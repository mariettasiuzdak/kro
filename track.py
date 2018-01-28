# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import smtplib

# define the lower and upper color boundaries
lower = (100, 051, 000)
upper = (226, 255, 255)

camera = cv2.VideoCapture(1)

gmail_user = 'kronotification@gmail.com'  
gmail_password = 'notification2018'

sent_from = gmail_user
to = 'marietta.siuzdak@gmail.com'
subject = 'You forgot about something'
email_text = 'Hey, you forgot to take something from your desk!'



# keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    if not grabbed:
        break

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, np.ones((5,5),np.uint8))
    mask = cv2.dilate(mask, np.ones((5,5),np.uint8))

    _, cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10: 
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
        if radius > 200:
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(sent_from, to, email_text)
                server.close()
                print 'Email sent'
                break
            except:
                print "Error: unable to send email"

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
