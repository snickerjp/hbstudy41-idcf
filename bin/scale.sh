#!/bin/bash
queue="scale:sclgrp:up"
lock_key="scale:sclgrp:lock"
incrd_key="scale:sclgrp:incrd"

path="`dirname $0`"
log_file="scale.log"
log() {
  echo [`date`] $1 >> ${path}/${log_file}
}

log "-------------------------"
queue_count=$(redis-cli llen $queue | awk '{print $1}')
log "queue_count: $queue_count"

if [ $queue_count -gt 0 ]; then
    vm_name=$(redis-cli lpop $queue | awk '{print $1}')
    log "queued by: $vm_name"

    locked=$(redis-cli get $lock_key | awk '{print $1}')
    incrd=$(redis-cli get $incrd_key | awk '{print $1}')
    if [ -z "$locked" ]; then
        locked=0
    fi
    if [ -z "$incrd" ]; then
        incrd=0
    fi
    log "locked: $locked"
    log "incrd: $incrd"
    vm_count=$(fab -f ~/fabfile.py -H localhost count_idcf_vms | awk 'NR==2 {print $0}')
    log "vm_count: $vm_count"
    if [ $locked -lt 1 ]; then
        redis-cli incr $lock_key
        redis-cli incr $incrd_key
        fab -f ~/fabfile.py -H localhost setup_idcf_vm:displayname=scale_$incrd
        redis-cli set $lock_key 0
        redis-cli del $queue
    else
        log "not deploying new vm"
    fi
fi

