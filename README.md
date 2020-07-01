This project is the source code for App Engine project.

# App

The app is available at [https://yyyaaannn.ew.r.appspot.com](https://yyyaaannn.ew.r.appspot.com)

GET parameters are `q_ddate`, `q_rdate` and `q_route` e.g. 

https://yyyaaannn.ew.r.appspot.com/?q_route=Helsinki%20Canberra%7CSydney%20Oslo&q_ddate=2020-12-19&q_rdate=2020-12-29

# Tips for using GCP Cloud Shell

Pull from Git if applicable (clone or pull)

```
git clone https://github.com/yyyaaan/gcp_app
git pull origin master
```

Creating SSH keys for GIT [here](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

Create virtual environment on GCP Shell

```
virtualenv --python python3 ~/envs/hello_world
source ~/envs/hello_world/bin/activate
pip install -r requirements.txt
```

Deploy

```
gcloud app deploy
```

Git Commit

```
git add .
git commit -m ""
git push -u origin master
```
