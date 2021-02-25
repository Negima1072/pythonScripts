#!/bin/bash
INFILES=(../*.py)
OUTFILE=../README.md

function extract_summary() {
  for f in "$@" 
  do
	  link=$(basename $f)
	  name=$(echo $link | sed -e "s/\(.*\).py/\1/")
	  echo "* [$name]($link) - $(fgrep -A5 -i "#summary:" $f | tr -d \\r | grep "#summary:" | sed -e "s/#summary:\(.*\)/\1/")"
  done
}
INFILES=($(printf '%s\n' "${INFILES[@]}" | tr "\n" " "))
echo "${INFILES[@]}" | tr " " "\n"
echo "${#INFILES[@]} files."

cat <<EOF > $OUTFILE
$(cat README.head.md | tr -d \\r)
$(extract_summary ${INFILES[@]})
$(cat README.foot.md | tr -d \\r)


$(&& date +"Updt: %Y/%m/%d %I:%M:%S by genREADME")
EOF
git add $OUTFILE
