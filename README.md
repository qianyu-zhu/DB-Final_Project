# DB-Final_Project
This is the repository for CSCI-SHU 213: Databases (Spring 2023). The final project is a web-based air-ticket reservation databases system.

## Team members
- Pinyu Chen (pc2753@nyu.edu)
- Qianyu Zhu (qz1086@nyu.edu)

## Tool used
Python Flask + html + CSS + MySQL databases

## Short introduction
The course project for this semester is online Air Ticket Reservation System. Using this system, customers can search for flights, purchase flights ticket, view their upcoming flight status or see their past flights, etc. There will be three types of users of this system - Customers, Booking Agents and Airline Staff (Administrator). Booking Agents will book flights for other Customers, can get a fixed commission. They can view their monthly reports and get total commission. Airline Staff will add new airplanes, create new flights, and update flight status. In general,this will be simple air ticket reservation system.

## To use the system
Download the project folder, and add graphical resources. They should be put under the `./project/static/` directory like this:
- `./project/static/video/`
- `./project/static/image/`

The resources can be found [here](https://drive.google.com/drive/folders/1pbf56wI_aPflQeJgG3sGhR2ilzUi4xct?usp=sharing).

The workflow is shown as below:
```shell
# Start the Flask server
python app.py
```
