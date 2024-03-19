import smtplib
import email.utils
from email.mime.text import MIMEText

import pathlib
import imaplib, ssl
import smtplib, email.mime.text
import sys
import os.path
import email
import subprocess
import mailbox
import configparser
import urllib.parse

import rich
from rich.pretty import pprint as PP
from rich.console import Console
from rich.table import Table
CONSOLE = Console()

cfg: configparser.ConfigParser
cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.turbosmrc"))

import logging
import time
FORMAT = '%(asctime)s+00:00 %(levelname)10s: %(message)-80s    (%(filename)s,%(funcName)s:%(lineno)s)'
FORMAT = '%(asctime)s+00:00 %(levelname)10s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logging.Formatter.converter = time.gmtime


def debug_cfg(cfg, con):
    t = rich.table.Table(title="rc contents", row_styles=["dim", ""])
    t.add_column("section")
    t.add_column("key")
    t.add_column("value")

    for s in cfg.sections():
        t.add_row("", "", "")
        so = cfg.options(section=s)
        # s = section title
        # so = list of keys in section

        for k in so:
            v = cfg.get(section=s, option=k)
            t.add_row("%s" % s, k, v)

    con.print(t)




#debug_cfg(cfg, CONSOLE)
cfg_ = {}

def run_init(cfg:configparser.ConfigParser, con):
    global cfg_
    cfg_['home'] = os.path.expanduser(cfg.get("main", "home"))
    logging.info("(main-config): home=%s" % cfg_['home'])
    os.makedirs(cfg_['home'], exist_ok=True)
    # make dirs for each imap account:
    smtp_accounts = []
    for s in cfg.sections():
        if s.startswith("smtp_"):
            x = {
                'id' : s[5:]
            }
            for k in cfg.options(s):
                x[k] = cfg.get(s, k)
                if k == 'sink':
                    x[k] = os.path.expanduser(x[k])
                    os.makedirs(x['sink'], exist_ok=True)

                if k == 'passfile':
                    x[k] = os.path.expanduser(x[k])
                    if len(x[k]) > 0:
                        x['pass'] = open(x[k]).read().replace("\r", "").split("\n")[0]

            x['home'] = os.path.join(cfg_['home'], x['id'])
            os.makedirs(x['home'], exist_ok=True)
            
            x['mbox'] = os.path.join(cfg_['home'], x['id'], 'sent.mbox')
            if not os.path.isfile(x["mbox"]):
                pathlib.Path.touch(x["mbox"])
            
            smtp_accounts.append(x)
    cfg_['smtp_accounts'] = smtp_accounts
    logging.info("(main-config): Ready to go!")
    

def run_simple(con):
    logging.info("RUNNING")
    for sa in cfg_['smtp_accounts']:
        logging.info("SMTP ACCOUNT id=[ %s ]" % sa["id"])
        try:
            box = mailbox.mbox(sa["mbox"])

            for sm_file_cand in os.listdir(sa['sink']):
                if os.path.isfile(os.path.join(sa['sink'], sm_file_cand)) and sm_file_cand.endswith(".sm"):
                    logging.info("SINK DETECTION RETURNED (%s)" % sm_file_cand)
                else:
                    logging.warning(sm_file_cand)
            # msg=MIMEText("so much text\nyeah\n")
            # msg["From"] = sa['sender_address']
            # msg["Subject"] = "bla2"
            # msg["To"] = "robert.degen@mailbox.org"
            # msg["Date"] = email.utils.formatdate(localtime=True)

            # server = smtplib.SMTP_SSL("%s:%d" % (sa['server'], int(sa['sslport'])))
            # server.login(sa['login'], sa['pass'])
            # server.send_message(msg)
            # server.quit()
            # box.add(msg)


            box.unlock()
        except Exception as exc:
            logging.error(exc)
    logging.info("DONE")

#debug_cfg(cfg, CONSOLE)
#sys.exit(0)

run_init(cfg, CONSOLE)

run_simple(CONSOLE)

sys.exit(0)
