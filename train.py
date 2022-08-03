#
# fasttext用の教師ファイルを作成
#
import os
import json
import MeCab
import re
import fasttext

LABEL_PREFIX = "__label__"
ROOT_PATH = os.getcwd() + "/"
GENRE_MASTER_FILE = "etc/genre.txt"
WAKATI_FILE = "train/wakati.txt"
TRAIN_FILE = "train/nhk.train"
VALID_FILE = "train/nhk.valid"
MODEL = "model/nhk_mode.bin"
MODEL_LOW = "model/nhk_mode_low.bin"
TEST_TXT = "etc/valid_tmp.txt"


def cleanText(txt):
    return re.sub("[“▼…▽！-／：-＠［-｀｛-～、-〜”’・]+", " ", txt)


def generate_genre_master(file):
    genre_master = {}
    g = open(file, "r", encoding="utf-8")
    for l in g.readlines():
        tmp = l.split(",")
        genre_master.update({tmp[0]: tmp[1]})
    g.close()
    return genre_master


def wakati_by_mecab(tagger, txt):
    terms = []
    node = tagger.parseToNode(cleanText(txt))
    while node:
        terms.append(node.surface)
        node = node.next
    return ' '.join(terms)


def extract_wakati_txt(tagger, json_path, genre_master):
    result = []
    os.chdir(json_path)
    for filename in os.listdir('.'):
        with open(filename, "r", encoding="utf-8") as f:
            service = filename[0:2]
            jsonDict = json.load(f)
            for obj in jsonDict['list'][service]:
                line = "{0} {1} {2}".format(
                    obj['title'], obj['subtitle'], obj['content'])
                wakati = wakati_by_mecab(tagger, line)
                genres = []
                for genre in obj["genres"]:
                    if (len(genre) < 4):
                        genre = "{0}00".format(genre)
                    genres.append(LABEL_PREFIX + genre_master[genre])
                result.append("{0} {1}".format(" ".join(genres), wakati))
    return result


def create_train_txt():
    tagger = MeCab.Tagger('-Owakati')
    genre_master = generate_genre_master(ROOT_PATH + GENRE_MASTER_FILE)
    wakati = extract_wakati_txt(tagger, ROOT_PATH + "json", genre_master)
    train_record = int(len(wakati) * 0.7)

    w = open(ROOT_PATH + WAKATI_FILE, 'w', encoding="utf-8")
    train = open(ROOT_PATH + TRAIN_FILE, 'w', encoding="utf-8")
    valid = open(ROOT_PATH + VALID_FILE, 'w', encoding="utf-8")
    for i, r in enumerate(wakati):
        print(r)
        w.writelines(r + '\n')
        if (i < train_record):
            train.writelines(r + '\n')
        else:
            valid.writelines(r + '\n')
    w.close()
    train.close()
    valid.close()


def create_model(level_low):
    if level_low:
        model = fasttext.train_supervised(input=ROOT_PATH + TRAIN_FILE)
        model_file = MODEL_LOW
    else:
        model = fasttext.train_supervised(input=ROOT_PATH + TRAIN_FILE, epoch=100, lr=1.0, wordNgrams=1, bucket=200000, dim=500)
        # model = fasttext.train_supervised(input=ROOT_PATH + TRAIN_FILE, autotuneValidationFile= ROOT_PATH + VALID_FILE)
        model_file = MODEL
    print(model.test(ROOT_PATH + VALID_FILE))
    model.save_model(ROOT_PATH + model_file)
    return model


def test_model(model, file):
    with open(file, 'r', encoding='utf-8') as f:
        p = 0
        for i, line in enumerate(f):
            tagger = MeCab.Tagger('-Owakati')
            ar = line.split("%%%")
            wakati = wakati_by_mecab(tagger, ar[0])
            r = model.predict(wakati, k=5)
            # print (wakati)
            # print(r)
            expected = ar[1]
            match = 0
            for g in r[0]:
                tmp = g.replace(LABEL_PREFIX, "")
                if (tmp in expected):
                    match += 1
            # print ("正解: " + ar[1])
            print(match / len(ar[1].split(",")))
            p += match / len(ar[1].split(","))
        print("総合点:{:.2f}".format(p))

#
# main
#


# create_train_txt()
model = create_model(False)
model = fasttext.load_model(ROOT_PATH + MODEL_LOW)
test_model(model, ROOT_PATH + TEST_TXT)

# model = create_model(True)
model = fasttext.load_model(ROOT_PATH + MODEL)
test_model(model, ROOT_PATH + TEST_TXT)
