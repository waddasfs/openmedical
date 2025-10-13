#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 21:05
# @Author  : yulong
# @File    : mongo_config.py

import os
from dotenv import load_dotenv

load_dotenv(".env")

mongo_config = {
    "ip": os.getenv("MONGODB_IP", "localhost"),
    "port": int(os.getenv("MONGODB_PORT", "27017")),
    "database": os.getenv("MONGODB_DATABASE", "medical"),
    "collection": os.getenv("MONGODB_COLLECTION", "users"),
    "username": os.getenv("MONGODB_USERNAME", ""),
    "password": os.getenv("MONGODB_PASSWORD", "")
}
