#!/bin/bash
DB=${1}
STATIONLIST=(87440 77210 89230 89230 99270 107440 78550)

for s in ${STATIONLIST[@]}
do
  rm ${s}.*
  wget "http://opendata-download-metobs.smhi.se/explore/zip?parameterIds=3,4&stationId=${s}&period=corrected-archive&includeMetadata=false" -O ${s}.csv
  tail -n +13 ${s}.csv > "${s}.clean"
  sed -i 's/;/,/g' "${s}.clean"
  cut -d',' -f -6 ${s}.clean > ${s}.clean.cut
  #sed -i -e 's/ (UTC)//' "${s}.clean.cut"
  awk -v var="${s}" -F=, '{$(NF+1)=var}1' OFS=, ${s}.clean.cut > cleaned.csv
  cat import_sqlite.sql | sqlite3 $DB
done


