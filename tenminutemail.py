#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from threading import Thread
from time import time, sleep
from json import loads
from bs4 import BeautifulSoup
from requests import Session, get, post
"""tenminutemail.py: 10 dakikalık e-mail adresi oluşturucu."""

__author__ = "Hichigo THT"
__license__ = "GPL"
__version__ = "1.0.2"
__status__ = "Production"
__date__ = "10.04.2019 Black Hole"


MAIL_URL = "https://www.minuteinbox.com/"
MAIL_REFLESH_URL = "https://www.minuteinbox.com/index/refresh"


class MailBox:
    def __init__(self, proxy=None, reflesh_interval = 10):
        self.ses = Session()
        self.email = None
        self.mails = []
        self.reflesh_interval = reflesh_interval
        self.checkmailthread = None
        self.__lastcheckdate = int(round(time()))
        self.__mailthreadstatus = False
        self.date = int(round(time()))
        self.proxy = proxy
        self.ses.proxies = proxy


    def connect(self):
        try:
            res = self.ses.get(MAIL_URL)
            if (res.status_code != 200):
                return {
                    "status": False,
                    "tr_message": "Mail sunucusuna bağlanılamadı.",
                    "eng_message": "Couldn't connect to mail server.",
                    "response": res,
                    "exception": None
                }

            self.ses.cookies.update(res.cookies)
            self.ses.headers.update({
                "Host": "www.minuteinbox.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                "Accept": "application/json; charset=utf8",
                "Content-Type": "application/json; charset=utf8",
                "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": MAIL_URL,
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            })

            soup = BeautifulSoup(res.text, "html.parser")
            self.email = soup.find("span", id="email").text

            if (self.email == None):
                return {
                    "status": False,
                    "tr_message": "Mail adresi alınamadı.",
                    "eng_message": "Couldn't get the mail address.",
                    "response": res,
                    "exception": None
                }

            return {
                "status": True,
                "tr_message": "Mail adresi alındı.",
                "eng_message": "Mail address successfully found.",
                "response": res,
                "exception": None
            }

        except Exception as e:
            return {
                "status": False,
                "tr_message": "Bilinmeyen bir hata oluştu. (Exception)",
                "eng_message": "A unknown error occured. (Exception)",
                "response": None,
                "exception": e
            }

    def start_check_thread(self):
        self.__mailthreadstatus = True
        self.checkmailthread = Thread(target=self.checkthread)
        self.checkmailthread.start()

    def checkthread(self):
        while (self.__mailthreadstatus is True and (int(round(time())) - self.date <= 600)):
            if (int(round(time())) - self.__lastcheckdate >= self.reflesh_interval):
                self.check()
                sleep(self.reflesh_interval)

    def stop_check_thread(self):
        self.__mailthreadstatus = False

    def close(self):
        self.stop_check_thread()
        self.ses.close()

    def check(self):
        try:
            if (int(round(time())) - self.date >= 600):
                return {
                    "status": False,
                    "tr_message": "Mail zaman aşımı.",
                    "eng_message": "Mail timeout achived.",
                    "response": None,
                    "exception": None
                }

            res = self.ses.get(MAIL_REFLESH_URL)
            if (res.status_code != 200):
                return {
                    "status": False,
                    "tr_message": "Mail sunucusuna bağlanılamadı.",
                    "eng_message": "Couldn't connect to mail server.",
                    "response": res,
                    "exception": None
                }

            res.encoding = "utf-8-sig"
            data = res.json()

            for mail in data:
                maildata = {
                    "header": mail["predmet"],
                    "sender": mail["od"],
                    "id": mail["id"],
                    "date": mail["kdy"],
                    "content": mail["akce"],
                    "status": mail["precteno"]
                }

                isExisting = False
                for oldmail in self.mails:
                    if (oldmail["id"] == mail["id"]):
                        isExisting = True
                        break

                if (isExisting == False):
                    self.mails.append(maildata)

            self.__lastcheckdate = int(round(time()))
            return {
                "status": True,
                "tr_message": "Mail listesi yenilendi.",
                "eng_message": "Mail list got refleshed.",
                "response": None,
                "exception": None
            }

        except Exception as e:
            return {
                "status": False,
                "tr_message": "Bilinmeyen bir hata oluştu. (Exception)",
                "eng_message": "A unknown error occured. (Exception)",
                "response": None,
                "exception": e
            }
