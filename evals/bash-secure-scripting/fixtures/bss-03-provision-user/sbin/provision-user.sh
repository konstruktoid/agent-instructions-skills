#!/bin/bash
# Create an application account and its database user.

. etc/db.conf

USERNAME=$1

useradd -m $USERNAME

PASSWORD=$RANDOM$RANDOM$RANDOM

echo "$USERNAME:$PASSWORD" | chpasswd

mysql -u admin -p$DB_ADMIN_PASSWORD -e "CREATE USER '$USERNAME'@'%' IDENTIFIED BY '$PASSWORD';"

echo "provisioned $USERNAME with password $PASSWORD" >> /var/log/provision.log
