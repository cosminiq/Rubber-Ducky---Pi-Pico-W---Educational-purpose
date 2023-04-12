#=================== Import Library===================================================
import socketpool
import wifi
import microcontroller
import os
import digitalio
import time
import board
import storage
#=====================================================================================
#=================== Import Web server Library========================================
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.methods import HTTPMethod
#=====================================================================================
#=================== Import i2c and LCD 16x2==========================================
import busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
#=====================================================================================
#=================== Parsing the Payload code=========================================
from ducky import *
#=====================================================================================
#=========================WEB APP=====================================================
import json
import binascii
#=====================================================================================
#==============Initiate I2c communication line for LCD================================ 
i2c = busio.I2C(board.GP17, board.GP16)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=2, num_cols=16)
# Talk to the LCD at I2C address 0x27.
# The number of rows and columns defaults to 2x16, so those
# arguments could be omitted in this case.
#========================================================================================

#=======================  Create Acces Point (default IP 192.168.1.4)====================
print("Connecting to WiFi", os.getenv('CIRCUITPY_WIFI_SSID'))
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
server.start(str(wifi.radio.ipv4_address))
#===========================================================================================
folder_path = "/Payload"
files = os.listdir(folder_path)
#===========================================================================================

#============Generate butons wor web page with the name of files============================
def generate_file_buttons():
    folder_path = "/Payload"
    files = os.listdir(folder_path)
    buttons = []
    for file in files:
        if os.listdir(folder_path):
            button ='<form method="POST" action=""><br><button type="submit" name="file" value="{}">{}</button><input type="hidden" name="clicked_button" value="{}"></form>'.format(file, file, file)
            buttons.append(button)
    return (' '.join(buttons))
#============================================================================================

#==========Generate links wor web page with the name of files=================================
def generate_table_rows(files):
    folder_path = "/Payload"
    files = os.listdir(folder_path)
    # Generate HTML for each file as a link in a table row
    table_rows = ""
    for file in files:
        file_path = folder_path+"/"+ file
        link = "<a href='{}'>{} </a>".format(file_path, file_path)
        table_row = "<tr><td><br>{}</td></tr>".format(link)
        table_rows += table_row
    return table_rows 
#============================================================================================

def scan_networks():
    # Scan for available Wi-Fi networks
    networks = {}
    for network in wifi.radio.start_scanning_networks():
        if network.ssid not in networks:
            networks[network.ssid] = {
                "rssi": network.rssi,
                "channel": network.channel
            }
        else:
            # Update the RSSI and channel for the existing network with the same SSID
            networks[network.ssid]["rssi"] = max(network.rssi, networks[network.ssid]["rssi"])
            networks[network.ssid]["channel"] = network.channel

    # Stop scanning for Wi-Fi networks
    wifi.radio.stop_scanning_networks()

    # Create an HTML table with the list of scanned networks
    table = "<table><tr><th>SSID</th><th>RSSI</th><th>Channel</th></tr>"
    for ssid, network_info in networks.items():
        table += "<tr><td style='border: 1px solid #ddd; padding: 8px;'>{}</td><td style='border: 1px solid #ddd; padding: 8px;'>{}</td><td style='border: 1px solid #ddd; padding: 8px;'>{}</td></tr>".format(
            ssid, network_info["rssi"], network_info["channel"])
    table += "</table>"

    # Return the HTML table
    return table
#==================================================================================================


#=============Constants for internal Pico W=========================================================
mac= [hex(i) for i in wifi.radio.mac_address]
temperature= "{:.2f}".format(microcontroller.cpu.temperature)
frequency= microcontroller.cpu.frequency / 1000000 # convert to MHz
voltage=microcontroller.cpu.voltage
#=====================================================================================================

#==============================First mesage on LCD====================================================
def welcome_msg():
    lcd.clear()
    lcd.set_cursor_pos(0, 0)
    lcd.print("AP Pi_Pico_duck ")
    lcd.set_cursor_pos(1, 0)
    lcd.print(str(wifi.radio.ipv4_address))
welcome_msg()
#=======================================================================================================

#==============================WEB PAGES REQUEST -Web page 1=============================================
@server.route("/")
def base(request: HTTPRequest):
    """
    Serve the default index.html file.
    """
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(f"{webpage()}")
print(f"Listening on http://{wifi.radio.ipv4_address}:80")
#=====================================================================================================

#=================================WEB PAGES POST-Web page 1===========================================
@server.route("/", method=HTTPMethod.POST)
def buttonpress(request: HTTPRequest):
    folder_path = "/Payload"
    files = os.listdir(folder_path)
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    form_data = b''
    form_data += raw_text
    my_string = raw_text
    result = my_string.split('=')[1]
    print(my_string)

    if b'clicked_button' in form_data:
        button_value = form_data.split(b'clicked_button=')[1].split(b'&')[0].decode('utf-8')
        print("Button was pushed")
    # Send the button value to the Pico
    if button_value is not None:
        print("Recive the value of button as string :", button_value)
           
    if button_value in files:
        lcd.set_cursor_pos(1, 0)
        lcd.print("Executing.......")
        print ("Pyaload find in sistem ...  ")
        file_path = folder_path + '/' + button_value
        runScript(file_path)
        lcd.set_cursor_pos(1, 0)
        lcd.print("Executing  done!")

    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(f"{webpage()}")
