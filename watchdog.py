#!/bin/python
# watchdog
# author: Cameron Larsen
# this script will monitor service now for tickets assigned your queues.
# BEFORE USING THIS SCRIPT YOU NEED TO INSTALL SELENIUM #
# pip install --user selenium #

import os
import sys
import time
import datetime
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from slackclient import SlackClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

# Slack API token
slack_token = "{slack token go here}"
sc = SlackClient(slack_token)

# define user info
sn_USER = "{username}"  # SN Username
sn_PASS = "{password}"  # SN Password
# define connection info
SN_URL = "https://{your SN domain}.service-now.com/incident_list.do?{URL query which displays the queues you wish to monitor}"
SN_LINKS = "https://{your SN domain}.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number="
# define driver and set options
os.system('unset QT_QPA_PLATFORM') # I had to add this to get it to work on Arch with QT5
SCRIPT_DIR = os.getcwd()
driver = webdriver.PhantomJS(SCRIPT_DIR + "/phantomjs", service_log_path=os.path.devnull, desired_capabilities={'phantomjs.page.settings.resourceTimeout': '10000', 'phantomjs.page.settings.loadImages': 'false'})
driver.implicitly_wait(10)   # # seconds
conn = sqlite3.connect(SCRIPT_DIR + "/incident.db")  # Connect to Database
c = conn.cursor()
c2 = conn.cursor()
# Log into sn
driver.get(SN_URL)
sn_enter_user = driver.find_element_by_name("userid")
sn_enter_user.send_keys(sn_USER)
sn_enter_pass = driver.find_element_by_name("password")
sn_enter_pass.send_keys(sn_PASS)
sn_submit_login = driver.find_element_by_name("Submit")
sn_submit_login.click()
driver.get(sn_URL)  # refresh the page
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "hdr_incident")))
# build list of incidents
time.sleep(5)
incidents_raw = []
for tr in driver.find_elements_by_xpath('//table[@id="incident_table"]//tr'):
    tds = tr.find_elements_by_tag_name('td')
    if tds:
        incidents_raw.append([td.text for td in tds])

for lst in incidents_raw:
    for j, item in enumerate(lst):
            lst[j] = item.replace("'", "")

for lst in incidents_raw:
    for j, item in enumerate(lst):
            lst[j] = item.replace("|", "")

active_incidents = []
for x in incidents_raw:
    active_incidents.append([x[1]])

incident_count = len(incidents_raw)

mk_str = ''.join(map(str, active_incidents))
mk_str = mk_str.replace("[", "")
comma_count = incident_count - 1
mk_str = mk_str.replace("]", ",", comma_count)
mk_str = mk_str.replace("]", "")
c.execute("DELETE FROM INCS WHERE incident_number NOT IN (" + mk_str + ")")
conn.commit()

# pump data into database
for x in range(incident_count):
    c.execute("INSERT OR IGNORE INTO INCS(incident_number,routing_company,created_time,incident_state,short_desc,assigned_to,incident_priority,assignment_group,updated_time) VALUES('"+incidents_raw[x][1]+"','"+incidents_raw[x][2]+"','"+incidents_raw[x][3]+"','"+incidents_raw[x][4]+"','"+incidents_raw[x][5]+"','"+incidents_raw[x][6]+"','"+incidents_raw[x][7]+"','"+incidents_raw[x][8]+"','"+incidents_raw[x][9]+"')")
    conn.commit()

for x in range(incident_count):
    c.execute("UPDATE OR IGNORE INCS SET incident_state='"+incidents_raw[x][4]+"', assigned_to='"+incidents_raw[x][6]+"', incident_priority='"+incidents_raw[x][7]+"', assignment_group='"+incidents_raw[x][8]+"', updated_time='"+incidents_raw[x][9]+"' where incident_number='"+incidents_raw[x][1]+"'")
    conn.commit()
# grab incidents that have not yet been broadcast
for row in c.execute('SELECT * FROM INCS WHERE broadcast is NULL'):
    row_message = '[{"title": "' + row[0] + ' - '+row[6]+' - '+row[3]+'\n <' + SN_LINKS + row[0] + '>", "pretext": "An Incident has been assigned to your group!", "text": "'+row[4]+'"}]'
    print(row[0])
    sc.api_call(
        "chat.postMessage",
        channel="{[channel you wish to post to]}",
        username="sn Alert",
        icon_url="{Icon URL}",
        attachments=row_message
    )
    c2.execute("UPDATE sn SET broadcast = 'y' WHERE incident_number = '"+row[0]+"'")


conn.commit()
c.close()
conn.close  # close connection to the DB
driver.quit()  # close the browser
