from geographiclib.geodesic import Geodesic


def calc_distance(hostel_coordinates, school_coordinates):
	'''
	we will be using the central gps address of every school
	'''
	lat, longi = school_coordinates.split(',')
	'''
	converting str points to float
	'''
	lat = float(lat)
	longi = float(longi)

	host_lat, host_longi = hostel_coordinates.split(',')
	
	host_lat = float(host_lat)
	host_longi = float(host_longi)

	geod = Geodesic.WGS84

	
	res = geod.Inverse(lat, longi, host_lat, host_longi)
	'''
	assume an average person walks 80m in a minute
	'''

	dist = res['s12']
	average_walking_time = int(dist / 80)

	return f'{average_walking_time} mins'