#=====================================================================================================        

           
#=======================Constants (image and animation) for web page =================================
img_file = "/html/pico_w_small.jpg"
animation = "/html/c2.gif"
question="html/question.gif"
#====================================================================================================


#=====================================================================================================
#================================ WEB APP=============================================================
#=====================================================================================================
HTML_path="/Html/Web_app.html"

def _sendkeys(keys: list):
    print("keys", keys)
    for key in keys:
        if type(key) == str:
            runScript_buffer(key)

"""
@server.route("/")
def base(request: HTTPRequest):
    with open(HTML_path, "rb") as f:
        content = f.read()
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(content)
""" 
@server.route("/sendkeys", "GET")
def buttonpress(request: HTTPRequest):
    request_data = request.query_params
    #print("==========================")
    #print(request_data)
    
    try:
        keys = binascii.unhexlify(request_data["keys"])
        keys = json.loads(keys)
        keys = keys["keys"]
        print(keys)
    except ValueError as e:
        print(f"payload not sent: error {e}")
        
    _sendkeys(keys)    
    create_file_from_list(keys)
   
    with open(HTML_path, "rb") as f:
        content = f.read()
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(content)
        

def create_file_from_list(file_list: list):
    
    file_path="/Payload/"
    filename = file_list[0]
    file_content = "\n".join(file_list[1:])
    
    if len(filename) > 0 :
        storage.remount("/",readonly=False)
        with open(file_path + filename + ".txt", "w") as f:
            f.write(file_content)
        storage.remount("/",readonly=True) 



print(f"Listening on http://{wifi.radio.ipv4_address}/html/Web_app.html")

#=====================================================================================================
#=====================================================================================================
#=====================================================================================================












#=============================== WEB PAGE 1==========================================================
def webpage():
    html = f"""
    <!DOCTYPE html>
<html>
<head>
	<title>Educational hacking project</title>
	<style>
		body {{
			margin: 0;
			padding: 0;
			display: flex;
			flex-direction: row;
		}}
		nav {{
			width: 200px;
			background-color: #99CCFF;
			color: #fff;
			padding: 20px;
        	margin-top: 20px;
		}}
		main {{
			flex: 1;
			padding: 20px;
			
		}}
		.panel-container {{
			display: flex;
			flex-direction: row;
			margin-top: 20px;
		}}
		.panel {{
            flex: 1;
            background-color: #f2f2f2;
            padding: 20px;
            margin-right: 20px;
            box-sizing: border-box;
		}}
        .new-panel {{
            background-color: #99CCFF;
            padding: 20px;
            width: calc(100% - 23px);
            margin-bottom: 20px;
            box-sizing: border-box;
            text-align: center;
        }}
		p1 {{
            margin: 0;
            font-size: 13px;
            font-weight: bold;
            color: black;
            border: 1px solid #ddd;
            padding: 8px
            }}
        table1{{
            text-align:center
            }}
      
		
	</style>
</head>
<body>
	<nav>
		<ul>
			<br><li><a href="/Html/Web_app.html">Live payload</a></li>
			<br><li><a href="/Html/Haking_info.html">Hacking info</a></li>
			<br><li><a href="/Html/Programing_info.html">Programing info</a></li>
			<br><li><a href="/Html/electonic_info.html">Electronics used</a></li>
			<br><li><a href="#">About</a></li>
			<br><li><a href="#">How to use</a></li>
		</ul>
		<div id="gif-container">
          <img src={animation} alt="Animated GIF">
        </div>
	</nav>
	<main>
	
		<div class="new-panel">
			<h2 style="text-align: center;">Web server on Raspberry pi pico W</h2>
			<table1>
                <p1>Frequency (MHz): {frequency}</p1>
                <p1>Temperature (C): {temperature}</p1>
                <p1>Voltage (V): {voltage}</p1>
                <p1>Internall MAC adress: {mac} </p1>
            </table1>
		</div>
		
		<div class="panel-container">
		
			<div class="panel">
				<h2>Execute payload</h2>
				<p style='font-family: Arial, sans-serif; font-weight: bold;'>Push de buttons !!!</p>
				{generate_file_buttons()}
			</div>
			
			<div class="panel">
				<h2>Visualize the payload content.</h2>
				<p style='font-family: Arial, sans-serif; font-weight: bold;'>Click the link</p>
				    <table>
                        {generate_table_rows(files)}
                    </table>
			</div>
			
			<div class="panel">
				<h2>Wifi networks in range</h2>
				{scan_networks()}
				<img src={img_file} alt="Image" alt="Image" width="300" height="110" style=" position: center; bottom: 0;">
			</div>
		</div>
		
	</main>
</body>
</html>

    """
    return html
#=========================================================================================================



#=========================================================================================================


while True:
        try:
        # Do something useful in this section,
        # for example read a sensor and capture an average,
        # or a running total of the last 10 samples

        # Process any waiting requests
            server.poll()
        except OSError as error:
            print(error)
            continue





            
        
   






