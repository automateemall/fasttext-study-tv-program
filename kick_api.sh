#
# NHK APIを叩き教師データ抽出
# https://api-portal.nhk.or.jp/doc-list-v2-con
# https://api.nhk.or.jp/v2/pg/list/130/{service}/{date}.json?key={apikey}
#
dataset=dataset.txt
mkdir -p json

touch ${dataset}

for s in `cat service.txt`; do
    for ((i=1; i < 8; i++)); do
        sv=`echo ${s} | grep -o "^.."`
        day=`date -d "${i} day" +'%Y-%m-%d'`
        url="${baseurl}/${sv}/${day}.json?key=${apikey}"
        echo "$url"
        curl $url | jq > "json/${sv}_${day}.json"
    done
done