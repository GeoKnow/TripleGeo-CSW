#!/bin/bash

PIDFILE=/tmp/triplegeo-csw.pid
LOGFILE=/tmp/triplegeo-csw.uwsgi.log

if test -z "$(which uwsgi)"
then
    echo "[error] Cannot find uwsgi executable"
    exit 1
fi

case "$1" in
start)
    echo 'Starting uWSGI ...'
    uwsgi --ini config.ini --pidfile ${PIDFILE} --daemonize ${LOGFILE}
    ;;
restart)
    if test -f ${PIDFILE}
    then
        echo 'Restarting uWSGI service by pid ...'
        uwsgi --reload ${PIDFILE}
        if [ $? -ne 0 ]; then 
            echo 'OK' 
        else
            echo '[error] Failed to reload uWSGI service'
        fi
    fi
    ;;
stop)
    if test -f ${PIDFILE}
    then
        pid=$(cat ${PIDFILE})
        echo "Stopping uWSGI service by pid (${pid}) ..."
        uwsgi --stop ${PIDFILE}
        if [ $? -eq 0 ]; then 
            echo 'OK' 
            rm -v ${PIDFILE}; 
        else
            echo '[error] Failed to stop uWSGI service'
        fi
    fi
    ;;
*)
    echo "[error] Unknown command: $1"
    ;;
esac

