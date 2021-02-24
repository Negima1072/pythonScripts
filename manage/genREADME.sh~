#!/bin/bash
INFILES=(../*.py)
OUTFILE=../README.md

function extract_summary() {
  for f in "$@" 
  do
	  link=$(basename $f)
	  name=$(echo $link | sed -n  "s/^_\(.*\)\.[^.]*$/\1/p")
	  echo "* [$name]($link) - $(fgrep -A5 -i "#summary:" $f | tr -d \\r | grep -v "^#summary:" | sed -n "s/^ *\([^=#*].*\)$/\1/gp" | head -1)"
  done
}
INFILES=($(printf '%s\n' "${INFILES[@]}" | tr "\n" " "))
echo "${INFILES[@]}" | tr " " "\n"
echo "${#INFILES[@]} files."

cat <<EOF > $OUTFILE
$(cat README.head.md | tr -d \\r)
$(extract_summary ${INFILES[@]})
$(cat README.foot.md | tr -d \\r)
EOF
git add $OUTFILE
