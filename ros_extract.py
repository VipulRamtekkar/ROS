import cv2
import numpy as np
import os 
import rosbag
import argparse
from cv_bridge import CvBridge

def main():
	'''
	Extracting compressed images from ROS Bag files 
	'''
	parser = argparse.ArgumentParser(description = "Extracting compressed images from a ROS bag file.")
	parser.add_argument("rosbag", help = "location of the rosbag file")
	parser.add_argument("topic", help = "the rostopic for the bagfile")
	parser.add_argument("--topic2", help = "ros messages of the corresponding images", default = None)
	parser.add_argument("--count", help = "Number of images to be extracted from the bagfile", type = int, default = 200)
	parser.add_argument("--compress", help = "Boolean value to state whether the images are compressed or not", type = bool, default = True)
	args = parser.parse_args()

	br = CvBridge()
	bag = rosbag.Bag(args.rosbag,"r")
	access = 0777
	if os.path.isdir("images"):
		pass
	else:
		os.mkdir("images",access)

	count = 0

	for topic, msg, t in bag.read_messages(topics=[args.topic]):

		if args.compress:
			cv_img = br.compressed_imgmsg_to_cv2(msg, desired_encoding = "passthrough") # Reading compressed image from bagfile
		else:
			cv_img = br.imgmsg_to_cv2(msg, desired_encoding = "passthrough") # if the images are raw 

		cv2.imwrite(os.path.join("images", "image_%03i.jpg" % count), cv_img)

		count = count + 1

		if count == args.count:
			break

	print "Images Saved"

	if args.topic2 is not None:
		
		if os.path.isdir("messages"):
			pass
		else:
			os.mkdir("messages",access)

		skip_messgage = True # If the message rate is not equal to image rate 
		miss = 22 # Compensating for the unequal message rates and changing the per message miss accordingly,
				  # now if misses every 1 message in 22 messages
		i = 0
		topic2 = args.topic2
		for topic, msg, t in bag.read_messages(topics=[topic2]):
			i = i + 1
			if skip_messgage:	
				if i%miss == 0:
					continue
			f = open(os.path.join("messages","pose_%03i.txt" % count), "a")
			f.write(str(msg))
			f.close()
			count = count + 1

			if count == args.count:
				break

		print "Messages Recorded"
	bag.close()

	return 

if __name__ == '__main__':
	main()
