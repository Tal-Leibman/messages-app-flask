#!/bin/sh
# wait-for-postgres.sh

set -e

attempt_num=1
max_attempts=5
seconds=2
until psql -c '\l'; do
  if [ $attempt_num -eq $max_attempts ]
  then
      echo "Attempt $attempt_num failed and there are no more attempts left!"
      return 1
  else
      echo "Attempt $attempt_num failed! Trying again in $seconds seconds..."
      attempt_num=`expr "$attempt_num" + 1`
      sleep "$seconds"
  fi
done

>&2 echo "Postgres is up - executing command"
exec ${@}
