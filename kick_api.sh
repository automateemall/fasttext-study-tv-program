#
# NHK APIを叩き教師データ抽出
# https://api-portal.nhk.or.jp/doc-list-v2-con

# https://api.nhk.or.jp/v2/pg/list/130/{service}/{date}.json?key={apikey}
baseurl=https://api.nhk.or.jp/v2/pg/list/
mkdir -p json
export `cat .env`

for a in `cat sub/area.txt`; do
    for ((i=0; i < 6; i++)); do
        sv=tv
        area=`echo ${a} | grep -o "^..."`
        day=`date -d "${i} day" +'%Y-%m-%d'`
        url="${baseurl}/${area}/${sv}/${day}.json?key=${apikey}"
        echo "${url}"
        curl "${url}" | jq > "json/${sv}_${area}_${day}.json"
        sleep 1
    done
done

for s in `cat sub/service.txt`; do
    for ((i=0; i < 6; i++)); do
        sv=`echo ${s}`
        area=130
        day=`date -d "${i} day" +'%Y-%m-%d'`
        url="${baseurl}/${area}/${sv}/${day}.json?key=${apikey}"
        echo "${url}"
        curl "${url}" | jq > "json/${sv}_${area}_${day}.json"
        sleep 1
    done
done

find ./json -type f -size  1k | xargs rm || true