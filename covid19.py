import requests
import os
import pandas as pd
import smtplib
from lxml import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import seaborn as sns
import matplotlib.pyplot as plt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition,To)
import base64
import mimetypes
from twilio.rest import Client
import telebot
from matplotlib.backends.backend_pdf import PdfPages
import time
import slack







# you can set cron job for linux like this
# * * * * * /usr/bin/python3  /to/path coronavirus.py >/dev/null 2>&1


class Coronavirus():
    def __init__(self):
       self.sender    = "sender@email.com"

       self.receiver  = [('receiver@email.com','John doe'),('another_receiver@email.com','Mary jane')]
       self.g_receiver = 'greceiver@email.com' #if using google

       self.to_emails = [ To( email='John@John.com' ,
        name='John Doe',
        substitutions={
        '-name-': 'John',
        },
        subject='Hi -name-, Here is today"s Corona Virus Update [ Covid19]' 

        ),

        To(email='Mary.b.Mary@Mary.com',
        name='Mary',
        substitutions = {
        '-name-' : 'Mary'
        }
        )
        ]

       self.password  = "password" # password if using  google's gmail
       self.attachments = ['coronaV.png', 'coronaV.csv','coronaV.pdf'] # attachments
       self.api = 'SG.xxxxx.xxxxxxx-xxxxx' #sendgrid api
       self.account_sid = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
       self.auth_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    #    twilio whats app
       self.to_whatsapp = [('+1xxxxxxxxxxxxxxxx','Mary'),('+xxxxxxxxxxxxxxx','John')]
       self.from_whatsapp = '+xxxxxxxxxxxxxxxxxxxx'

    #    telegram api token and chat id
       self.bot_token = 'xxxxxxxxxxxxxxxx:xxxxxxxxxxxxxxx-xxxxxxxxxx'
       self.bot_chatID = '654564773'
    
     #    slack token
       self.SLACK_API_TOKEN ='xoxb-xxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxx-xxxxx'


    # scrape worldometers
    def getCoronaData(self):
        url    = 'https://www.worldometers.info/coronavirus/'
        htmly  = requests.get(url).content
        htmlyr = html.fromstring(htmly)

        df_list = pd.read_html(htmly)
        Tcases = htmlyr.xpath('//*[@id="maincounter-wrap"]/div/span/text()')[0][:]
        TDeaths = htmlyr.xpath('//*[@id="maincounter-wrap"]/div/span/text()')[1][:]
        Recovered = htmlyr.xpath('//*[@id="maincounter-wrap"]/div/span/text()')[2][:]

        df = df_list[0]
        print(df)
        df.to_csv('coronaV.csv')
        pp = PdfPages("coronaV.pdf")
        pp.close()

        self.Plots(df)
        self.SendGrid(Tcases,TDeaths,Recovered)
        # self.sendgrid()
        self.notifyWhatsapp(Tcases,TDeaths,Recovered)
        self.notifyTelegram(Tcases,TDeaths,Recovered)
        self.notifySlack(Tcases,TDeaths,Recovered)
        self.DelFiles()


    # Send Notification emails with sendgrid
    def SendGrid(self,Tcases,TDeaths,Recovered):
         # # Add body to email
        body = """ <html>
                   <body>
                        <u><strong>COVID19<strong></u><br><br>
                            <b>Total Cases: {Tcases}  </b><br>
                            <b style="color:red">Total Deaths : {TDeaths}  </b><br>
                            <b>Recovered : {Recovered}  </b><br>
                            <a href="https://www.worldometers.info/coronavirus/" >Check the link: click here </a>
                    </body>
                    </html>
                """.format(Tcases=Tcases,TDeaths=TDeaths,Recovered=Recovered)


        message = Mail(
        from_email= (self.sender,'John Doe'),
        to_emails= self.receiver,
        subject='Corona Virus Update [ Covid19] [Local]',
        html_content=body,
        is_multiple= True)

        for filename in self.attachments:
            with open(filename, 'rb') as f:
                data = f.read()
                f.close()
                encoded_file = base64.b64encode(data).decode()

                attachedFile = Attachment(
                    FileContent(encoded_file),
                    FileName(filename),
                    FileType(mimetypes.guess_type(filename)[0]),
                    Disposition('attachment')
                )
                print("filename =%s " % filename)
                print(mimetypes.guess_type(filename))
                message.attachment = attachedFile

        try:
            sg = SendGridAPIClient(self.api)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)

        
    # Send emails using googles gmail
    def SendEmail(self,Tcases,TDeaths,Recovered):
        msg = MIMEMultipart()

        msg['Subject'] = 'Corona Virus Update [ Covid19]'
        msg['From'] = self.sender
        msg['To'] =   self.g_receiver
        
        # # Add body to email
        body = 'Total Cases: ' + Tcases + '\
        \nTotal Deaths : ' + TDeaths + '\
        \nRecovered : ' + Recovered + '\
        \nCheck the link: https://www.worldometers.info/coronavirus/'
        msg.attach(MIMEText(body,"plain"))
            
        
        if  len(self.attachments) > 0: # are there attachments?
            
            for filename in self.attachments:
                f = filename
                part = MIMEBase('application', "octet-stream")
                part.set_payload( open(f,"rb").read() )
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
                msg.attach(part)


        
        user = self.sender
        password = self.password
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.connect("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.sendmail(self.sender, self.receiver, msg.as_string())
        print("Successfully sent email")
        server.quit()

       
        
    def Plots(self,df):
        df2 = df[['Country,Other','TotalCases','TotalDeaths','TotalRecovered','Serious,Critical']]
        df2 = df2.head(10)
        
        df2= pd.melt(df2, id_vars=['Country,Other']).sort_values(['variable','value'])
        
        g = sns.catplot(x="Country,Other", y="value", hue="variable", data=df2,height=6, kind="bar", palette = 'twilight',aspect=1.5)
        g.despine(left=True,bottom=True)
        g.set_xlabels("Countries")
        g.set_ylabels("Cases in thousands")
        plt.xticks(rotation=90)
        plt.title('Ten(10) With Most covid19 cases')
        g.savefig("coronaV.png")
        
    
    def DelFiles(self):
        files = ['coronaV.png', 'coronaV.csv','coronaV.pdf']
        for f in files:
            os.remove(f)


    
    
    def notifyTelegram(self,Tcases,TDeaths,Recovered):


        message ='ℍ𝔼ℝ𝔼 𝕀𝕊 𝕋𝕆𝔻𝔸𝕐𝕊 ℂ𝕆ℝ𝕆ℕ𝔸 𝕍𝕀ℝ𝕌𝕊 𝕌ℙ𝔻𝔸𝕋𝔼 [ ℂ𝕆𝕍𝕀𝔻𝟙𝟡] 👹 \
        \nTotal Cases: ' + Tcases + '\
        \nTotal Deaths : ' + TDeaths + '\
        \nRecovered : ' + Recovered + '\
        \nCheck the link: https://www.worldometers.info/coronavirus/'


        send_text = 'https://api.telegram.org/bot' + self.bot_token + '/sendMessage?chat_id=' + self.bot_chatID + '&parse_mode=Markdown&text=' + message

        requests.get(send_text)

        # url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        # files = {'photo': open('coronaV.png', 'rb')}
        # data = {'chat_id' : self.bot_chatID}
        # r= requests.post(url, files=files, data=data)
        # print(r.status_code, r.reason, r.content)

        bot = telebot.TeleBot(self.bot_token)
        # doc = open('book.csv', 'rb')
        # bot.send_document(self.bot_chatID, doc)
        # bot.send_document(self.bot_chatID, "FILEID")




        for media in self.attachments:
            ext = os.path.splitext(media)[-1].lower()
            print(ext)

            if ext == ".pdf":
                doc = open(media, 'rb')
                bot.send_document(self.bot_chatID, doc)


            if ext == ".png": 
                doc = open(media, 'rb')
                bot.send_photo(self.bot_chatID, doc)
        print("Telegram Notification Sent!")


            
        

    
    def notifyWhatsapp(self,Tcases,TDeaths,Recovered):

        client = Client(self.account_sid,self.auth_token)
        from_whatsapp_number = 'whatsapp:'+self.from_whatsapp
        to_whatsapp_number = self.to_whatsapp

        if len(to_whatsapp_number) >0:
            for num in to_whatsapp_number:
                client.messages.create(
                            body=""" Hi {jina},  ℍ𝔼ℝ𝔼 𝕀𝕊 𝕋𝕆𝔻𝔸𝕐𝕊 ℂ𝕆ℝ𝕆ℕ𝔸 𝕍𝕀ℝ𝕌𝕊 𝕌ℙ𝔻𝔸𝕋𝔼 [ ℂ𝕆𝕍𝕀𝔻𝟙𝟡] 👹 

                𝕿𝖔𝖙𝖆𝖑 𝕮𝖆𝖘𝖊𝖘 : {Tcases} 
                𝕿𝖔𝖙𝖆𝖑 𝕯𝖊𝖆𝖙𝖍𝖘 : {TDeaths}
                𝕽𝖊𝖈𝖔𝖛𝖊𝖗𝖊𝖉  : {Recovered} 
                              """.format(jina = num[1] ,Tcases=Tcases,TDeaths=TDeaths,Recovered=Recovered) ,
                            from_=from_whatsapp_number,
                            to='whatsapp:'+num[0])
        print("Whatsapp Notification Sent!")
        
        
      
    
     def notifySlack(self,Tcases,TDeaths,Recovered):
        client = slack.WebClient(token=self.SLACK_API_TOKEN)
        body=""" Hi,  ℍ𝔼ℝ𝔼 𝕀𝕊 𝕋𝕆𝔻𝔸𝕐𝕊 ℂ𝕆ℝ𝕆ℕ𝔸 𝕍𝕀ℝ𝕌𝕊 𝕌ℙ𝔻𝔸𝕋𝔼 [ ℂ𝕆𝕍𝕀𝔻𝟙𝟡] 👹 
        𝕿𝖔𝖙𝖆𝖑 𝕮𝖆𝖘𝖊𝖘 : {Tcases} 
        𝕿𝖔𝖙𝖆𝖑 𝕯𝖊𝖆𝖙𝖍𝖘 : {TDeaths}
        𝕽𝖊𝖈𝖔𝖛𝖊𝖗𝖊𝖉    : {Recovered}""".format(Tcases=Tcases,TDeaths=TDeaths,Recovered=Recovered)

        response = client.chat_postMessage(
            channel='#diy-projects',
            text=body)
        assert response["ok"]

        for media in self.attachments:
            resUpload = client.files_upload(
            channels='#diy-projects',
            file=media)
            assert resUpload["ok"]
        print("Slack Notification Sent!")


            
        


Coronavirus().getCoronaData()
        
