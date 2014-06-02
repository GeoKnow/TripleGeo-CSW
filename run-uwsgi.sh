#!/bin/bash

PIDFILE=/tmp/triplegeo-csw.pid

case "$1" in

start)
    echo 'Starting uWSGI ...'
    uwsgi --ini config.ini --pidfile ${PIDFILE}
    rm -v ${PIDFILE}
    ;;
restart)
    echo 'Restarting uWSGI service by pid ...'
    if test -f ${PIDFILE}
    then
        uwsgi --reload ${PIDFILE}
    fi
    ;;
stop)
    echo 'Stopping uWSGI service by pid ...'
    if test -f ${PIDFILE}
    then
        uwsgi --stop ${PIDFILE}
    fi
    ;;
*)
    echo ' ** Unknown command **'
    ;;
esac

