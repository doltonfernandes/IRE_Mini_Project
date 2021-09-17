#!/bin/bash
# progress bar function
prog() {
    local w=80 p=$1;  shift
    # create a string of spaces, then change them to dots
    printf -v dots "%*s" "$(( $p*$w/100 ))" ""; dots=${dots// /.};
    # print those dots on a fixed-width space plus the percentage etc. 
    printf "\r\e[K|%-*s| %3d%% %s" "$w" "$dots" "$p" "$*"; 
}

rm -f queries_op.txt

prog "0"
pFactor=$(cat $2 | wc -l)
pFactor=$(echo "100 / $pFactor" | bc -l)
IFS=$'\n'
currLine=0
for line in $(cat "$2");
do
	currLine=$((currLine+1))
	python query.py "$1" "$line" >> queries_op.txt
	prog $(python -c "print(int($currLine * $pFactor))")
done