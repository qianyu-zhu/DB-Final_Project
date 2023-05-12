#Import Flask Library
import math
import time
import json
import hashlib
import pymysql.cursors
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, time, datetime
from flask import Flask, render_template, request, session, redirect


#Initialize the app from Flask
app = Flask(__name__)
app.secret_key = 'some key that you will never guess'

#Configure MySQL
conn = pymysql.connect(db='Air',
					   user='root',
					   password='',
					   host='localhost',
					   charset='utf8mb4',
					   cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index')

#Define route for FlightSearch
@app.route('/FlightSearch', methods =['POST', 'GET'])
def FlightSearch():

	msg = ''
	flight_result = ''

	if request.method == 'POST':
		To = request.form['To']
		From = request.form['From']
		DepartureDate = request.form['DepartureDate']    # in form of 2023/04/29
		DepartureDate = DepartureDate.replace('/','-')   # in form of 2023-04-29, class = string
		a = datetime.strptime(DepartureDate, '%Y-%m-%d') # in form of 2023-04-29 00:00:00, class = datetime

		if a < datetime.today() - timedelta(days=1):
			msg = 'You can only search for upcoming flights!'

		else:
			# enter departure airport and arrival airport
			if From.isupper() and To.isupper():
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
					FROM flight WHERE departure_airport = \'{}\' AND arrival_airport = \'{}\' AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			# enter departure airport and arrival city
			elif From.isupper() and not To.isupper():
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM airport AS a, flight AS b\
				WHERE a.airport_name = b.arrival_airport\
				AND b.departure_airport = \'{}\' \
				AND a.airport_city = \'{}\' \
				AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			# enter departure city and arrival airport
			elif not From.isupper() and To.isupper():
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM airport AS a, flight AS b\
				WHERE a.airport_name = b.departure_airport\
				AND a.airport_city = \'{}\' \
				AND b.arrival_airport = \'{}\' \
				AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()
		
			# enter arrival and departure cities
			else:
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM airport AS a, flight AS b, airport AS c \
				WHERE a.airport_name = b.departure_airport\
				AND b.arrival_airport = c.airport_name\
				AND a.airport_city= \'{}\' \
				AND c.airport_city = \'{}\' \
				AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			if not flight_result:
				msg = "There's no available flight based on the condition you insert."

	return render_template('FlightSearch', msg=msg, flight_result=flight_result)


#Define route for StatusCheck
@app.route('/StatusCheck',methods =['POST', 'GET'])
def status():

	msg = ''
	status_result = ''

	if request.method == 'POST':
		airline = request.form['Airline']
		flight_num = request.form['Flight No.']
		DepartureDate = request.form['DepartureDate']  # in form of 2023/04/29
		DepartureDate = DepartureDate.replace('/','-') # in form of 2023-04-29, class = string
	
		#search flight based on airline name and flight number
		cursor = conn.cursor()
		query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status \
			FROM flight WHERE airline_name = \'{}\' AND flight_num = \'{}\' AND departure_time LIKE \'{}\'"

		cursor.execute(query.format(airline, flight_num, DepartureDate +'%'))
		status_result = cursor.fetchall()

		if not status_result:
			msg = "There's no available flight according to the condition you insert."

	return render_template('StatusCheck',status_result = status_result, msg=msg)

#Define route for register
@app.route('/Register', methods=['GET', 'POST'])
def Register():
	return render_template('Register',msg1='',msg2='',msg3='')

# ----------------------------------------Login-----------------------------------------------
#Define route for Login
@app.route('/Login', methods=['GET', 'POST'])
def Login():
	return render_template('Login', msg='')

#Define route for customer-login
@app.route('/CustomerLogin', methods=['GET', 'POST'])
def CustomerLogin():
	email = request.form['Email']
	password = request.form['Password']

	#find registered customer record in database
	cursor = conn.cursor()
	query = "SELECT * FROM customer WHERE email = %s and password = %s"
	cursor.execute(query, (email, hashlib.md5(password.encode()).hexdigest()))
	data = cursor.fetchone()
	cursor.close()

	if(data):
		#creates a session for the the user, session is a built in
		session['username1'] = email
		return redirect("/CustomerViewMyFlights")
	else:
		#no record found, return an error message to the html page
		msg1 = 'Invalid email or password!'
		return render_template('Login', msg1=msg1)

#Define route for booking-agent-login
@app.route('/BookingAgentLogin', methods=['GET', 'POST'])
def BookingAgentLogin():
	email = request.form['Email']
	password = request.form['Password']

	#find registered agent record in database
	cursor = conn.cursor()
	query = "SELECT * FROM booking_agent WHERE email = %s and password = %s"
	cursor.execute(query, (email, hashlib.md5(password.encode()).hexdigest()))
	# cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()
	if(data):
		session['username2'] = email
		return redirect("/AgentViewMyFlights")
	else:
		#no record found, returns an error message to the html page
		msg2 = 'Invalid email or password!'
		return render_template('Login', msg2=msg2)

#Define route for airline-staff-login
@app.route('/StaffLogin', methods=['GET', 'POST'])
def StaffLogin():
	if request.method == 'POST':
		username = request.form['Username']
		password = request.form['Password']

		#find registered staff record in database
		cursor = conn.cursor()
		query = "SELECT * FROM airline_staff WHERE username = %s and password = %s"
		#the following line automatically encodes password in database
		cursor.execute(query, (username, hashlib.md5(password.encode()).hexdigest()))
		data = cursor.fetchone()
		cursor.close()

		if(data):
			#create a session for the the user, session is a built in
			session['username3'] = username
			return redirect("/StaffViewMyFlights")
		else:
			#no record found, returns an error message to the html page
			msg3 = 'Invalid username or password!'
			return render_template('Login', msg3=msg3)
	
# ----------------------------------------Register-----------------------------------------------
#Define route for Customer Register
@app.route('/CustomerRegister', methods=['GET', 'POST'])
def CustomerRegister():
	if request.method == 'POST':
		name = request.form['Name']
		city = request.form['City']
		email = request.form['Email']
		state = request.form['State']
		street = request.form['Street']
		password = request.form['Password']
		phone_number = request.form['Phone_Num']
		date_of_birth =request.form['Date_Of_Birth']
		building_number = request.form['Building_Num']
		passport_number = request.form['Passport_Num']
		passport_country =request.form['Passport_Country']
		passport_expiration = request.form['Passport_Expiration_Date']

		cursor = conn.cursor()
		query = "SELECT * FROM customer WHERE email = %s"
		cursor.execute(query, (email))
		data = cursor.fetchone()
		if(data):
			#If the previous query returns data, then user exists
			msg1 = "This user already exists."
			return render_template('Register', msg1 = msg1)
		else:
			try:
				ins = "INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
				cursor.execute(ins, (email, name, hashlib.md5(password.encode()).hexdigest(), building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
				conn.commit()
				cursor.close()
			except pymysql.Error as err:
				#return database error on insertion
				return render_template('Register', msg1=err)
			return render_template('Login')
		
#Define route for Booking Agent Register
@app.route('/AgentRegister', methods=['GET', 'POST'])  
def AgentRegister():
	if request.method == 'POST':
		email = request.form['Email']
		password = request.form['Password']
		booking_agent_id = request.form['Booking_Agent_ID']

		cursor = conn.cursor()
		query = "SELECT * FROM booking_agent WHERE email = %s"
		cursor.execute(query, (email))
		data = cursor.fetchone()
		if(data):
			#If the previous query returns data, then user exists
			msg2 = "This user already exists"
			return render_template('Register', msg2 = msg2)
		else:
			try:
				ins = "INSERT INTO booking_agent VALUES(%s,%s,%s)"
				cursor.execute(ins,(email, hashlib.md5(password.encode()).hexdigest(), booking_agent_id))
				conn.commit()
				cursor.close()
			except pymysql.Error as err:
				return render_template('Register', msg1=err)
			return redirect('Login')


#Define route for Airline Staff Register
@app.route('/AirlineStaffRegister', methods=['GET', 'POST'])
def AirlineStaffRegister():
	if request.method == 'POST':
		#grabs information from the forms
		username = request.form['Username']
		password = request.form['Password']
		last_name = request.form['Last_Name']
		first_name = request.form['First_Name']
		airline_name = request.form['Airline_Name']
		date_of_birth = request.form['Date_Of_Birth']

		cursor = conn.cursor()
		query = "SELECT * FROM airline_staff WHERE username = %s"
		cursor.execute(query, (username))
		data = cursor.fetchone()
		if(data):
			#If the previous query returns data, then user exists
			msg3 = "This user already exists"
			return render_template('Register', msg3 = msg3)
		else:
			try:
				ins = "INSERT INTO airline_staff VALUES(%s,%s,%s,%s,%s,%s)"
				cursor.execute(ins, (username, hashlib.md5(password.encode()).hexdigest(), first_name, last_name, date_of_birth, airline_name))
				conn.commit()
				cursor.close()
				return render_template('Login')
			except:
				return render_template('Register', msg3 = 'Failed to register user.')
			


# ----------------------------------------Customer-----------------------------------------------
@app.route('/CustomerViewMyFlights', methods=['GET', 'POST'])
def CustomerViewMyFlights():
	msg1=''
	cursor = conn.cursor()
	c_email = session['username1']
	query = "SELECT DISTINCT airline_name, flight_num, departure_airport, \
		arrival_airport, departure_time, arrival_time, price, status \
		FROM flight WHERE departure_time > %s AND \
		(airline_name, flight_num) IN (select airline_name, flight_num FROM ticket NATURAL JOIN purchases where customer_email = %s)"
	cursor.execute(query,(datetime.today(),c_email))
	upcoming_flight_result = cursor.fetchall()
	if not upcoming_flight_result:
		msg1 = "You have no purchased upcoming flights."
	
	advanced_result=''
	msg2 = ''
	if request.method == 'POST':
		To = request.form['To']
		From = request.form['From']
		DepartureDateRange = request.form['DepartureDateRange'] # in form of 2023/04/29 - 2023/05/12 , class = string
		StartRange = DepartureDateRange.split("-")[0].strip()   # in form of 2023/04/29 , class = string
		EndRange = DepartureDateRange.split("-")[1].strip()     # in form of 2023/05/12 , class = string
		StartRange = StartRange.replace('/','-')                # in form of 2023-04-29, class = string
		EndRange = EndRange.replace('/','-')                    # in form of 2023-05-12, class = string
		StartRange = datetime.strptime(StartRange, '%Y-%m-%d')  # in form of 2023-04-29 00:00:00, class = datetime
		EndRange = datetime.strptime(EndRange, '%Y-%m-%d')      # in form of 2023-05-12 00:00:00, class = datetime

		
		# enter departure and arrival airports
		if From.isupper() and To.isupper():
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, ticket_id \
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				WHERE customer_email = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND departure_airport = \'{}\' AND arrival_airport = \'{}\' '
			cursor.execute(q.format(c_email, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()
		
		# enter departure city and arrival airport
		elif not From.isupper() and To.isupper():
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, ticket_id \
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				JOIN airport ON(departure_airport = airport_name) \
				WHERE customer_email = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND airport_city = \'{}\' AND arrival_airport = \'{}\' '
			cursor.execute(q.format(c_email, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()

		# enter departure airport and arrival city
		elif From.isupper() and not To.isupper():
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, ticket_id \
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				JOIN airport ON(arrival_airport = airport_name) \
				WHERE customer_email = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND departure_airport = \'{}\' AND airport_city = \'{}\' '
			cursor.execute(q.format(c_email, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()

		# enter departure znd arrival cities
		else:
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, ticket_id \
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				JOIN airport a ON(departure_airport = a.airport_name) \
				JOIN airport b ON(arrival_airport = b.airport_name) \
				WHERE customer_email = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND a.airport_city = \'{}\' AND b.airport_city = \'{}\''
			cursor.execute(q.format(c_email, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()
		
		if not advanced_result:
			msg2 = "You have no purchased flights within the departure date range."
	return render_template('CustomerViewMyFlights',msg1=msg1,upcoming_flight_result=upcoming_flight_result,msg2=msg2,advanced_result=advanced_result)




@app.route('/CustomerSearchFlights', methods=['GET', 'POST'])
def CustomerSearchFlights():
	msg=''
	flight_result = ''

	if request.method == 'POST':
		To = request.form['To']
		From = request.form['From']
		DepartureDate = request.form['DepartureDate']    # in form of 2023/04/29
		DepartureDate = DepartureDate.replace('/','-')   # in form of 2023-04-29, class = string
		a = datetime.strptime(DepartureDate, '%Y-%m-%d') # in form of 2023-04-29 00:00:00, class = datetime

		if a < datetime.today() - timedelta(days=1):
			msg = 'You can only search for upcoming flights!'

		else:
			if From.isupper() and To.isupper():
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status FROM flight WHERE departure_airport = \'{}\' AND arrival_airport = \'{}\' AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()
			

			# enter departure airport and arrival city
			elif From.isupper() and not To.isupper():
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM airport AS a, flight AS b\
				WHERE a.airport_name = b.arrival_airport\
				AND b.departure_airport = \'{}\' \
				AND a.airport_city = \'{}\' \
				AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			# enter departure city and arrival airport
			elif not From.isupper() and To.isupper():
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM airport AS a, flight AS b\
				WHERE a.airport_name = b.departure_airport\
				AND a.airport_city = \'{}\' \
				AND b.arrival_airport = \'{}\' \
				AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()
		
			# enter arrival and departure cities
			else:
				cursor = conn.cursor()
				query = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM airport AS a, flight AS b, airport AS c \
				WHERE a.airport_name = b.departure_airport\
				AND b.arrival_airport = c.airport_name\
				AND a.airport_city= \'{}\' \
				AND c.airport_city = \'{}\' \
				AND departure_time LIKE \'{}\'"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			if not flight_result:
				msg = "There's no available flight based on the condition you insert."

	return render_template('CustomerSearchFlights',msg=msg,flight_result=flight_result)

@app.route('/CustomerPurchaseTickets', methods=['GET', 'POST'])
def CustomerPurchaseTickets():
	msg = ''
	c_email = session['username1']
	if request.method == 'POST':
		Flight_Num = request.form['Flight_Num']
		Airline_Name = request.form['Airline_Name']
		Num_of_Tickets_to_Purchase_for_this_Flight = int(request.form['Num_of_Tickets_to_Purchase_for_this_Flight'])

		cursor = conn.cursor()
		query = "SELECT seats-count(ticket_id) AS seat_left\
			FROM flight JOIN ticket USING (airline_name, flight_num) \
			JOIN airplane USING (airline_name, airplane_id)\
			WHERE airline_name = \'{}\' \
			AND flight_num = \'{}\'"

		cursor.execute(query.format(Airline_Name, Flight_Num))
		#stores the results in a variable
		seat_left = cursor.fetchone()['seat_left']

		if seat_left == None:
			msg = "There's no available flight based on the condition you insert."

		elif seat_left == 0:
			#If the previous query returns data, then user exists
			msg = "This flight has been sold out!"

		elif seat_left < Num_of_Tickets_to_Purchase_for_this_Flight:
			msg = "There's only {} tickets left for this flight! Please decrease the quantity you want or change a flight!"
			msg = msg.format(int(seat_left))

		else:
			msg = "You have successfully purchased {} flight tickets for Flight Number {} operated by {}! You can check for flights in ViewMyFlights Page."
			msg = msg.format(Num_of_Tickets_to_Purchase_for_this_Flight,Flight_Num,Airline_Name)
			cursor.execute("SELECT count(*) as num_existing_tickets, MAX(ticket_id) as max_ticket_id FROM ticket")
			existing = cursor.fetchone()

			#insert new ticket and purchases in dataframe
			if int(existing['num_existing_tickets']) == 0:
				start_ticket_id = int(1)
			else:
				start_ticket_id = int(existing['max_ticket_id'])+1
			for i in range(Num_of_Tickets_to_Purchase_for_this_Flight):
				query_insert_ticket = "INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES (%s, %s, %s)"
				query_insert_purchases = "INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES (%s, %s,null, %s)"
				t = datetime.today().strftime('%Y-%m-%d')[:10]
				cursor.execute(query_insert_ticket,(start_ticket_id+i, Airline_Name, Flight_Num))
				cursor.execute(query_insert_purchases,(start_ticket_id+i,c_email,t))
			conn.commit()
			cursor.close()

	return render_template('CustomerPurchaseTickets',msg=msg)

@app.route('/CustomerTrackSpending', methods=['GET', 'POST'])
def CustomerTrackSpending():
	msg1 = 'In the past one year, you spent {} in total.'

	c_email = session['username1']
	cursor = conn.cursor()
	query = "SELECT  IFNULL(sum(price),0)  as sum_spending \
		from ticket NATURAL JOIN purchases NATURAL JOIN flight \
		WHERE customer_email = \'{}\'  and purchase_date between \'{}\' and \'{}\'"
	today = datetime.now()
	last_year_today = datetime.now() - timedelta(days=1*365)
	cursor.execute(query.format(c_email,last_year_today,today))
	one_year_spending = int(cursor.fetchone()["sum_spending"])
	msg1 = msg1.format(one_year_spending)

	#Default: track customer spending in the past 6 months
	m = 6
	month_list = [0]*m
	month_spending_list = [0]*m
	this_month_today = datetime.now()

	#calculate spending in each month
	for i in range(m):
		month_list[i]= int(this_month_today.strftime("%m"))
		cursor = conn.cursor()
		query = "SELECT IFNULL(sum(price),0) as sum_spending \
			from ticket NATURAL JOIN purchases NATURAL JOIN flight \
			WHERE customer_email = \'{}\'  and purchase_date between \'{}\' and \'{}\'"
		last_month_today = this_month_today - relativedelta(months=1)
		cursor.execute(query.format(c_email,last_month_today,this_month_today))
		row = cursor.fetchone()
		month_spending_list[i] = int(row["sum_spending"])
		this_month_today = last_month_today

	#reverse list order
	month_list = month_list[::-1]
	month_list = json.dumps(month_list)
	month_spending_list = month_spending_list[::-1]
	month_spending_list = json.dumps(month_spending_list)

	if request.method == 'POST':

		PurchaseDateRange = request.form['PurchaseDateRange']  # in form of 2023/04/29 - 2023/05/12 , class = string
		StartRange = PurchaseDateRange.split("-")[0].strip()   # in form of 2023/04/29 , class = string
		EndRange = PurchaseDateRange.split("-")[1].strip()     # in form of 2023/05/12 , class = string
		StartRange = StartRange.replace('/','-')               # in form of 2023-04-29, class = string
		EndRange = EndRange.replace('/','-')                   # in form of 2023-05-12, class = string
		StartRange = datetime.strptime(StartRange, '%Y-%m-%d') # in form of 2023-04-29 00:00:00, class = datetime
		EndRange = datetime.strptime(EndRange, '%Y-%m-%d')     # in form of 2023-05-12 00:00:00, class = datetime

		m = 0
		month_spending_list = []
		month_list = []
		this_month_today = EndRange

		#find customer spending during each month in the past year
		while this_month_today>=StartRange:
			m+=1
			month_list.append(int(this_month_today.strftime("%m"))) 

			#find customer spending during particular month
			cursor = conn.cursor()
			query = "SELECT IFNULL(sum(price),0) as sum_spending \
				from ticket NATURAL JOIN purchases NATURAL JOIN flight \
				WHERE customer_email = \'{}\'  and purchase_date between \'{}\' and \'{}\'"

			last_month_today = this_month_today - relativedelta(months=1)
			cursor.execute(query.format(c_email,last_month_today,this_month_today))
			row = cursor.fetchone()
			month_spending_list.append(int(row["sum_spending"]))
			this_month_today = last_month_today

		#reverse list order
		month_list = month_list[::-1]
		month_list = json.dumps(month_list)
		month_spending_list = month_spending_list[::-1]
		month_spending_list = json.dumps(month_spending_list)
	
	return render_template('CustomerTrackSpending',msg1=msg1,month_spending_list=month_spending_list,month_list=month_list,m=m)

@app.route('/Logout')
def Logout():
	session.pop('username1', None)
	session.pop('username2', None)
	session.pop('username3', None)
	return render_template('/Login')


# ----------------------------------------Booking Agent-----------------------------------------------
@app.route('/AgentViewMyFlights', methods=['GET', 'POST'])
def AgentViewMyFlights():

	msg1=''
	a_email = session['username2']

	#find booking agent id
	cursor = conn.cursor()
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\''
	cursor.execute(query.format(a_email))
	agent_id = cursor.fetchone()['booking_agent_id']

	#default: find upcoming flights the agent booked tickets for in the following month
	query = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status\
			FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
			WHERE departure_time >= \'{}\' AND departure_time <= \'{}\' AND booking_agent_id = \'{}\''
	today = datetime.now()
	next_month_today = today + relativedelta(months=1)
	cursor.execute(query.format(today,next_month_today,agent_id))
	upcoming_flight_result = cursor.fetchall()

	#no booking record in the next month found
	if not upcoming_flight_result:
		msg1 = "There is no flight you purchased on behalf of customers in the next 30 days."
	
	advanced_result=''
	msg2 = ''
	if request.method == 'POST':
		To = request.form['To']
		From = request.form['From']
		DepartureDateRange = request.form['DepartureDateRange'] # in form of 2023/04/29 - 2023/05/12 , class = string
		StartRange = DepartureDateRange.split("-")[0].strip()   # in form of 2023/04/29 , class = string
		EndRange = DepartureDateRange.split("-")[1].strip()     # in form of 2023/05/12 , class = string
		StartRange = StartRange.replace('/','-')                # in form of 2023-04-29, class = string
		EndRange = EndRange.replace('/','-')                    # in form of 2023-05-12, class = string
		StartRange = datetime.strptime(StartRange, '%Y-%m-%d')  # in form of 2023-04-29 00:00:00, class = datetime
		EndRange = datetime.strptime(EndRange, '%Y-%m-%d')      # in form of 2023-05-12 00:00:00, class = datetime

		# enter departure and arrival airports
		if From.isupper() and To.isupper():
			cursor = conn.cursor()
			query = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, \
			departure_time, arrival_time, price, status, customer_email, COUNT(ticket_id) as ticket_count\
			FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
			WHERE booking_agent_id = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
			AND departure_airport = \'{}\' AND arrival_airport = \'{}\' \
			GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, customer_email '
			cursor.execute(query.format(agent_id, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()
				
		# enter departure city and arrival airport
		elif not From.isupper() and To.isupper():
			cursor = conn.cursor()
			query = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, \
				departure_time, arrival_time, price, status, customer_email, COUNT(ticket_id) as ticket_count\
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				JOIN airport ON(departure_airport = airport_name) \
				WHERE booking_agent_id = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND airport_city = \'{}\' AND arrival_airport = \'{}\' \
				GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, customer_email'
			cursor.execute(query.format(agent_id, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()
		
		# enter departure airport and arrival city
		elif From.isupper() and not To.isupper():
			cursor = conn.cursor()
			query = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, \
				departure_time, arrival_time, price, status, customer_email, COUNT(ticket_id) as ticket_count\
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				JOIN airport ON(arrival_airport = airport_name) \
				WHERE booking_agent_id = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND departure_airport = \'{}\' AND airport_city = \'{}\' \
				GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, customer_email'
			cursor.execute(query.format(agent_id, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()

		# enter departure znd arrival cities
		else:
			cursor = conn.cursor()
			query = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, \
				departure_time, arrival_time, price, status, customer_email, COUNT(ticket_id) as ticket_count\
				FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
				JOIN airport a ON(departure_airport = a.airport_name) \
				JOIN airport b ON(arrival_airport = b.airport_name) \
				WHERE booking_agent_id = \'{}\' AND departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND a.airport_city = \'{}\' AND b.airport_city = \'{}\' \
				GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, customer_email'
			cursor.execute(query.format(agent_id, EndRange, StartRange, From, To))
			advanced_result = cursor.fetchall()

		if not advanced_result:
			msg2 = "There is no valid booking based on the given information."
	return render_template('AgentViewMyFlights',msg1=msg1,upcoming_flight_result=upcoming_flight_result,msg2=msg2,advanced_result=advanced_result)

@app.route('/AgentSearchFlights', methods=['GET', 'POST'])
def AgentSearchFlights():
	msg=''
	flight_result = ''

	if request.method == 'POST':
		To = request.form['To']
		From = request.form['From']
		DepartureDate = request.form['DepartureDate']    # in form of 2023/04/29
		DepartureDate = DepartureDate.replace('/','-')   # in form of 2023-04-29, class = string
		a = datetime.strptime(DepartureDate, '%Y-%m-%d') # in form of 2023-04-29 00:00:00, class = datetime
		
		if a < datetime.now()- relativedelta(day=1):
			msg = 'You can only search for upcoming flights!'

		else:
			# enter departure airport and arrival airport
			if From.isupper() and To.isupper():
				cursor = conn.cursor()
				query = "SELECT ALL airline_name, flight_num, departure_airport, arrival_airport, \
						departure_time, arrival_time, price, seats-count(ticket_id) AS seat_left, status \
						FROM flight LEFT JOIN ticket USING (airline_name, flight_num) \
						JOIN airplane USING (airline_name, airplane_id)\
						WHERE departure_airport = \'{}\' \
						AND arrival_airport = \'{}\' \
						AND departure_time LIKE \'{}\' \
						GROUP BY airline_name, flight_num"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			# enter departure airport and arrival city
			elif From.isupper() and not To.isupper():
				cursor = conn.cursor()
				query = "SELECT ALL airline_name, flight_num, departure_airport, arrival_airport, \
						departure_time, arrival_time, price, seats-count(ticket_id) AS seat_left, status \
						FROM airport AS a, (flight LEFT JOIN ticket USING (airline_name, flight_num) \
						JOIN airplane USING (airline_name, airplane_id)) \
						WHERE a.airport_name = arrival_airport \
						AND departure_airport = \'{}\' \
						AND a.airport_city = \'{}\' \
						AND departure_time LIKE \'{}\' \
						GROUP BY airline_name, flight_num"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			# enter departure city and arrival airport
			elif not From.isupper() and To.isupper():
				cursor = conn.cursor()
				query = "SELECT ALL airline_name, flight_num, departure_airport, arrival_airport, \
						departure_time, arrival_time, price, seats-count(ticket_id) AS seat_left, status \
						FROM airport AS a, (flight LEFT JOIN ticket USING (airline_name, flight_num) \
						JOIN airplane USING (airline_name, airplane_id)) \
						WHERE a.airport_name = departure_airport \
						AND a.airport_city = \'{}\'\
						AND arrival_airport = \'{}\'\
						AND departure_time LIKE \'{}\'\
						GROUP BY airline_name, flight_num"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()
		
			# enter arrival and departure cities
			else:
				cursor = conn.cursor()
				query = "SELECT ALL airline_name, flight_num, departure_airport, arrival_airport, \
						departure_time, arrival_time, price, seats-count(ticket_id) AS seat_left, status\
						FROM airport AS a, (flight LEFT JOIN ticket USING (airline_name, flight_num) \
						JOIN airplane USING (airline_name, airplane_id)), airport AS c \
						WHERE a.airport_name = departure_airport \
						AND arrival_airport = c.airport_name \
						AND a.airport_city = \'{}\'\
						AND c.airport_city = \'{}\'\
						AND departure_time LIKE \'{}\'\
						GROUP BY airline_name, flight_num"
				cursor.execute(query.format(From, To, '%'+str(DepartureDate)+'%'))
				flight_result = cursor.fetchall()

			if not flight_result:
				msg = "There's no available flight based on the condition you insert."
	return render_template('AgentSearchFlights',msg=msg,flight_result=flight_result)

@app.route('/AgentPurchaseTickets', methods=['GET', 'POST'])
def AgentPurchaseTickets():
	msg = ''
	a_email = session['username2']

	#find booking agent id
	cursor = conn.cursor()
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\''
	cursor.execute(query.format(a_email))
	agent_id = cursor.fetchone()['booking_agent_id']

	if request.method == 'POST':
		c_email = request.form['Cus_Email']
		Flight_Num = request.form['Flight_Num']
		Airline_Name = request.form['Airline_Name']
		Num_of_Tickets_to_Purchase_for_this_Flight = int(request.form['Num_of_Tickets_to_Purchase_for_this_Flight'])
		
		#find the airline agent works for
		query = 'SELECT airline_name FROM works_for WHERE email = \'{}\' AND airline_name = \'{}\''
		cursor.execute(query.format(a_email, Airline_Name))
		work_airline = cursor.fetchone()

		# if agent does not work for the flight's airline 
		if work_airline == None:
			msg = 'You are not allowed to book since you are not working for this airline!'
			return render_template('AgentPurchaseTickets', msg=msg)

		#find number of available seats in the flight
		query = "SELECT seats-count(ticket_id) AS seat_left\
			FROM flight JOIN ticket USING (airline_name, flight_num) JOIN airplane USING (airline_name, airplane_id)\
			WHERE airline_name = \'{}\' \
			AND flight_num = \'{}\'"

		cursor.execute(query.format(Airline_Name, Flight_Num))
		seat_left = cursor.fetchone()['seat_left']

		#cannot find the flight
		if seat_left == None:
			msg = "The flight does not exist!"

		#no seats left
		elif seat_left == 0:
			msg = "This flight has been sold out!"

		#no enough seats left
		elif seat_left < Num_of_Tickets_to_Purchase_for_this_Flight:
			msg = "There's only {} tickets left for this flight! Please decrease the quantity you want or change a flight!"
			msg = msg.format(int(seat_left))
			
		#insert records in ticket & purchases dataframes
		else:
			msg = "You have successfully purchased {} flight ticket(s) for Flight Number {} operated by {}! You can check for flights in ViewMyFlights Page."
			msg = msg.format(Num_of_Tickets_to_Purchase_for_this_Flight,Flight_Num,Airline_Name)
			cursor.execute("SELECT count(*) as num_existing_tickets, MAX(ticket_id) as max_ticket_id FROM ticket")
			existing = cursor.fetchone()
			
			#set ticket id
			if int(existing['num_existing_tickets']) == 0:
				start_ticket_id = int(1)
			else:
				start_ticket_id = int(existing['max_ticket_id'])+1

			try:
				for i in range(Num_of_Tickets_to_Purchase_for_this_Flight):
					query_insert_ticket = "INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES (%s, %s, %s)"
					query_insert_purchases = "INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES (%s, %s, %s, %s)"
					t = datetime.today().strftime('%Y-%m-%d')
					t = t[:10]
					cursor.execute(query_insert_ticket,(start_ticket_id+i, Airline_Name, Flight_Num))
					cursor.execute(query_insert_purchases,(start_ticket_id+i,c_email,agent_id,t))
				conn.commit()
				cursor.close()

			#error during insertion
			except pymysql.Error as err:
				return render_template('AgentPurchaseTickets', msg=err.args[1])

	return render_template('AgentPurchaseTickets',msg=msg)

@app.route('/AgentMyCommission', methods=['GET', 'POST'])
def AgentMyCommission():
	a_email = session['username2']

	#find the airline agent works for
	cursor = conn.cursor()
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\''
	cursor.execute(query.format(a_email))
	agent_id = cursor.fetchone()['booking_agent_id']

	#default: compute commission during the past month
	EndRange = date.today()
	StartRange = (EndRange-timedelta(days=30))

	#compute total commission during the last month, default commission rate 10%
	query = 'SELECT CAST(0.1*SUM(price) as decimal(10,2)) as TotalPrice, CAST((0.1*SUM(price))/COUNT(*) as decimal(10,2)) as AvePrice, COUNT(*) as NumTicket\
		FROM purchases NATURAL JOIN ticket NATURAL JOIN flight \
		WHERE booking_agent_id = \'{}\' AND purchase_date <= \'{}\' AND purchase_date >= \'{}\''
	cursor.execute(query.format(agent_id, EndRange, StartRange))
	commission = cursor.fetchone()

	if request.method == 'POST':
		PurchaseDateRange = request.form['PurchaseDateRange'] # in form of 2023/04/29 - 2023/05/12 , class = string
		StartRange = PurchaseDateRange.split("-")[0].strip()  # in form of 2023/04/29 , class = string
		EndRange = PurchaseDateRange.split("-")[1].strip()    # in form of 2023/05/12 , class = string
		StartRange = StartRange.replace('/','-')              # in form of 2023-04-29, class = string
		EndRange = EndRange.replace('/','-')                  # in form of 2023-05-12, class = string
		
		#compute total commission during the specified time window, default commission rate 10%
		query = 'SELECT CAST(0.1*SUM(price) as decimal(10,2)) as TotalPrice, \
			CAST((0.1*SUM(price))/COUNT(*) as decimal(10,2)) as AvePrice, COUNT(*) as NumTicket\
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight \
			WHERE booking_agent_id = \'{}\' AND purchase_date <= \'{}\' AND purchase_date >= \'{}\''
		cursor.execute(query.format(agent_id, EndRange, StartRange))
		commission = cursor.fetchone()
			
	#no valid booking during the time window
	if commission is None:
		commission = [[0],[0],[0]]

	return render_template('AgentMyCommission', c = commission, start_date = StartRange, end_date = EndRange)

@app.route('/AgentTopCustomer')
def AgentTopCustomer():
	a_email = session['username2']

	#find airline agent works for
	cursor = conn.cursor()
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\''
	cursor.execute(query.format(a_email))
	agent_id = cursor.fetchone()['booking_agent_id']

	mostTicName = []
	mostComName = []
	mostTicValue = []
	mostComValue = []
	end_date = date.today()
	start_date = end_date-relativedelta(months=6)
	start_date_year = end_date-relativedelta(months=12)

	#find total number of ticket each customer booked during the past half/one year, keep the top 5
	query = "SELECT name, count(ticket_id) as TotalTicket FROM purchases \
		RIGHT JOIN customer ON (customer.email = purchases.customer_email)\
		WHERE booking_agent_id = \'{}\'\
		AND purchase_date <= \'{}\' AND purchase_date >= \'{}\'\
		GROUP BY customer_email\
		ORDER BY COUNT(ticket_id) DESC LIMIT 5"

	cursor.execute(query.format(agent_id, end_date, start_date))
	out = cursor.fetchall()

	for a in out:
		mostTicName.append(a['name'].strip())
		mostTicValue.append(a['TotalTicket'])
	
	query = "SELECT name, CAST(0.1*SUM(price) as decimal(10,2)) as TotalCom\
		FROM (purchases NATURAL JOIN ticket NATURAL JOIN flight) \
		JOIN customer ON (customer.email = customer_email)\
		WHERE booking_agent_id = \'{}\' AND purchase_date <= \'{}\' AND purchase_date >= \'{}\'\
		GROUP BY customer_email\
		ORDER BY COUNT(ticket_id) DESC LIMIT 5"
	
	cursor.execute(query.format(agent_id, end_date, start_date_year))
	out = cursor.fetchall()

	for a in out:
		mostComName.append(a['name'].strip())
		mostComValue.append(int(a['TotalCom']))
	return render_template('AgentTopCustomer', 
							id = agent_id,
							mostTicName=json.dumps(mostTicName,default=str), 
							mostComName=json.dumps(mostComName,default=str), 
							mostTicValue=json.dumps(mostTicValue,default=str), 
							mostComValue=json.dumps(mostComValue,default=str))

@app.route('/AgentCustomerInfo', methods=['GET', 'POST'])
def AgentCustomerInfo():
	a_email = session['username2']

	cursor = conn.cursor()
	query = 'SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\''
	cursor.execute(query.format(a_email))
	agent_id = cursor.fetchone()['booking_agent_id']

	query = 'SELECT DISTINCT customer_email FROM purchases WHERE booking_agent_id = \'{}\''
	cursor.execute(query.format(agent_id))
	cusEmailList = cursor.fetchall()

	if request.method == 'POST':
		c_email = request.form['CustomerEmail']
		query = 'SELECT * FROM purchases WHERE booking_agent_id = \'{}\' AND customer_email = \'{}\''
		cursor.execute(query.format(agent_id, c_email))
		cusInfo = cursor.fetchone()
		if cusInfo is None:
			return render_template('AgentCustomerInfo', 
			  						c_list = cusEmailList, 
			  						msg = 'You could only view information of customer you booked tickets for!')
		
		query = 'SELECT email, name, building_number, street, city, state, phone_number, date_of_birth \
			FROM customer WHERE email = \'{}\''
		cursor.execute(query.format(c_email))
		cusInfo = cursor.fetchone()
		if cusInfo is None:
			return render_template('AgentCustomerInfo', c_list = cusEmailList, msg = 'Customer does not exist!')
		return render_template('AgentCustomerInfo', c_list = cusEmailList, c = cusInfo, msg = 'The customer\'s information is as below:')
	return render_template('AgentCustomerInfo', c_list = cusEmailList)

# ----------------------------------------Airline Staff-----------------------------------------------
@app.route('/StaffViewMyFlights', methods=['GET', 'POST'])
def StaffViewMyFlights():
	msg1=''
	cursor = conn.cursor()
	username = session['username3']
	query = "SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
		FROM flight NATURAL join airline_staff WHERE departure_time >= \'{}\' and departure_time <= \'{}\' \
		and airline_name = (SELECT airline_name from airline_staff WHERE username = \'{}\')"
	today = datetime.now()
	next_month_today = today + relativedelta(months=1)
	cursor.execute(query.format(today,next_month_today,username))
	upcoming_flight_result = cursor.fetchall()
	if not upcoming_flight_result:
		msg1 = "The airline you work for has no upcoming flights in the next 30 days."

	#Use procedure to get staff company
	cursor.callproc('get_staff_company',(username,))
	airline_name = cursor.fetchone()['airline_name']

	advanced_result=''
	msg2 = ''

	if request.method == 'POST':
		To = request.form['To']
		From = request.form['From']
		DepartureDateRange = request.form['DepartureDateRange'] # in form of 2023/04/29 - 2023/05/12, class = string
		StartRange = DepartureDateRange.split("-")[0].strip()   # in form of 2023/04/29 , class = string
		EndRange = DepartureDateRange.split("-")[1].strip()     # in form of 2023/05/12 , class = string
		StartRange = StartRange.replace('/','-')                # in form of 2023-04-29, class = string
		EndRange = EndRange.replace('/','-')                    # in form of 2023-05-12, class = string
		StartRange = datetime.strptime(StartRange, '%Y-%m-%d')  # in form of 2023-04-29 00:00:00, class = datetime
		EndRange = datetime.strptime(EndRange, '%Y-%m-%d')      # in form of 2023-05-12 00:00:00, class = datetime

		# enter departure and arrival airports
		if From.isupper() and To.isupper():
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, \
				departure_time, arrival_time, price, status FROM flight \
				WHERE departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND departure_airport = \'{}\' AND arrival_airport = \'{}\' \
				AND airline_name = \'{}\''
			cursor.execute(q.format(EndRange, StartRange, From, To, airline_name))
			advanced_result = cursor.fetchall()
		
		# enter departure city and arrival airport
		elif not From.isupper() and To.isupper():
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM flight \
				JOIN airport ON(departure_airport = airport_name) \
				WHERE departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND airport_city = \'{}\' AND arrival_airport = \'{}\' \
				AND airline_name = \'{}\''
			cursor.execute(q.format(EndRange, StartRange, From, To, airline_name))
			advanced_result = cursor.fetchall()

		# enter departure airport and arrival city
		elif From.isupper() and not To.isupper():
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM flight \
				JOIN airport ON(arrival_airport = airport_name) \
				WHERE departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND departure_airport = \'{}\' AND airport_city = \'{}\' \
				AND airline_name = \'{}\''
			cursor.execute(q.format(EndRange, StartRange, From, To, airline_name))
			advanced_result = cursor.fetchall()

		# enter departure and arrival cities
		else:
			cursor = conn.cursor()
			q = 'SELECT DISTINCT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
				FROM flight \
				JOIN airport a ON(departure_airport = a.airport_name) \
				JOIN airport b ON(arrival_airport = b.airport_name) \
				WHERE departure_time <= \'{}\' AND departure_time >= \'{}\' \
				AND a.airport_city = \'{}\' AND b.airport_city = \'{}\' \
				AND airline_name = \'{}\''
			cursor.execute(q.format(EndRange, StartRange, From, To, airline_name))
			advanced_result = cursor.fetchall()
		
		if not advanced_result:
			msg2 = 'There is no matched flight corresponding to your input.'

	return render_template('StaffViewMyFlights',msg1=msg1,upcoming_flight_result=upcoming_flight_result,msg2=msg2,advanced_result=advanced_result)

@app.route('/StaffViewFlightCustomer', methods=['GET', 'POST'])
def StaffViewFlightCustomer():
	msg3 = ''
	customer_list = ''
	username = session['username3']

	#search customer list on a particular flight
	if request.method == 'POST':
		cursor = conn.cursor()
		flight_num = request.form['Flight_Num']
		query1 = 'SELECT airline_name, flight_num from flight WHERE flight_num = \'{}\' \
			AND airline_name = (SELECT airline_name from airline_staff WHERE username = \'{}\')'
		cursor.execute(query1.format(flight_num,username))
		flight_result = cursor.fetchall()

		if not flight_result:
			msg3 = "The flight doesn't exist."
		else:
			query2 = "SELECT name from customer where email IN (SELECT customer_email from purchases \
				where ticket_id IN (SELECT ticket_id from ticket WHERE airline_name = \
				(SELECT airline_name from airline_staff WHERE username= \'{}\') and flight_num = \'{}\'))"
			cursor.execute(query2.format(username,flight_num))
			customer_list = cursor.fetchall()

			if not customer_list:
				msg3 = 'No customer has purchased for this flight.'

	return render_template('StaffViewFlightCustomer',msg3=msg3,customer_list= customer_list)

@app.route('/StaffAdd', methods=['GET', 'POST'])
def StaffAdd():
	return render_template('StaffAdd',msg1='',msg2='',msg3='')

#Define route for Airline Staff Add Flights
@app.route('/StaffAddFlights', methods=['GET', 'POST'])
def StaffAddFlights():
	if request.method == 'POST':
		price = request.form['Price']
		status = request.form['Status']
		flight_num = request.form['Flight_Num']
		airplane_id = request.form['Airplane_ID']
		airline_name = request.form['Airline_Name']
		arrival_time = request.form['Arrival_Time']
		departure_time = request.form['Departure_Time']
		arrival_airport = request.form['Arrival_Airport']
		departure_airport = request.form['Departure_Airport']


		username = session['username3']
		cursor = conn.cursor()
		query1 = "SELECT permission_id FROM permission WHERE username = %s"
		cursor.execute(query1, (username))
		p_id = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		if not p_id:
			msg1 = 'You don\'t have permission to create flights!'
			return render_template('StaffAdd',msg1=msg1)
		elif p_id['permission_id'] != 1 and p_id['permission_id'] != 3:
				msg1 = 'You don\'t have permission to create flights!'
				return render_template('StaffAdd',msg1=msg1)
		
		#there are several places in app.py requiring procedure in Air database. 
		#following lines are alternative ways to obtain airline staff's company.

		# query2 = "SELECT airline_name from airline_staff WHERE username=%s"
		# cursor.execute(query2, (username))
		# company = cursor.fetchone()['airline_name']

		# Use procedure to get staff company
		cursor.callproc('get_staff_company',(username,))
		company = cursor.fetchone()['airline_name']

		if company != airline_name:
			msg1 = 'You can\'t create flights for other airlines!'
			return render_template('StaffAdd',msg1=msg1)

		query3 = "SELECT * FROM flight WHERE airline_name= %s AND flight_num=%s"
		cursor.execute(query3, (airline_name,flight_num))
		existing = cursor.fetchone()
		if existing:
			msg1 = "This flight already exists."
			return render_template('StaffAdd',msg1=msg1)			

		try:
			ins = "INSERT INTO flight VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			cursor.execute(ins, (airline_name,flight_num,departure_airport,departure_time,arrival_airport,arrival_time,price,status,airplane_id))
			conn.commit()
			cursor.close()
			msg1 = "Successfully created a flight!"
			return render_template('StaffAdd',msg1=msg1)
		except pymysql.Error as e:
			return render_template('StaffAdd', msg1=e.args[1])

#Define route for Airline Staff for change options
@app.route('/StaffChange', methods=['GET', 'POST'])
def StaffChange():
	return render_template('StaffChange', msg1 = '')

#Define route for Airline Staff To change flight status
@app.route('/StaffChangeStatus', methods=['GET', 'POST'])
def StaffChangeStatus():
	username = session['username3']

	if request.method == 'POST':
		#grabs information from the forms
		flight_num = request.form['Flight_Num']
		to_status = request.form['To_Status']

		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query1 = "SELECT permission_id FROM permission WHERE username = %s"
		cursor.execute(query1, (username))
		#stores the results in a variable
		p_id = cursor.fetchone()

		#use fetchall() if you are expecting more than 1 data row
		if not p_id:
			msg1 = 'You don\'t have permission to change flights status!'
			return render_template('StaffChange',msg1=msg1)
		elif p_id['permission_id'] != 2 and p_id['permission_id'] != 3:
			msg1 = 'You don\'t have permission to change flights status!'
			return render_template('StaffChange',msg1=msg1)
		else:
			# query2 = "SELECT airline_name from airline_staff WHERE username=%s"
			# cursor.execute(query2, (username))
			# company = cursor.fetchone()['airline_name']

			# Use procedure to get staff company
			cursor.callproc('get_staff_company',(username,))
			company = cursor.fetchone()['airline_name']
			
			query3 = "SELECT * FROM flight WHERE airline_name=%s and flight_num=%s"
			cursor.execute(query3, (company,flight_num))
			existing = cursor.fetchone()

			if not existing:
				msg1 = "The flight that you want to change status for doesn't exist in your airline company!"
				return render_template('StaffChange',msg1=msg1)
			elif not (to_status in ('upcoming','in progress','arrived', 'delayed','on time')):
				msg1 = "Please input a feasible status."
				return render_template('StaffChange',msg1=msg1)
			#update flight status in database				
			try:
				from_status = existing["status"]
				query4 = "UPDATE flight SET status = %s WHERE airline_name = %s and flight_num=%s"
				cursor.execute(query4, (to_status,company,flight_num))
				conn.commit()
				cursor.close()
				msg1 = "The status of the flight is successfully changed from {} to {}"
				msg1 = msg1.format(from_status,to_status)
				return render_template('StaffChange',msg1 = msg1)
			except:
				return render_template('StaffChange', msg1 = 'Failed to change the flight status.')


#Define route for Airline Staff Add Airplane
@app.route('/StaffAddAirplanes', methods=['GET', 'POST'])
def StaffAddAirplanes():
	if request.method == 'POST':
		seats = request.form['Seats']
		airplane_id = request.form['Airplane_ID']
		airline_name = request.form['Airline_Name']
		username = session['username3']

		cursor = conn.cursor()
		query1 = "SELECT permission_id FROM permission WHERE username = %s"
		cursor.execute(query1, (username))
		p_id = cursor.fetchone()

		if not p_id:
			msg2 = 'You don\'t have permission to add airplanes!'
			return render_template('StaffAdd',msg2=msg2)
		elif p_id['permission_id'] != 1 and p_id['permission_id'] != 3:
			msg2 = 'You don\'t have permission to add airplanes!'
			return render_template('StaffAdd',msg2=msg2)

		# query2 = "SELECT airline_name from airline_staff WHERE username=%s"
		# cursor.execute(query2, (username))
		# company = cursor.fetchone()['airline_name']

		# Use procedure to get staff company
		cursor.callproc('get_staff_company',(username,))
		company = cursor.fetchone()['airline_name']

		if company != airline_name:
			msg2 = 'You can\'t add airplanes for other airlines!'
			return render_template('StaffAdd',msg2=msg2)

		query3 = "SELECT * FROM airplane WHERE airline_name= %s AND airplane_id=%s"
		cursor.execute(query3, (airline_name,airplane_id))
		existing = cursor.fetchone()
		if existing:
			msg2 = "This airplane already exists."
			return render_template('StaffAdd',msg2=msg2)			

		try:
			ins = "INSERT INTO airplane VALUES(%s,%s,%s)"
			cursor.execute(ins, (airline_name,airplane_id,seats))
			conn.commit()
			cursor.close()
			msg2 = "Successfully added an airplane!"
			return render_template('StaffAdd',msg2=msg2)
		except:
			return render_template('StaffAdd', msg2 = 'Failed to add the airplane.')

#Define route for Airline Staff Add Airport
@app.route('/StaffAddAirports', methods=['GET', 'POST'])
def StaffAddAirports():
	if request.method == 'POST':
		airport_name = request.form['Airport_Name']
		airport_city = request.form['Airport_City']
		username = session['username3']

		cursor = conn.cursor()
		query1 = "SELECT permission_id FROM permission WHERE username = %s"
		cursor.execute(query1, (username))
		p_id = cursor.fetchone()

		if not p_id:
			msg3 = 'You don\'t have permission to add airports!'
			return render_template('StaffAdd',msg3=msg3)			
		elif p_id['permission_id'] != 1 and p_id['permission_id'] != 3:
			msg3 = 'You don\'t have permission to add airports!'
			return render_template('StaffAdd',msg3=msg3)
		
				
		query3 = "SELECT * FROM airport WHERE airport_name= %s"
		cursor.execute(query3, (airport_name))
		existing = cursor.fetchone()
		if existing:
			msg3 = "This airport already exists."
			return render_template('StaffAdd',msg3=msg3)			

		try:
			ins = "INSERT INTO airport VALUES(%s,%s)"
			cursor.execute(ins, (airport_name,airport_city))
			conn.commit()
			cursor.close()
			msg3 = "Successfully added an airport!"
			return render_template('StaffAdd',msg3=msg3)
		except pymysql.Error as err:
			return render_template('StaffAdd', msg3 = err)

#Define route for Airline Staff To Grant Permission
@app.route('/StaffAddPermissions', methods=['GET', 'POST'])
def StaffAddPermissions():
	if request.method == 'POST':
		staff_to_grant = request.form['staff_to_grant']
		permission_id_to_grant = int(request.form['permission_id_to_grant'])
		username = session['username3']

		cursor = conn.cursor()
		query1 = "SELECT permission_id FROM permission WHERE username = %s"
		cursor.execute(query1, (username))
		p_id = cursor.fetchone()

		if not p_id or (p_id['permission_id'] not in (1, 3)):
			msg4 = 'You don\'t have permission to grant permission!'
			return render_template('StaffAdd',msg4=msg4)
		
		query = 'SELECT airline_name from airline_staff WHERE username = \'{}\''
		cursor.execute(query.format(username))
		my_name = cursor.fetchone()['airline_name']
		cursor.execute(query.format(staff_to_grant))
		staff_name = cursor.fetchone()['airline_name']

		if my_name != staff_name:
			msg4 = 'You don\'t have permission to grant permission to staff in another airline!'
			return render_template('StaffAdd',msg4=msg4)

		# query2 = "SELECT airline_name from airline_staff WHERE username=%s"
		# cursor.execute(query2, (username))
		# company = cursor.fetchone()['airline_name']

		# Use procedure to get staff company
		cursor.callproc('get_staff_company',(username,))
		company = cursor.fetchone()['airline_name']

		query3 = "SELECT airline_name FROM airline_staff WHERE username= %s"
		cursor.execute(query3, (staff_to_grant))
		staff_to_grant_company = cursor.fetchone()
		if not staff_to_grant_company:
			msg4 = "{} is not a registered staff for any airline!"
			msg4 = msg4.format(staff_to_grant)
			return render_template('StaffAdd',msg4=msg4)	
		if staff_to_grant_company['airline_name'] != company:
			msg4 = "You can't grant permission to other airline's staff."
			return render_template('StaffAdd',msg4=company)			
		if permission_id_to_grant not in (1, 2, 3):
			msg4 = "Please input a feasible admin type. 1 stands for admin, 2 stands for operator, 3 stands for both."
			return render_template('StaffAdd',msg4=msg4)

		query4 = "SELECT permission_id FROM permission WHERE username=%s"
		cursor.execute(query4, (staff_to_grant))
		existing = cursor.fetchone()
		if existing:
			# have 1, grant 2; have 2, grant 1.
			if existing["permission_id"] not in (3, permission_id_to_grant):
				try:
					ins = f"UPDATE permission SET permission_id = 3 WHERE username = \'{staff_to_grant}\'"
					cursor.execute(ins)
					conn.commit()
					cursor.close()
					msg4 = "Successfully granted permission of both Admin and Operator!"
					return render_template('StaffAdd',msg4=msg4)
				except Exception as err:
					return render_template('StaffAdd',msg4=f'{username} {ins} Failed to grant permission.')
			else:
				return render_template('StaffAdd',msg4="The staff has already have the permission you granted!")
		else:
			# no permission before
			try:
				ins = "INSERT INTO permission VALUES(%s,%s)"
				cursor.execute(ins, (staff_to_grant,permission_id_to_grant))
				conn.commit()
				cursor.close()
				msg4 = "Successfully granted the permission of {}!"
				administrative_dict = {1:"Admin",2:"Operator",3:"Admin and Operator"}
				msg4 = msg4.format(administrative_dict[permission_id_to_grant])
				return render_template('StaffAdd',msg4=msg4)
			except:
				return render_template('StaffAdd',msg4='Failed to grant permission.')

#Define route for Airline Staff To ADD booking agents for his/her airline
@app.route('/StaffAddBookingAgents', methods=['GET', 'POST'])
def StaffAddBookingAgents():
	if request.method == 'POST':
		#grabs information from the forms
		email_of_agent_to_add = request.form['email_of_agent_to_add']


		username = session['username3']
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query1 = "SELECT permission_id FROM permission WHERE username = %s"
		cursor.execute(query1, (username))
		#stores the results in a variable
		p_id = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		if not p_id:
			msg5 = 'You don\'t have permission to add booking agents!'
			return render_template('StaffAdd',msg5=msg5)			
		elif p_id['permission_id'] != 1 and p_id['permission_id'] != 3:
			msg5 = 'You don\'t have permission to add booking agents!'
			return render_template('StaffAdd',msg5=msg5)
		
		# query2 = "SELECT airline_name from airline_staff WHERE username=%s"
		# cursor.execute(query2, (username))
		# company = cursor.fetchone()['airline_name']

		# Use procedure to get staff company
		cursor.callproc('get_staff_company',(username,))
		company = cursor.fetchone()['airline_name']

		query3 = "SELECT * FROM booking_agent WHERE email= %s"
		cursor.execute(query3, (email_of_agent_to_add))
		is_registered_agent = cursor.fetchone()
		if not is_registered_agent:
			msg5 = "{} is not a registered booking agent!"
			msg5 = msg5.format(email_of_agent_to_add)
			return render_template('StaffAdd',msg5=msg5)

		query4 = "SELECT * FROM works_for WHERE email=%s and airline_name=%s"	
		cursor.execute(query4, (email_of_agent_to_add,company))
		already_added = cursor.fetchone()
		if already_added:
			msg5 = "{} is already an added booking agent works for your airline company!"
			msg5 = msg5.format(email_of_agent_to_add)
			return render_template('StaffAdd',msg5=msg5)			

		try:
			ins = "INSERT INTO works_for VALUES(%s,%s)"
			cursor.execute(ins, (email_of_agent_to_add,company))
			conn.commit()
			cursor.close()
			msg5 = "Successfully added a booking agent to work for your airline company!"
			return render_template('StaffAdd',msg5=msg5)
		except:
			return render_template('StaffAdd', msg5 = 'Failed to add booking agent.')

#Define route for Airline Staff View Top 5 Booking Agents
@app.route('/StaffViewTopAgents', methods=['GET', 'POST'])
def StaffViewTopAgents():
	msg1=''
	msg2=''
	msg3=''
	msg4=''
	cursor = conn.cursor()
	today = datetime.now()
	last_month_today = today-relativedelta(months=1)
	create_view_query = "CREATE or REPLACE VIEW commission as ( SELECT booking_agent_id,sum(price*0.1) as total_commission, count(*) as num_of_tickets from purchases NATURAL join ticket NATURAL join flight WHERE purchase_date BETWEEN \'{}\' AND \'{}\' GROUP BY booking_agent_id HAVING booking_agent_id is NOT Null)"
	cursor.execute(create_view_query.format(last_month_today,today))
	query = "SELECT booking_agent_id from commission c1 WHERE 4>=(SELECT COUNT(DISTINCT booking_agent_id) from commission c2 WHERE c2.total_commission > c1.total_commission)"
	cursor.execute(query)
	last_month_bycommission = cursor.fetchall()
	if not last_month_bycommission:
		msg1 = "No booking agents can be returned."
	
	query = "SELECT booking_agent_id from commission c1 WHERE 4>=(SELECT COUNT(DISTINCT booking_agent_id) from commission c2 WHERE c2.num_of_tickets > c1.num_of_tickets)"
	cursor.execute(query)
	last_month_bynum = cursor.fetchall()
	if not last_month_bynum:
		msg2 = "No booking agents can be returned."
	
	last_6month_today = today-relativedelta(months=6)
	create_view_query = "CREATE or REPLACE VIEW commission as ( SELECT booking_agent_id,sum(price*0.1) as total_commission, count(*) as num_of_tickets from purchases NATURAL join ticket NATURAL join flight WHERE purchase_date BETWEEN \'{}\' AND \'{}\' GROUP BY booking_agent_id HAVING booking_agent_id is NOT Null)"
	cursor.execute(create_view_query.format(last_6month_today,today))
	query = "SELECT booking_agent_id from commission c1 WHERE 4>=(SELECT COUNT(DISTINCT booking_agent_id) from commission c2 WHERE c2.total_commission > c1.total_commission)"
	cursor.execute(query)
	last_6month_bycommission = cursor.fetchall()
	if not last_6month_bycommission:
		msg3 = "No booking agents can be returned."
	
	query = "SELECT booking_agent_id from commission c1 WHERE 4>=(SELECT COUNT(DISTINCT booking_agent_id) from commission c2 WHERE c2.num_of_tickets > c1.num_of_tickets)"
	cursor.execute(query)
	last_6month_bynum = cursor.fetchall()
	if not last_6month_bynum:
		msg4 = "No booking agents can be returned."
	return render_template('StaffViewTopAgents',last_month_bycommission=last_month_bycommission,last_month_bynum=last_month_bynum,last_6month_bycommission=last_6month_bycommission,last_6month_bynum=last_6month_bynum,msg1=msg1,msg2=msg2,msg3=msg3,msg4=msg4)

#Define route for Airline Staff View Top Frequent Customer
@app.route('/StaffViewFrequentCustomer', methods=['GET', 'POST'])
def StaffViewFrequentCustomer():

	msg1=''
	username = session["username3"]
	cursor = conn.cursor()

	query1 = "SELECT airline_name from airline_staff WHERE username=%s"
	cursor.execute(query1, (username))
	company = cursor.fetchone()['airline_name']

	today = datetime.now()
	last_year_today = today-relativedelta(days=1*365)
	create_view_query = "CREATE or REPLACE VIEW top_customer as \
		(SELECT name,customer_email,phone_number,passport_country, count(*) \
		as total_flights from ticket NATURAL JOIN flight NATURAL JOIN purchases\
		JOIN customer ON purchases.customer_email=customer.email WHERE departure_time BETWEEN \'{}\' \
		AND \'{}\' and flight.airline_name = \'{}\' GROUP BY customer_email)"
	cursor.execute(create_view_query.format(last_year_today,today,company))
	query = "SELECT * from top_customer t1 WHERE 0=(SELECT COUNT(DISTINCT customer_email) \
		from top_customer t2 WHERE t2.total_flights> t1.total_flights)"
	cursor.execute(query)
	top_freq_cust = cursor.fetchall()
	if not top_freq_cust:
		msg1="No customer can be returned."
		return render_template('StaffViewFrequentCustomer',msg1=msg1)
	
	topcust_flightlist=[]
	for row in top_freq_cust:
		# topcust_flightlist.append(row['customer_email'])
		query="SELECT name,customer_email,airline_name,flight_num,COUNT(ticket_id) AS ticket_count,\
			departure_time,departure_airport,arrival_time,arrival_airport,price,status \
			FROM ticket NATURAL join purchases NATURAL join flight JOIN customer \
			on purchases.customer_email=customer.email WHERE airline_name = %s AND customer_email = %s \
			AND departure_time < %s \
			GROUP BY name,customer_email,airline_name,flight_num,departure_time,\
			departure_airport,arrival_time,arrival_airport,price,status"
		cursor.execute(query,(company,row['customer_email'],today))
		topcust_flightlist.append(cursor.fetchall())


	return render_template('StaffViewFrequentCustomer',top_freq_cust=top_freq_cust,msg1=msg1,topcust_flightlist=topcust_flightlist)


#Define route for airline staff view report
@app.route('/StaffReport', methods=['GET', 'POST'])
def StaffReport():
	msg = 'Between {} and {}, the airline you work for sold {} tickets in total.'

	username = session['username3']
	cursor = conn.cursor()

	# query1 = "SELECT airline_name from airline_staff WHERE username=%s"
	# cursor.execute(query1, (username))
	# company = cursor.fetchone()['airline_name']

	# Use procedure to get staff company
	cursor.callproc('get_staff_company',(username,))
	company = cursor.fetchone()['airline_name']

	query = "SELECT count(*) as ticket_sold \
			from purchases NATURAL JOIN ticket WHERE airline_name = \'{}\'\
			and purchase_date BETWEEN \'{}\' and \'{}\'"
	today = datetime.now()
	last_year_today = datetime.now() - timedelta(days=1*365)
	cursor.execute(query.format(company,last_year_today,today))
	one_year_sold_num = cursor.fetchone()["ticket_sold"]
	msg1 = msg.format(last_year_today.date(), today.date(), one_year_sold_num)

	m = 12
	month_sold_num_list = [0]*m
	month_list = [0]*m
	this_month_today = datetime.now()
	for i in range(m):
		month_list[i]= int(this_month_today.strftime("%m"))
		cursor = conn.cursor()
		query = "SELECT count(*) as ticket_sold from purchases NATURAL JOIN ticket WHERE airline_name = \'{}\' and purchase_date BETWEEN \'{}\' and \'{}\'"


		last_month_today = this_month_today - relativedelta(months=1)
		cursor.execute(query.format(company,last_month_today,this_month_today))
		row = cursor.fetchone()
		month_sold_num_list[i] = row["ticket_sold"]

		this_month_today = last_month_today

	month_list = month_list[::-1]
	month_list = json.dumps(month_list)
	month_sold_num_list = month_sold_num_list[::-1]
	month_sold_num_list = json.dumps(month_sold_num_list)

	if request.method == 'POST':
		TicketSoldDateRange = request.form['TicketSoldDateRange'] # in form of 2023/04/29 - 2023/05/12 , class = string
		StartRange = TicketSoldDateRange.split("-")[0].strip()    # in form of 2023/04/29 , class = string
		EndRange = TicketSoldDateRange.split("-")[1].strip()      # in form of 2023/05/12 , class = string
		StartRange = StartRange.replace('/','-')                  # in form of 2023-04-29, class = string
		EndRange = EndRange.replace('/','-')                      # in form of 2023-05-12, class = string
		StartRange = datetime.strptime(StartRange, '%Y-%m-%d')    # in form of 2023-04-29 00:00:00, class = datetime
		EndRange = datetime.strptime(EndRange, '%Y-%m-%d')        # in form of 2023-05-12 00:00:00, class = datetime

		m = 0
		month_sold_num_list= []
		month_list = []
		this_month_today = EndRange
		while this_month_today>=StartRange:
			m+=1
			month_list.append(int(this_month_today.strftime("%m"))) 
			cursor = conn.cursor()
			query = "SELECT count(*) as ticket_sold from purchases NATURAL JOIN ticket \
			WHERE airline_name = \'{}\' and purchase_date BETWEEN \'{}\' and \'{}\'"
			last_month_today = this_month_today - relativedelta(months=1)
			cursor.execute(query.format(company,last_month_today,this_month_today))
			row = cursor.fetchone()
			month_sold_num_list.append(int(row["ticket_sold"]))
			this_month_today = last_month_today
		month_list = month_list[::-1]
		month_list = json.dumps(month_list)
		month_sold_num_list = month_sold_num_list[::-1]
		sold_sum = str(sum(month_sold_num_list))
		month_sold_num_list = json.dumps(month_sold_num_list)
		msg1 = msg.format(StartRange.date(), EndRange.date(), sold_sum)
	
	return render_template('StaffReport',msg1=msg1,month_sold_num_list=month_sold_num_list,month_list=month_list,m=m)

#Define route for airline-staff compare revenue
@app.route('/StaffComparison', methods=['GET', 'POST'])
def StaffComparison():
	username = session['username3']
	cursor = conn.cursor()

	# query1 = "SELECT airline_name from airline_staff WHERE username=%s"
	# cursor.execute(query1, (username))
	# company = cursor.fetchone()['airline_name']

	# Use procedure to get staff company
	cursor.callproc('get_staff_company',(username,))
	company = cursor.fetchone()['airline_name']

	query2 = "SELECT IFNULL(sum(price),0) as direct_sum from purchases \
		NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\'  \
		and purchase_date BETWEEN \'{}\' and \'{}\' and booking_agent_id is Null"
	today = datetime.now()
	last_year_today = datetime.now() - relativedelta(days=1*365)
	cursor.execute(query2.format(company,last_year_today,today))
	sum = cursor.fetchone()
	if not sum:
		one_year_direct_sum = 0
	else:
		one_year_direct_sum = sum["direct_sum"]

	query3 = "SELECT IFNULL(sum(price),0) as indirect_sum from purchases \
		NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\'  \
		and purchase_date BETWEEN \'{}\' and \'{}\' and booking_agent_id is NOT Null"
	cursor.execute(query3.format(company,last_year_today,today))
	sum = cursor.fetchone()
	if not sum:
		one_year_indirect_sum = 0
	else:
		one_year_indirect_sum = sum["indirect_sum"]

	last_year_revenue_list = [math.floor(one_year_direct_sum),math.floor(one_year_indirect_sum)]
	last_year_revenue_list = json.dumps(last_year_revenue_list)

	query4 = "SELECT IFNULL(sum(price),0) as direct_sum from purchases \
		NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\'  \
		and purchase_date BETWEEN \'{}\' and \'{}\' and booking_agent_id is Null"
	today = datetime.now()
	last_month_today = datetime.now() - relativedelta(days=1*30)
	cursor.execute(query4.format(company,last_month_today,today))
	sum = cursor.fetchone()
	if not sum:
		one_month_direct_sum = 0
	else:
		one_month_direct_sum = sum["direct_sum"]

	query5 = "SELECT IFNULL(sum(price),0) as indirect_sum from purchases \
		NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = \'{}\'  \
		and purchase_date BETWEEN \'{}\' and \'{}\' and booking_agent_id is NOT Null"
	cursor.execute(query5.format(company,last_month_today,today))
	sum = cursor.fetchone()
	if not sum:
		one_month_indirect_sum = 0
	else:
		one_month_indirect_sum =sum["indirect_sum"]

	last_month_revenue_list = [math.floor(one_month_direct_sum),math.floor(one_month_indirect_sum)]
	last_month_revenue_list = json.dumps(last_month_revenue_list)
 
	return render_template('StaffComparison',last_year_revenue_list=last_year_revenue_list,last_month_revenue_list=last_month_revenue_list)

#Define route for airline-staff view top3 popular destinations
@app.route('/StaffViewPopularDestinations', methods=['GET', 'POST'])
def StaffViewPopularDestinations():
	msg1=''
	msg2=''

	cursor = conn.cursor()
	today = datetime.now()
	last_3month_today = today-relativedelta(months=3)
	create_view_query = "CREATE or REPLACE view popular_dest as (SELECT airport_city, COUNT(*) AS num_flights \
		FROM airport P JOIN flight F on P.airport_name=F.arrival_airport JOIN ticket T on F.airline_name=T.airline_name \
		and F.flight_num=T.flight_num WHERE F.departure_time BETWEEN \'{}\' and \'{}\' GROUP BY P.airport_city)"
	cursor.execute(create_view_query.format(last_3month_today,today))
	query = "SELECT airport_city from popular_dest p1 WHERE 2>=(SELECT COUNT(DISTINCT airport_city) \
		from popular_dest p2 WHERE p2.num_flights > p1.num_flights)"
	cursor.execute(query)
	last_3month_topdest = cursor.fetchall()
	if not last_3month_topdest:
		msg1 = "No destination can be returned for last 3 month as departure date."
	
	
	last_year_today = today-relativedelta(year=1)
	create_view_query = "CREATE or REPLACE view popular_dest as (SELECT airport_city, COUNT(*) AS num_flights \
		FROM airport P JOIN flight F on P.airport_name=F.arrival_airport JOIN ticket T on F.airline_name=T.airline_name \
		and F.flight_num=T.flight_num WHERE F.departure_time BETWEEN \'{}\' and \'{}\' GROUP BY P.airport_city)"
	cursor.execute(create_view_query.format(last_year_today,today))
	query = "SELECT airport_city from popular_dest p1 WHERE 2>=(SELECT COUNT(DISTINCT airport_city) \
		from popular_dest p2 WHERE p2.num_flights > p1.num_flights)"
	cursor.execute(query)
	last_year_topdest = cursor.fetchall()
	if not last_year_topdest:
		msg2 = "No destination can be returned for last a year as departure date."
	

	return render_template('StaffViewPopularDestinations',last_3month_topdest=last_3month_topdest,last_year_topdest=last_year_topdest,msg1=msg1,msg2=msg2)


#Define route for About
@app.route('/About', methods=['GET', 'POST'])
def About():
	return render_template('About')

if __name__ == "__main__":
	app.run('127.0.0.1', 5500, debug = True)