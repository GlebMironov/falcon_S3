# Simple falcon powered service for store files on AWS S3

* Setup OS dependencies (example for Ubuntu 14.04):
```bash
$: sudo apt-get install rabbitmq-server
```

* Setup Python dependencies:
```bash
$: cd falcon_S3
$: sudo pip3 install -r requirements.txt
```

* Init AWS engine (you must have 'Access Key ID', 'Secret Access Key' and 'Region' into your home directory)
```bash
$: cat ~/.aws/credentials
[default]
aws_access_key_id = <some_aws_access_key_id>
aws_secret_access_key = <some_aws_secret_access_key>
region = us-west-2

$: cd falcon_S3/app
$: python3 init_engine.py
```

* Run celery:
```bash
$: cd falcon_S3/app
$: celery -A tasks worker --loglevel=info
```

* Run application:
```bash
$: cd falcon_S3/app
$: gunicorn -b 0.0.0.0:5000 app:app
```

* Usage application:
```bash
$: http -f PUT localhost:5000/storage file@<some path to file>/test.bin
HTTP/1.1 201 Created
Connection: close
Date: Thu, 23 Mar 2017 15:10:06 GMT
Server: gunicorn/19.7.1
content-length: 48
content-type: application/json; charset=UTF-8

{
    "file_key": "ec993fe6151149390e0234090481195a"
}

$: http GET localhost:5000/storage file_key=ec993fe6151149390e0234090481195a
HTTP/1.1 200 OK
Connection: close
Date: Thu, 23 Mar 2017 15:11:16 GMT
Server: gunicorn/19.7.1
content-length: 169088
content-location: test.bin
content-type: application/octet-stream



+-----------------------------------------+
| NOTE: binary data not shown in terminal |
+-----------------------------------------+

```
