import os
from flask import Flask, request, json
import datetime
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

USER = "ec2-user" #os.environ.get('USER')

BILLING_PATH =    "/home/" + str(USER) + "/gan-shmuel/billing"
DB_BILLING_PATH = "/home/" + str(USER) + "/gan-shmuel/billing/db"

WEIGHT_PATH =    "/home/" + str(USER) + "/gan-shmuel/weight"
DB_WEIGHT_PATH = "/home/" + str(USER) + "/gan-shmuel/weight/db"

intervalHours = 720

# monitor JSON -> /monitor
# [Billing:XXXX, Weight:XXXX]
build_set = {
    "Testing": ["", ""],
    "Staging": ["", ""],
    "Production": ["", ""]
}

with open("logfile.log","w") as com_log:
    com_log.write("")

@app.route('/', methods=['GET'])
def main():
    return "welcome to CI!"

@app.route('/health',methods=["GET"])
def health():
    return "CI up!"

@app.route('/monitor',methods=["GET"])
def health():
    print(json.dumps(build_set, indent=4, sort_keys=True))

@app.route('/gitcomm' , methods=['POST'])
def git_api_comm():
    if request.headers['Content-Type'] == 'application/json':

        os.chdir("/gan-shmuel/")
        # TODO: docker-compose up TO PROD!
        os.system("echo [0]: loading commit json")
        my_commit = request.json
        jsonDump = json.dumps(my_commit)
        jsonLoad = json.loads(jsonDump)

        branch_ref = jsonLoad["ref"]
        directory_ref = jsonLoad["commits"][-1]
        com_msg = directory_ref["message"]
        author = directory_ref["author"]['email']
        branch = branch_ref.split("/")[2]

        os.system("echo [1]: printing json results")
        with open("print.txt", "a+") as f:
            f.write(str(author) + "\n")
            f.write(str(com_msg) + "\n")
            f.write(str(branch) + "\n")

        os.system("cat print.txt")

        with open("logfile.log", "a") as com_log:
            date = datetime.datetime.now()
            dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
            com_log.write("[{0}] made by {1} on branch {2} with commit message: {3}\n".format(dt_string, author, branch, com_msg))

        os.system("echo [2]: checkouting to commits on relevent branch")
        os.system("git checkout " + branch)
        os.system("git pull") # -q to quiet output

        os.system("echo $PWD")
        os.system("ls -alF")

        mail_list = ""
        if (branch == "Devops"):
            mail_list = ["eilon696@gmail.com", author]
        elif (branch == "Billing"):
            mail_list = ["oronboy100@gmail.com", author]
        elif (branch == "Weight"):
            mail_list = ["ron981@gmail.com", author]
        else:
            mail_list = ["eilon696@gmail.com", author]

        if branch != "Devops":
            os.system("echo [3]: switching to branch dir")
            os.chdir(branch.lower()) 
            os.system("echo $PWD")
            os.system("ls -alF")           

            os.system("echo [4]: settings port and volume paths")
            if branch == "Billing":
                os.environ["PORT"] = "8086"
                os.environ["VOLUME"] = DB_BILLING_PATH
                os.environ["TEAM_PATH"] = BILLING_PATH
                build_set['Testing'][0] = "Billing:8086"
            elif branch == "Weight":
                os.environ["PORT"] = "8085"
                os.environ["VOLUME"] = DB_WEIGHT_PATH
                os.environ["TEAM_PATH"] = WEIGHT_PATH
                build_set['Testing'][1] = "Weight:8085"

            os.system("echo " + os.environ["PORT"])
            os.system("echo " + os.environ["TEAM_PATH"])
            os.system("echo " + os.environ["VOLUME"])        

            os.system("echo [5]: docker-compose up for test")
            os.system("docker-compose up --detach --build")
            # os.system("echo RUNNING DOCKER-COMPOSE")
            # os.chdir(branch.lower()) 
            # os.system("ls -alF")
            # os.system("docker-compose --env-file ./config/.env.test up --detach --build"
            os.system("echo [5.5]: exec to test container and loading test")
            os.system('docker exec -i $(docker container ps --filter label=container=app --filter label=team=' + branch.lower() + ' --format "{{.ID}}") sh')
            os.system("echo $PWD")
            os.system("ls -alF")
            os.system('python3 app/test.py')
            test_result = os.system('echo $?')

            os.system("echo [6]: stopping tests containers")

            if test_result == 0: # OK
                os.system("echo [7]: test was successful! stopping test containers & settings port & volume paths")
                os.system("docker stop $(docker container ps --filter label=team=" + branch.lower() + " --format '{{.ID}}')")
                if branch == "Billing":
                    os.environ["PORT"] = "8082"
                    os.environ["VOLUME"] = DB_BILLING_PATH
                    os.environ["TEAM_PATH"] = BILLING_PATH
                    build_set['Testing'][0] = ""
                    build_set['Staging'][0] = "Billing:8082"
                elif branch == "Weight":
                    os.environ["PORT"] = "8084"
                    os.environ["VOLUME"] = DB_WEIGHT_PATH
                    os.environ["TEAM_PATH"] = WEIGHT_PATH
                    build_set['Testing'][1] = ""
                    build_set['Staging'][1] = "Weight:8084"

                os.system("echo " + os.environ["PORT"])
                os.system("echo " + os.environ["TEAM_PATH"])
                os.system("echo " + os.environ["VOLUME"])
                
                os.system("echo [8]: docker-compose for staging [READY FOR STAGING]")
                os.system("docker-compose up --detach --build")

                # TODO: merge with staging
                ''' os.system("git checkout staging")
                os.system("git merge " + branch)
                os.system("export VOLUME=/var/www/html/gan-shmuel/"+ branch)

                if branch == "Billing":
                    os.environ["PORT"] = "8082"
                    os.environ["VOLUME"] = DB_BILLING_PATH
                    os.environ["TEAM_PATH"] = BILLING_PATH
                    build_set['Staging'][0] = ""
                    build_set['Production'][0] = "Billing:8081"
                elif branch == "Weight":
                    os.environ["PORT"] = "8084"
                    os.environ["VOLUME"] = DB_WEIGHT_PATH
                    os.environ["TEAM_PATH"] = WEIGHT_PATH
                    build_set['Staging'][1] = ""
                    build_set['Production'][1] = "Weight:8083"

                #os.system("export VOLUME=/"+ branch)
                #WHEN MAIN WILL CLONE CORRECTLY IT WILL WORK I HOPE.

                os.system("docker-compose --env-file ./config/.env.stg up --detach --build")'''
                sendmail(mail_list, "Test on branch" + branch + " was successful!", "Test result: " + str(test_result) + " (0 is OK)\nThe server will be update soon")
            else:
                os.system("echo [7]: test was unsuccessful! stopping test containers!!")
                os.system("docker stop $(docker container ps --filter label=team=" + branch.lower() + " --format '{{.ID}}')")
                sendmail(mail_list,"Test on branch" + branch + " failed!", "Test result: " + str(test_result) + "\ncheck your code again")
        else:
            os.system("echo [3]: Restarting CI docker-compose")
            os.system("docker-compose -f devops/docker-compose.yml up --build")

        os.chdir("..")       
        return my_commit

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 46
app.config['MAIL_USERNAME'] ='autmailer101@gmail.com'
app.config['MAIL_PASSWORD'] ='12341234!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/mailer')
def mailLogger():
    with app.app_context():
        mail_list = ["oronboy100@gmail.com", "eilon696@gmail.com", "ron981@gmail.com",
                    "erezmizra@gmail.com", "tovikolitz@gmail.com" , "hodaya060@gmail.com",
                    "kfir2251@gmail.com", "Pinoubg@live.fr",
                    "efrat7024@gmail.com", "htemstet@gmail.com"]

        title = sendmail(mail_list, 'Commiter report!', "Hello from Green Devops AutoMailer! \nAttaching the commit log of the last " + str(intervalHours) + " hours", "logfile.log")
        with open("logfile.log", "w") as com_log:
            com_log.write("")
    return title

def sendmail(mail_list, title, body, attachment = 1):
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
    scheduler.add_job(id ='Scheduled task', func = mailLogger , trigger = 'interval', minutes = intervalHours)
    scheduler.start()
    app.run(host='0.0.0.0')