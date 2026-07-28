#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64

s = "Zmxhz19ub3RfaGvyzSEHIQ=="
decoded = base64.b64decode(s).decode('utf-8')
print(decoded)
