import os
from flask import Flask, request ,json
import datetime
from flask import Response
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

@app.route('/', methods=['GET'])
def main():
    return "good"

@app.route('/health',methods=["GET"])
def health():
    return "ok"

@app.route('/gitcomm' , methods=['POST'])
def git_api_comm():
    if request.headers['Content-Type'] == 'application/json':
       
        my_commit = request.json
        jsonDump = json.dumps(my_commit)
        jsonLoad = json.loads(jsonDump)

        branch_ref = jsonLoad["ref"]

        directory_ref = jsonLoad["commits"][-1]

        branch = branch_ref.split("/")[2]
        print(branch)
        realDir = directory_ref["modified"]
        realadded = directory_ref["added"]
        if realDir:
            dirToString = str(realDir)
        else:
            dirToString = str(realadded)
        #dirToString = str(realDir)
        realFolder = dirToString.split("/")[0]
        pureFolder = realFolder.replace("['","")
        
        print(pureFolder)

        date = datetime.datetime.now()
        dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
        nm_dt = date.strftime("%d/%m/%Y_%H")
        with open(f"./logFile_"+nm_dt+".txt", "a+") as com_log:
            com_log.write("[{0}] {4} {1} {2} {3}".format(dt_string,branch,pureFolder,com_msg,author))
            com_log.write("\n")

        os.chdir("/gan-shmuel/")
        os.system("ls -a")
        os.system("git checkout origin/" + branch)
        os.system("git checkout " + branch)
        os.system("git pull")
        os.chdir(pureFolder)
        #os.system("pushd "+pureFolder)
        os.system("docker-compose up --detach --build")
        #os.system("popd")
        os.chdir("../..")

        return my_commit


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'autmailer101@gmail.com'
app.config['MAIL_PASSWORD'] = '12341234!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/mailer')
def maiLogger():
    with app.app_context():
        mail_list=["oronboy100@gmail.com","eilon696@gmail.com","ron981@gmail.com"]
        for m in range(len(mail_list)):
            msg = Message('LogFile Just For you Green Team Leaders!()', sender = 'autmailer101@gmail.com', recipients = [mail_list[m]])
            msg.body = "Hello from Green Devops AutoMailer! \n Weve got new log for you (Attached)"
            with app.open_resource("logFile_"+nm_dt+".txt"") as fp:
                msg.attach("logFile_"+nm_dt+".txt"", "text/plain", fp.read()) 
            mail.send(msg)
            return "Sent!"



if __name__ == '__main__':
    scheduler.add_job(id ='Scheduled task', func = maiLogger , trigger = 'interval', minutes = 720)
    scheduler.start()
    app.run(host='0.0.0.0')
