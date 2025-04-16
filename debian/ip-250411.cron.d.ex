#
# Regular cron jobs for the ip-250411 package.
#
0 4	* * *	root	[ -x /usr/bin/ip-250411_maintenance ] && /usr/bin/ip-250411_maintenance
