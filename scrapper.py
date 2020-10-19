#link: https://web.cs.wpi.edu/~cew/share/opps.html
from bs4 import BeautifulSoup as bs
import requests
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()

def job(t):
	now = datetime.datetime.now()
	fo = open('lastentry.txt', 'r')
	lastentry = fo.read()
	fo.close()
	link = 'https://web.cs.wpi.edu/~cew/share/opps.html'
	r = requests.get(link)
	page = r.text
	soup=bs(page, 'html.parser')
	lis = soup.find_all("li")


	def getList(lis):
	    newOppList = []
	    for li in lis:
	        txt = str(li)
	        inLi = False
	        inA = False
	        curText = ""
	        for i in range(0, len(txt)):
	            if txt[i] == '<' and txt[i+1] == 'l':
	                inLi = True
	            elif txt[i-1] == '>' and txt[i-2] == 'i':
	                inLi = False
	                if curText == "</li>" or curText.strip() == ',':
	                    curText=""
	                elif curText != "":
	                    newtxt = curText.strip()
	                    newtxt = newtxt.replace(',', '', 1)
	                    newtxt = newtxt.strip()
	                    newtxt = newtxt.replace('\n', '')
	                    if newtxt == lastentry:
	                        return newOppList
	                    else:
	                        newOppList.append(newtxt) 
	                    curText = ""
	            if txt[i] == '<' and txt[i+1] == 'a':
	                inA = True
	            elif txt[i-1] == '>' and txt[i-2] == 'a' and txt[i-3]=='/':
	                inA = False
	            if not inA and not inLi:
	                curText += txt[i]
	        
	        #what we wanna grab for the email:
	        #full opportunity (all txt between li)
	        #the link itself

	        #we use the former as our last seen opportunity.
	        
	        
	listOfNewOpportunities = getList(lis)
	listOfLinks = []
	listOfLinkText = []
	atags = soup.find_all('a')
	for i in range(0, len(listOfNewOpportunities)):
	    lnk = atags[i]['href']
	    if lnk[0]=='.':
	        lnk = 'https://web.cs.wpi.edu/~cew/share' + lnk[1:]
	    listOfLinks.append(lnk)
	    listOfLinkText.append(atags[i].getText())
	if len(listOfNewOpportunities) > 0:
	    fo = open("lastentry.txt", "w")
	    fo.write(listOfNewOpportunities[0])
	    fo.close()
	    #compose email here
	    curDate = str(now.month) + "-" + str(now.day) + "-" + str(now.year)
	    fullDate = curDate + ": CS Opportunities Updates\n\n"
	    fullMsg = fullDate
	    for i in range(0, len(listOfNewOpportunities)):
	        fullMsg += "(" + str(i+1) + ") " + listOfLinkText[i] + " " + listOfNewOpportunities[i] + ":\n     " + listOfLinks[i] + "\n"
	    fo = open("email.txt", "w")
	    fo.write(fullMsg)
	    fo.close()
	    port = 465
	    smtp_server = "smtp.gmail.com"
	    sender_email = os.getenv('wpicsscrapper@gmail.com')
	    receiver_email = os.getenv('RECEIVER_ADDRESS')
	    password = os.getenv('SENDER_PASSWORD') 
	    message = MIMEMultipart("alternative")
	    message["Subject"] = fullDate
	    message["From"] = sender_email
	    message["To"] = receiver_email
	    part1 = MIMEText(fullMsg, "plain")
	    message.attach(part1)
	    context = ssl.create_default_context()
	    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
	        server.login(sender_email, password)
	        server.sendmail(sender_email, receiver_email, message.as_string())
	        server.quit()
schedule.every().day.at("09:00").do(job,'It is 09:00') #can modify this.

while True:
	schedule.run_pending()
	time.sleep(86400) # wait 1 day

