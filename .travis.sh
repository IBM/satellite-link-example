#!/bin/bash
docker run -i --volume $PWD:/app --workdir /app registry.access.redhat.com/ubi8/python-39 sh << EOF
pip install -r requirements.txt
EOF
