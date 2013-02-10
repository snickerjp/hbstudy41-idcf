# -*- coding: utf-8 -*-

from fabric.api import *

# uname -s をただ実行
def host_type():
    run('uname -s')

from fabric.contrib.files import *

# epelのrepoをsudoでセットアップ
def setup_repo_epel():
    sudo("""
        yum -y localinstall \
http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    """)

# setup_epel_repoの実行と、redisの設定、起動
def setup_redis():
    setup_repo_epel()
    sudo("""
        yum -y install redis
    """)
    comment("/etc/redis.conf",r"bind 127.0.0.1")　# コメントアウトする
    sudo("""
        chkconfig redis on
        service redis restart
    """)

# idcf cloud api tool
def install_idcf_api():
    run("""
       yum -y localinstall \
http://repo.cloud.idc.jp/Linux/CentOS/6/idc/x86_64/idcf-release-8-0.0.idcf.el6.noarch.rpm
       yum -y install idcf.compute -y
       idcf-compute-api -v
    """)

def install_idcf_api_sudo():
    sudo("""
       yum -y localinstall \
http://repo.cloud.idc.jp/Linux/CentOS/6/idc/x86_64/idcf-release-8-0.0.idcf.el6.noarch.rpm
       yum -y install idcf.compute -y
       idcf-compute-api -v
    """)
# 
import json
import os,sys,time
SCALE_GROUP = "sclgrp"

def setup_idcf_vm(displayname="scale"):
    resp = local("""
    idcf-compute-api deployVirtualMachine \
                       --keypair {keypair} \
                       --displayname {displayname} \
                       --group {group} \
                       --templateid {templateid} \
                       --serviceofferingid {serviceofferingid} \
                       --zoneid {zoneid}
    """.format(keypair="「IDCFで登録したキーペア名」", #your ssh-key name
               displayname=displayname,
               group=SCALE_GROUP,
               templateid="2008", #(2008) [LATEST] CentOS 6.3 64-bit
               serviceofferingid="22", #(22) S2
               zoneid="1"),capture=True)
    print resp

    retval = json.loads(resp, 'UTF-8')
    ret = retval["deployvirtualmachineresponse"]
    vm_id = ret["id"]
    jobid = ret["jobid"]
    wait_job(jobid)
    print "__vmid__,%d" %vm_id

def wait_job(jobid):
    while True:
        resp = local("""
                    idcf-compute-api queryAsyncJobResult --jobid {jobid}
        """.format(jobid=jobid),capture=True)

        retval = json.loads(resp, 'UTF-8')
        ret = retval["queryasyncjobresultresponse"]

        if ret["jobstatus"] == 1:
           print resp
           break
        else:
           time.sleep(30)

def setup_hosts(ip=None,host_name=None):
    print ip
    print host_name
    if ip and host_name:
        append("/etc/hosts",
            ["{0} {1}".format(ip,host_name)],
            use_sudo=True)

# instance setup
SUDOERS = "devops"

def setup_sudoers(user=SUDOERS):
    run("""
    mkdir -p -m 700 /etc/skel/.ssh
    useradd {user}
    usermod -a -G wheel {user}
    cp /root/.ssh/authorized_keys /home/{user}/.ssh
    chown -R {user}:{user} /home/{user}
    chmod 600 /home/{user}/.ssh/authorized_keys
    """.format(user=user))
    uncomment("/etc/pam.d/su",r"auth\s+sufficient\s+pam_wheel.so\s+trust use_uid")
    uncomment("/etc/sudoers",r"%wheel\sALL=\(ALL\)\s+NOPASSWD:\sALL")

def sshd_config(user=SUDOERS):
    comment("/etc/ssh/sshd_config",r"^PermitRootLogin yes")
    uncomment("/etc/ssh/sshd_config",r"PermitEmptyPasswords no")
    append("/etc/ssh/sshd_config",
        ["PermitRootLogin no",
        "AllowUsers {0}".format(user)])
    #run("service sshd restart")
    run("service sshd reload") # sshd restart は怖いので、reload

def setup_redis_cli():
    setup_repo_epel()
    sudo("""
        yum -y install redis
    """)

from fabric.operations import *

def setup_cgi():
    sudo("""
    yum -y install httpd
    chkconfig httpd on
    service httpd start
    """)
    #put("~/hello_py.cgi","/var/www/cgi-bin/hello_py.cgi",use_sudo=True)
    put("hello_py.cgi","/var/www/cgi-bin/hello_py.cgi",use_sudo=True)
    sudo("chmod 755 /var/www/cgi-bin/hello_py.cgi")
    run("curl -s http://localhost/cgi-bin/hello_py.cgi | sed -e 's/<[^>]*>//g'")

def hostname():
    return run("hostname")

def setup_monit():
    setup_repo_epel()
    sudo("""
        yum -y install monit
    """)
    upload_template("loadavg.rc","/etc/monit.d",use_sudo=True,backup=False,
        context=dict(redis_server="redis-server",
        host_name=hostname(),
        scale_group=SCALE_GROUP))
    sudo("""
        chkconfig monit on
        service monit restart
    """)
def copy_idcfrc():
    put(".idcfrc","~/.idcfrc")

def count_idcf_vms():
    with hide('running', 'stdout', 'stderr'):
        resp = local("""
            idcf-compute-api listVirtualMachines --state Running
        """,capture=True)
    retval = json.loads(resp,'UTF-8')
    ret = retval["listvirtualmachinesresponse"]
    count = ret["count"]
    print count

def setup_stress():
    sudo("yum -y install stress")

def do_stress():
    run("stress --cpu 8 --timeout 10m")

def add_balancing_server(vmid):
    resp = local("""
        idcf-compute-api assignToLoadBalancerRule\
            --id {id} \
            --virtualmachineids {virtualmachineids}
    """.format(id="「ロードバランサID」", #your ID of the load balancer rule
        virtualmachineids=vmid),capture=True)
    print resp
