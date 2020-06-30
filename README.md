This project is the source code for App Engine project.

# App

The app is available at [https://yyyaaannn.ew.r.appspot.com](https://yyyaaannn.ew.r.appspot.com)

GET parameters are `q_ddate`, `q_rdate` and `q_route`

# Tips for using GCP Cloud Shell

Pull from Git if any

```
git clone https://github.com/yyyaaan/gcp_app
```

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