#!/usr/bin/python
# -*- coding: utf-8 -*-
html = '''
<HTML>
<HEAD>
<TITLE>test</TITLE>
</HEAD>
<BODY>
<HR>
<DIV ALIGN="center">
<H1>%s</H1>
<HR>
</DIV>
</BODY>
</HTML>
'''
import socket
name = socket.gethostname()
print html % name
