import os
from flask import Flask, request, json
import datetime
from flask_mail import Mail, Message
from flask import render_template
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

BILLING_PATH =    "/home/ec2-user/gan-shmuel/billing"
DB_BILLING_PATH = "/home/ec2-user/gan-shmuel/billing/db"

WEIGHT_PATH =    "/home/ec2-user/gan-shmuel/weight"
DB_WEIGHT_PATH = "/home/ec2-user/gan-shmuel/weight/db"

intervalHours = 720

#                                     test/stage/prod
BILLING_MONITOR_ARRAY = ["", "", ""] #["", "", "8081"]
WEIGHT_MONITOR_ARRAY = ["", "", ""]  #["8085", "", ""]
STATUS_MONITOR_ARRAY = ["", "", ""]

with open("logfile.log","w") as com_log:
    com_log.write("")

@app.route('/', methods=['GET'])
def main():
    return "welcome to CI!"

@app.route('/health',methods=["GET"])
def health():
    return "CI up!"

@app.route('/monitor',methods=["GET"])
def monitor():
    return render_template('monitor.html', billing = BILLING_MONITOR_ARRAY, weight = WEIGHT_MONITOR_ARRAY, status = STATUS_MONITOR_ARRAY)

@app.route('/gitcomm' , methods=['POST'])
def git_api_comm():
    global BILLING_MONITOR_ARRAY
    global WEIGHT_MONITOR_ARRAY
    global STATUS_MONITOR_ARRAY

    if request.headers['Content-Type'] == 'application/json':
        STATUS_MONITOR_ARRAY[2] = "loading"

        os.chdir("/gan-shmuel/")
        # TODO: docker-compose up TO PROD!
        os.system("echo [0]: loading commit json")
        my_commit = request.json
        jsonDump = json.dumps(my_commit)
        jsonLoad = json.loads(jsonDump)

        commit_json = jsonLoad.get("ref", "")
        pull_request_json = jsonLoad.get("action", "")

        if pull_request_json:
            if pull_request_json == "opened":
                os.system("echo [0.5]: a pull request just opened")
            elif pull_request_json == "closed":
                # LOAD TO PRODUCTION
                os.system("echo [0.5]: a pull request just resolved - lets upload something to production!")
                branch = jsonLoad["pull_request"]["head"]["ref"]

                os.system("echo [2]: checkouting to commits on main for production")
                os.system("git checkout -f main")
                os.system("git pull") # -q to quiet output

                os.system("echo [3]: switching to " + branch + " dir")
                os.chdir(branch.lower())
                os.system("echo $PWD")
                os.system("ls -alF")

                if branch == "Billing":
                    os.environ["PORT"] = "8081"
                    os.environ["VOLUME"] = DB_BILLING_PATH
                    os.environ["TEAM_PATH"] = BILLING_PATH
                    BILLING_MONITOR_ARRAY[2] = "8081"
                    STATUS_MONITOR_ARRAY[0] = "uploading to production"
                elif branch == "Weight":
                    os.environ["PORT"] = "8083"
                    os.environ["VOLUME"] = DB_WEIGHT_PATH
                    os.environ["TEAM_PATH"] = WEIGHT_PATH
                    WEIGHT_MONITOR_ARRAY[2] = "8083"
                    STATUS_MONITOR_ARRAY[1] = "uploading to production"

                os.system("echo " + os.environ["PORT"])
                os.system("echo " + os.environ["TEAM_PATH"])
                os.system("echo " + os.environ["VOLUME"])
                
                os.system("echo [4]: docker-compose for production [READY FOR PRODUCTION]")
                os.system("docker-compose up --detach --build")

                if branch == "Billing":
                    STATUS_MONITOR_ARRAY[0] = ""
                elif branch == "Weight":
                    STATUS_MONITOR_ARRAY[1] = ""

                os.chdir("..")

                mail_list = ""
                if (branch == "Devops"):
                    mail_list = ["eilon696@gmail.com"]
                elif (branch == "Billing"):
                    mail_list = ["oronboy100@gmail.com"]
                elif (branch == "Weight"):
                    mail_list = ["ron981@gmail.com"]
                else:
                    mail_list = ["eilon696@gmail.com"]
                sendmail(mail_list, branch + " was uploaded to production!", "Uploading server to production PORT..")
        elif commit_json:
            directory_ref = jsonLoad["commits"][-1]
            com_msg = directory_ref["message"]
            author = directory_ref["author"]['email']
            branch = commit_json.split("/")[2]

            os.system("echo [0.5]: loading a commit from " + branch)
            os.system("echo [1]: printing json results")

            with open("logfile.log", "a") as com_log:
                date = datetime.datetime.now()
                dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
                com_log.write("[{0}] made by {1} on branch {2} with commit message: {3}\n".format(dt_string, author, branch, com_msg))

            os.system("echo [2]: checkouting to commits on relevent branch")
            os.system("git checkout -f " + branch)
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

            if branch not in ("Devops", "staging", "main"): # OK is Billing/Weight
                os.system("echo [3]: switching to branch dir")
                os.chdir(branch.lower())
                os.system("echo $PWD")
                os.system("ls -alF")

                os.system("echo [4]: settings port and volume paths")
                if branch == "Billing":
                    os.environ["PORT"] = "8086"
                    os.environ["VOLUME"] = DB_BILLING_PATH
                    os.environ["TEAM_PATH"] = BILLING_PATH
                    BILLING_MONITOR_ARRAY[0] = "8086"
                    STATUS_MONITOR_ARRAY[0] = "testing"
                    
                elif branch == "Weight":
                    os.environ["PORT"] = "8085"
                    os.environ["VOLUME"] = DB_WEIGHT_PATH
                    os.environ["TEAM_PATH"] = WEIGHT_PATH
                    WEIGHT_MONITOR_ARRAY[0] = "8085"
                    STATUS_MONITOR_ARRAY[1] = "testing"

                os.system("echo " + os.environ["PORT"])
                os.system("echo " + os.environ["TEAM_PATH"])
                os.system("echo " + os.environ["VOLUME"])        

                os.system("echo [5]: docker-compose up for test")
                os.system("docker-compose up --detach --build")
                os.system("echo [5.5]: exec to test container and loading test")
                os.system('docker exec $(docker container ps --filter label=container=app --filter label=team=' + branch.lower() + ' --format "{{.Names}}") python3 /app/test.py')
                test_result = os.system('echo $?')

                os.system("echo [6]: stopping tests containers")

                if test_result == 0: # OK
                    os.system("echo [7]: test was successful! stopping test containers & settings port & volume paths")
                    os.system("docker stop $(docker container ps --filter label=team=" + branch.lower() + " --format '{{.ID}}')")

                    if branch == "Billing":
                        os.environ["PORT"] = "8082"
                        os.environ["VOLUME"] = DB_BILLING_PATH
                        os.environ["TEAM_PATH"] = BILLING_PATH
                        BILLING_MONITOR_ARRAY[0] = ""
                        BILLING_MONITOR_ARRAY[1] = "8082"
                        STATUS_MONITOR_ARRAY[0] = "exiting test"
                    elif branch == "Weight":
                        os.environ["PORT"] = "8084"
                        os.environ["VOLUME"] = DB_WEIGHT_PATH
                        os.environ["TEAM_PATH"] = WEIGHT_PATH
                        WEIGHT_MONITOR_ARRAY[0] = ""
                        WEIGHT_MONITOR_ARRAY[1] = "8084"
                        STATUS_MONITOR_ARRAY[1] = "exiting test"

                    os.system("echo " + os.environ["PORT"])
                    os.system("echo " + os.environ["TEAM_PATH"])
                    os.system("echo " + os.environ["VOLUME"])
                    
                    os.system("echo [8]: docker-compose for staging [READY FOR STAGING]")
                    os.system("docker-compose up --detach --build")

                    if branch == "Billing":
                        STATUS_MONITOR_ARRAY[0] = "merging to staging"
                    elif branch == "Weight":
                        STATUS_MONITOR_ARRAY[1] = "merging to staging"

                    os.chdir("..")

                    str_github = "Erez"
                    os.system("git config --global user.name '%s'"%str_github)
                    str_github = "erezmizra@gmail.com"
                    os.system("git config --global user.email '%s'"%str_github)

                    '''os.system("echo [9]: Updating DB from branches to Devops")
                    # Update Devops DB from branch
                    os.system("git checkout Devops")
                    os.system("git pull")
                    os.system("git checkout " + branch + " -- " + branch.lower() + "/db") # git checkout Billing -- Billing/db
                    commit_str = "Updated Devops DB file: " + branch.lower() + "/db"
                    os.system("git add .")
                    os.system("git commit -m '%s'"%commit_str)
                    os.system("git push")'''

                    os.system("echo [10]: Merging branch to staging")
                    os.system("git checkout -f staging")
                    os.system("git pull")
                    os.system("git checkout " + branch + " -- " + branch.lower())
                    merge_str = "Merging with " + branch.lower()
                    os.system("git add .")
                    os.system("git commit -m '%s'"%merge_str)
                    os.system("git push")

                    if branch == "Billing":
                        STATUS_MONITOR_ARRAY[0] = ""
                    elif branch == "Weight":
                        STATUS_MONITOR_ARRAY[1] = ""

                    sendmail(mail_list, "Test on branch" + branch + " was successful!", "Test result: " + str(test_result) + " (0 is OK)\nUploading server to staging PORT..")
                else:
                    os.system("echo [7]: test was unsuccessful! stopping test containers!!")
                    os.system("docker stop $(docker container ps --filter label=team=" + branch.lower() + " --format '{{.ID}}')")
                    sendmail(mail_list,"Test on branch" + branch + " failed!", "Test result: " + str(test_result) + "\ncheck your code again")
                    os.chdir("..")
            else:
                # A NEW CI WAS PULLED
                os.system("echo $PWD")
                os.system("ls -alF")

                os.system("echo [4]: Merging Devops to staging")
                # TODO: merge with staging
                os.system("git checkout -f staging")
                os.system("git pull")
                os.system("git checkout Devops -- devops") #  -> getting Devops dir to merge
                merge_str = "Merging with " + branch.lower()
                os.system("git commit -m '%s'"%merge_str)
                os.system("git push")

        STATUS_MONITOR_ARRAY[2] = ""
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
        mail_list = ["oronboy100@gmail.com", "eilon696@gmail.com", "ron981@gmail.com", "erezmizra@gmail.com",
                    "tovikolitz@gmail.com" , "hodaya060@gmail.com", "kfir2251@gmail.com", "Pinoubg@live.fr",
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
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    scheduler.add_job(id ='Scheduled task', func = mailLogger , trigger = 'interval', minutes = intervalHours)
    scheduler.start()
    app.run(host='0.0.0.0')