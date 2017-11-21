#!/usr/bin/env python

#license removed for brevity
import rospy
from std_msgs.msg import String
import serial
from gps_message.msg import GPS_data

ser = serial.Serial("/dev/ttyUSB0", baudrate = 4800, timeout = None)

qual_dict = {0: "invalid", 1: "GPS fix(SPS)", 2: "DGPS fix", 3: "PPS fix", 4:"Real Time Kinematic", 5:"Float RTK", 6: "Dead Reckoning", 7:"Manual input mode", 8:"Simulated mode"}

def format_data(arr):
	hrs = 0
	mins = 0
	secs = 0
	#math to help parse the time integer from HHMMSS into HH:MM:SS
	try: #in case the data is blank and the time returns as null
		secs = int(arr[1] % 100)
		mins = int(arr[1] / 100.0) % 100
		hrs = int(arr[1] / 10000.0) % 100
	except:
		pass

    #math to help parse the lat/long integer from DDMM.MMM to DD and MM.MM seperatly ( D --> degrees, M --> minutes)
	lat_deg = int(arr[2]) / 100.0
	lat_mins = (lat_deg * 100) - arr[2]
	long_deg = int(arr[4]) / 100.0
	long_mins = (long_deg * 100) - arr[4]

	#puts arr values in a string that formats them to label them in a helpful way.
	#the values are in standard NME sentences, and we are only fomrating GGA sentences
	msg = "\nTime: " + str(hrs).zfill(2) + ":"+ str(mins).zfill(2) + ":" + str(secs).zfill(2)
	msg += "\nLatitude: " + str(lat_deg) + " deg "  + str(lat_mins) + "' " + str(arr[3]);
	msg += "\t\tLatitude: " + str(long_deg) + " deg "  + str(long_mins) + "' " + str(arr[5]);
	msg += "\nFixed Quality: " + str(qual_dict[arr[6]])
	msg +="\nNum of Satelittes: " + str(arr[7])
	msg +="\nHorizontal Dilution: " + str(arr[8]) + " " + str(arr[9])
	msg +="\t\tGeoid: " + str(arr[12]) + " " + str(arr[13])
	msg +="\t\tAltitude: " + str(arr[10]) + " " +  str(arr[11])
	msg +="\nLast Update: " + str(arr[14])
	msg +="\t\tStation ID: " + str(arr[15])

	return msg

def talker():
    #declares that node is publishing to 'GPS_topic' topic
    pub = rospy.Publisher('GPS_Topic', String, queue_size = 10) # Topic name: 'GPS_Topic', STring
    #tells rospy that the name of the node is 'talker'
    rospy.init_node('gps_talker', anonymous=True) # node name: gps_talker
    rate = rospy.Rate(40) # 40hz (loops forty times per second)
    msg_arr = GPS_data()

    while not rospy.is_shutdown():
		serial_data = ser.readline() #get values form serial
		parsed_data = str(serial_data).split(',') 

		msg_arr.name = parsed_data[0] # we only need to see the GGA values, and that condition is determined by the first NME value
		if(str(parsed_data[0]) == "$GPGGA"): 
			try:			
				msg_arr.time = parsed_data[1]
				msg_arr.latitude = parsed_data[2]
				msg_arr.lat_direction = parsed_data[3]
				msg_arr.longitude = parsed_data[4]
				msg_arr.long_direction = parsed_data[5]
				msg_arr.fix_qual = parsed_data[6]
				msg_arr.num_sats = parsed_data[7]
				msg_arr.horz_dilut = parsed_data[8]
				msg_arr.horz_unit = parsed_data[9]
				msg_arr.altitude = parsed_data[10]
				msg_arr.alt_unit = parsed_data[11]
				msg_arr.geoid = parsed_data[12]
				msg_arr.geoid_unit = parsed_data[13]
				msg_arr.last_update = parsed_data[14]
				msg_arr.station_ID = parsed_data[15]
			except:
				pass

	        rospy.loginfo(format_data(msg_arr))
			# pub.publish(format_data(msg_arr))
	        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass