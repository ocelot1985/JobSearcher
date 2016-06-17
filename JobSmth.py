#coding=utf-8

# Version 1.1  reconstruct of class format

# Automatically download job information everyday.
# Author: ZhangKai
# Email:  ocelot1985@gmail.com

import urllib2
import sys
import os
import re
import base64
import smtplib  
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
from email.mime.multipart import MIMEMultipart

from bs4 import BeautifulSoup

# set python file encoding format, otherwise
# there will be error in buildMailContent function
reload(sys)
sys.setdefaultencoding('utf-8')


# utility function
# sending the jobInfo to your mailbox in plain text format
def buildMailContent(mainUrl, title):
	content = ""
	for key in jobInfo:
		url = mainUrl + key
		content = content + str(url) + '\t\t' + str(jobInfo[key]) + '\n'

	return content

# utility function
# sending jobInfo mail in html format
#def buildHtmlContent(mainUrl, title, jobInfo):
#	#jobInfo = jobSum[site]
#	if not jobInfo:
#		content = "<h1> Sorry! No New Job Info</h1>" + "<br/>" + "<img src=\"http://f.hiphotos.bdimg.com/album/w%3D2048/sign=c5ddd4a7ac4bd11304cdb0326e97a50f/2f738bd4b31c8701acc38232267f9e2f0608ffe8.jpg\">"
#		return content
#	content = "<h1>" + title + "</h1>"
#	for key in jobInfo:
#		url = "<a href=\"" + mainUrl + str(key) + "\">" + str(jobInfo[key]) + "</a> <br/>"
#		content = content + url
#	return content


# utility function
# sending jobInfo mail in html file as attachment
# @return: a file handler
def buildHtmlContent(mainUrl, title, jobInfo):
    fd = open("/data0/work/job.html", "w+")
	#jobInfo = jobSum[site]
    if not jobInfo:
        content = "<h1> Sorry! No New Job Info</h1>" + "<br/>" 
        #return content
        fd.write(content)
        fd.close()
        return
        #return fd
    content = "<html><head><meta charset=\"utf-8\"></head><body><h1>" + title + "</h1>"
    for key in jobInfo:
        url = "<a href=\"" + mainUrl + str(key) + "\">" + str(jobInfo[key]) + "</a> <br/>"
        content = content + url
    #return content
    content = content + "</body></html>"
    fd.write(content)
    fd.close()
    return
    #return fd

def send_mail(to_list,sub,content):
	#mailto_list=[ocelot1985@126.com]
	mail_host="smtp.126.com"
	mail_user="ocelot1985"
	mail_pass="1985zk1110yz"
	mail_postfix="126.com"
	me="<"+mail_user+"@"+mail_postfix+">"
	#msg = MIMEText(content,_subtype='plain',_charset='gb2312')
	msg = MIMEText(content,_subtype='html',_charset='utf-8')
	msg['Subject'] = sub
	msg['From'] = me
	msg['To'] = ";".join(to_list)
	#print msg
	try:
		server = smtplib.SMTP()
		server.connect(mail_host)
		server.login(mail_user,mail_pass)
		ret = server.sendmail(me, to_list, msg.as_string())
		#print ret
		server.close()
		return True
	except Exception, e:
		print str(e)
		return False


def new_send_mail(to_list,sub,mail):
    #mailto_list=[ocelot1985@126.com]
    mail_host="smtp.126.com"
    mail_user="ocelot1985"
    mail_pass="1985zk1110yz"
    mail_postfix="126.com"
    me="<"+mail_user+"@"+mail_postfix+">"
    #msg = MIMEText(content,_subtype='plain',_charset='gb2312')
    content = open(mail, "r")
    print type(content.read())
    msg = MIMEMultipart()
    #att = MIMEText(content.read(),_subtype='html',_charset='utf-8')
    att = MIMEBase('application', 'octet-stream')
    att.set_payload(open(mail,'r').read())
    Encoders.encode_base64(att)
    att.add_header('Content-Disposition', 'attachment; filename="job.html"')
    #att = MIMEBase(base64.encodestring(content.read()))
    #att["Content-Type"] = 'application/octet-stream'
    #att["Content-Disposition"] = 'attachment; filename="job.html"'
    msg.attach(att)
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    #print msg
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        ret = server.sendmail(me, to_list, msg.as_string())
        #print ret
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

# process job information class
class JobFinder(object):
	"""	This is a class processing job information on BYR board."""
	def __init__(self, url):
		self.url = url
		# page number
		self.num = 1
		# finding content title and link url
		self.tdAttrContent = {'class' : ['title_9']}
		# finding post date
		# there is 2 title_10 class in page
		self.tdAttrDate = {'class' : ['title_10']}
		# post date reg
		# It is used for filtering today's post;
		# Because today's post date is 00:00:01 format;
		# Old one's format is 2014-08-15 format;
		self.pattern = re.compile(r'\d\d:\d\d:\d\d')
		# filter for searching test or chinese format test
		self.filter1 = re.compile(u'\u6d4b\u8bd5')
		self.filter2 = re.compile(r'[Tt]est')
		self.filter3 = re.compile(r'QA')
		# end flag
		self.flag = 0
		# Job summary info dict
		# key is site name, such as smth, byr, value is job info dict
		self.jobSum = {}
		# list storing site name
		self.site = ['smth', 'byr']
		# dict for storing link and title of job information
		self.jobInfo = {}
		# dict for storing filter results
		self.filtered = {}

	def getJobInfo(self):
		#jobInfo = {}
		#print jobUrl
		#jobPage = urllib2.urlopen(self.url + str(self.num)).read()
		#jobPage = urllib2.urlopen('http://www.baidu.com/')
		jobPage = os.popen("/data0/work/phantomjs-1.9.8-linux-x86_64/bin/phantomjs /data0/work/phantomjs-1.9.8-linux-x86_64/smth.js " + str(self.num))
                content = jobPage.read()
                #print content
                #print type(content)
		# inside BeautifulSoup, process encoding is unicode
		parser = BeautifulSoup(markup=content,features='lxml',from_encoding='utf-8')
		#parser = BeautifulSoup(markup=content,features='lxml',from_encoding='gb18030')
		#parser = BeautifulSoup(markup=content,from_encoding='gb18030')
                #print parser.prettify()
                #print dir(parser)
                #print parser.contents
		body = parser.find('tbody')
		#print body
                if body == None:
                    sys.exit();
		
		for tr in body.children:
			# bypass top and ad posts in the page
			# because this tr elements have class property
			if tr.attrs:
				continue
			#print tr.find(name='td', attrs=tdAttrContent).encode('gb18030')
			# if the post's date is not today, dont save it
			# because class title_10 exists twice, so if there's change in the page,
			# I need to use find_all to correctly get the post date
			post = tr.find(name='td', attrs=self.tdAttrDate).contents[0]
			match = self.pattern.search(post)
			if not match:
				#print 'in not match'
				self.flag = 1
				continue
			else:
				#print 'in match'
				self.flag = 0
			# find job info td element
			tdJob = tr.find(name='td', attrs=self.tdAttrContent)
			href = tdJob.contents[0].attrs
                        #print href['href']
			title = tdJob.contents[0].contents[0]
			#print title
			# save the link and title info in the dict
			# unicode() is used for solving chinese character problem in unicode
			self.jobInfo[href['href']] = unicode(title)
			#jobInfo[href['href']] = title
			#print jobInfo[href['href']]
		
		#jobSum[site] = jobInfo
		#print str(jobInfo)
		#printDict(jobInfo)

	def search(self):
		for key in self.jobInfo:
			match1 = self.filter1.search(self.jobInfo[key])
			match2 = self.filter2.search(self.jobInfo[key])
			match3 = self.filter3.search(self.jobInfo[key])
			if match1 or match2 or match3:
				print "match found"
				self.filtered[key] = self.jobInfo[key]

	def perDayJob(self):
		while self.flag != 1:
			#print flag
			self.getJobInfo()
			self.num = self.num + 1
			#print num
		# reset num for next site, such as BYR is after newsmth
		# and reset the flag
		#num = 1
		#flag = 0
		#jobSum[siteName] = jobInfo
		self.search()
		return self.filtered
		#return self.jobInfo
	
	


############
# data area
############

# base job info url.
# p=1(2/3/4...), the number is page no.
jobUrlSmth = 'http://www.newsmth.net/nForum/board/Career_Upgrade?p='
mainUrlSmth = 'http://www.newsmth.net'
titleSmth = 'JobInfo@newsmth'

jobUrlByr = 'http://bbs.byr.cn/board/JobInfo?p='
mainUrlByr = 'http://bbs.byr.cn'
titleByr = 'JobInfo@BYR'

######################
# main interface
######################
if __name__ == "__main__":
    job = JobFinder(jobUrlSmth)
    info = job.perDayJob()
    #print info
    #perDayJob(jobUrlByr, site[1])
    #mail = buildMailContent()
    #mailSmth = buildHtmlContent(mainUrlSmth, titleSmth, {})
    buildHtmlContent(mainUrlSmth, titleSmth, info)
    #mailByr = buildHtmlContent(mainUrlByr, titleByr, site[1])
    #print mail.encode('gb18030')
    #mailto_list=['917984410@qq.com','ocelot1985@163.com']
    #mailto_list=['917984410@qq.com','ocelot1985@126.com']
    mailto_list=['917984410@qq.com','370656326@qq.com']
    #mailto_list=['370656326@qq.com']
    #print mail
    ret = new_send_mail(mailto_list,"Smth Jobber Everyday", "/data0/work/job.html")
    #mailSmth.close()
    print ret
