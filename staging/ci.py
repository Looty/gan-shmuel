import os
from flask import Flask, request ,json
import datetime
from flask import Response
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()


with open("logfile.log","w") as com_log:
    com_log.write("")

@app.route('/', methods=['GET'])
def main():
    return "wellcome to CI"

@app.route('/health',methods=["GET"])
def health():
    return "CI up"

@app.route('/gitcomm' , methods=['POST'])
def git_api_comm():
    if request.headers['Content-Type'] == 'application/json':
       
        my_commit = request.json
        jsonDump = json.dumps(my_commit)
        jsonLoad = json.loads(jsonDump)

        branch_ref = jsonLoad["ref"]

        directory_ref = jsonLoad["commits"][-1]
        com_msg = directory_ref["message"]
        author = directory_ref["author"]['email']
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

        with open("logfile.log","a") as com_log:
            date = datetime.datetime.now()
            dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
            com_log.write("[{0}] {4} {1} {2} {3} {5}".format(dt_string,branch,pureFolder,com_msg,author,"\n"))

        os.chdir("/gan-shmuel/")
        os.system("ls -a")
        os.system("git checkout origin/" + branch)
        os.system("git checkout " + branch)
        os.system("git pull")
        os.chdir(pureFolder)

        if branch != "Devops":
            os.system("docker-compose --env-file ./config/.env.test up --detach --build")
            os.system('docker exec -i $(docker container ps --filter label=container=app --filter label=team=' + branch.lower() + ' --format "{{.ID}}") sh')

            #print(str(subprocess.check_output(['python3', 'app/test.py'])))
            #test_result = subprocess.check_output(['python3', 'app/test.py'])
            #print(subprocess.getoutput('python3 app/test.py'))
            #test_result = subprocess.getoutput('python3 app/test.py')
            os.system('python3 app/test.py')
            test_result = os.system('echo $?')
            print(test_result)

            
            str_stop = "docker stop $(docker container ps --filter label=team=" + branch.lower() + " --format '{{.ID}}')"
            mail_list = ""
            if (branch == "Devops"):
                    mail_list = ["eilon696@gmail.com",author]
            elif (branch == "Billing"):
                    mail_list = ["oronboy100@gmail.com",author]
            elif (branch == "Weight"):
                    mail_list = ["ron981@gmail.com",author]
            else:
                    mail_list = ["eilon696@gmail.com",author]
            sendmail(mail_list,"test failed","your test result: " +str(test_result) + "check your code again")

            if test_result == 0:
                os.system(str_stop)
                if pureFolder == "staging":
                    os.system("docker-compose --env-file ./config/.env.stg up --detach --build")
                else:
                    os.system("docker-compose --env-file ./config/.env.dep up --detach --build")
                sendmail(mail_list,"test success","your test result: " + str(test_result) + "the server will be update soon")
            else:
                os.system(str_stop)
                sendmail(mail_list,"test failed","your test result: " + str(test_result) + "check your code again")


        os.chdir("../..")       
        return my_commit


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/mailer')
def maiLogger():
    with app.app_context():
        mail_list=["oronboy100@gmail.com","eilon696@gmail.com","ron981@gmail.com" ,"erezmizra@gmail.com", "tovikolitz@gmail.com" , "hodaya060@gmail.com","kfir2251@gmail.com","c0527606305@gmail.com","Pinoubg@live.fr","efrat7024@gmail.com","htemstet@gmail.com"]
        title=sendmail(mail_list,'LogFile Just For you Green Team!',"Hello from Green Devops AutoMailer! \n Weve got new log for you (Attached)","logfile.log")
        with open("logfile.log","w") as com_log:
            com_log.write("")
    return title

def sendmail(mail_list,title,body,attachment=1):
    try:
        for m in range(len(mail_list)):
            msg = Message(title, sender = 'autmailer101@gmail.com', recipients = [mail_list[m]])
            msg.body = body
            if attachment != 1:
                with app.open_resource(attachment) as fp:
                    msg.attach(attachment, "text/plain", fp.read()) 
            mail.send(msg)
        return title
    except:
        print("Something Wrong")
        


if __name__ == '__main__':

    scheduler.add_job(id ='Scheduled task', func = maiLogger , trigger = 'interval', minutes = 720)
    scheduler.start()
    app.run(host='0.0.0.0')