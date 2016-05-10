#!/bin/sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
command="java -jar $DIR/lib/rabix-backend-local-0.0.1-SNAPSHOT.jar"
for i in "$@"
do
    command="$command $i"
done

eval $command
