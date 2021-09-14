import os
from flask import Flask, request ,json
import datetime
from flask import Response
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

intervalHours = 720
os.chdir("/gan-shmuel/")
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

        # TODO: docker-compose up TO PROD!
       
        my_commit = request.json
        jsonDump = json.dumps(my_commit)
        jsonLoad = json.loads(jsonDump)

        branch_ref = jsonLoad["ref"] #refs/heads/Billing

        directory_ref = jsonLoad["commits"][-1]
        com_msg = directory_ref["message"]
        author = directory_ref["author"]['email']
        branch = branch_ref.split("/")[2]

        with open("print.txt", "a+") as f:
            f.write(str(author) + "\n")
            f.write(str(com_msg) + "\n")
            f.write(str(branch) + "\n")

        os.system("cat print.txt")

        # [12/09/2021 10:41:38] made by .com on branch main 28282828
        with open("logfile.log", "a") as com_log:
            date = datetime.datetime.now()
            dt_string = date.strftime("%d/%m/%Y %H:%M:%S")
            com_log.write("[{0}] made by {1} on branch {2} with commit message: {3}\n".format(dt_string, author, branch, com_msg))

       
        #maybe can be renove because after one time we have all the branch
        #os.system("git checkout origin/" + branch)
        #
        os.system("git checkout " + branch)
        os.system("git pull")

        if branch != "Devops":
            #volume_name= "gan-shmuel_" + branch.lower() + "_data"
            #volume_name= "gan-shmuel_data"
            #os.system("docker volume rm -f " + volume_name)

            #add env to the volume
            os.system("echo INIT VOLUME")
            os.system("export VOLUME=/var/www/html/gan-shmuel/"+ branch)
            os.system("echo RUNNING DOCKER-COMPOSE")
            os.chdir(branch.lower()) 
            os.system("ls -alF")
            os.system("docker-compose --env-file ./config/.env.test up --detach --build")
            #
            os.system('docker exec -i $(docker container ps --filter label=container=app --filter label=team=' + branch.lower() + ' --format "{{.ID}}") sh')
            os.system("ls -alF")
            os.system('python3 ./app/test.py')
            test_result = os.system('echo $?')
            str_stop = "docker stop $(docker container ps --filter label=team=" + branch.lower() + " --format '{{.ID}}')"
            mail_list = ""

            if (branch == "Devops"):
                    mail_list = ["eilon696@gmail.com", author]
            elif (branch == "Billing"):
                    mail_list = ["oronboy100@gmail.com", author]
            elif (branch == "Weight"):
                    mail_list = ["ron981@gmail.com", author]
            else:
                    mail_list = ["eilon696@gmail.com", author]

            if test_result == 0: # OK
                os.system(str_stop)
                #os.system("git checkout staging")
                #os.system("git merge " + branch)
                os.system("export VOLUME=/var/www/html/gan-shmuel/"+ branch)
                os.system("docker-compose --env-file ./config/.env.stg up --detach --build")
                sendmail(mail_list, "Test on branch" + branch + " was successful!", "Test result: " + str(test_result) + " (0 is OK)\nThe server will be update soon")
            else:
                os.system(str_stop)
                sendmail(mail_list,"Test on branch" + branch + " failed!", "Test result: " + str(test_result) + "\ncheck your code again")
        os.chdir("../..")       
        return my_commit


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
# app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
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
                    "kfir2251@gmail.com", "c0527606305@gmail.com", "Pinoubg@live.fr",
                    "efrat7024@gmail.com", "htemstet@gmail.com"]

        title = sendmail(mail_list, 'Commiter report!', "Hello from Green Devops AutoMailer! \nAttaching the commit log of the last " + str(intervalHours) + " hours", "logfile.log")
        with open("logfile.log", "w") as com_log:
            com_log.write("")
    return title

def sendmail(mail_list, title, body, attachment=1):
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