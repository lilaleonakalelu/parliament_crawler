import pathlib
from datetime import datetime

import cassis
import time
import os
# path of the corpus where all xmi files are stored
XMI_CORPUS_PATH = "/vol/s5935481/parlamentary_xmi_corpus"
# dictionary with identifiers for the different parliaments
MASK = {
        "Reichstag": {"landtag":"Reichstag",
                      "origin_path":"/resources/corpora/parlamentary",
                      "user1":"abrami",
                      "user2":"hammerla",
                      "quelle":"BSB-Bayerische Staatsbibliothek",
                      "date_func": (lambda file_path: file_path.strip(".txt").split(" ")[-1]),
                      "subtitle": (lambda file_path: file_path.split("/")[-3].replace(" ", "") + "__" + "".join(file_path.split("/")[-1].split(" ")[0:2])),
                      "save_path": (lambda file_path: create_dirs(os.path.join(XMI_CORPUS_PATH, "reichstag", "/".join(file_path.split("/")[4:-1]))))
                      }

    }


def create_dirs(dir_path:str):
    """
    Help function to create directories, if they dont exist.
    :param dir_path:
    :return:
    """
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path


def current_milli_time():
    """
    returns timestamp in milliseconds.
    :return:
    """
    return round(time.time() * 1000)





def save_txt_as_xmi(txt_path:str, landtag:str, datum: str,
                    typesystem:cassis.TypeSystem, user1:str, user2:str,
                    origin_path:str, quelle:str, subtilte_protocol:str,
                    save_path:str):
    """
    landtag: parliament of the given protocol
    datum: date of the protocol with style: DD.MM.YYYY
    Function to save a txt file as apache uima xmi.
    :param txt_path:
    :param landtag:
    :param datum:
    :param typesystem:
    :return:
    """
    with open(txt_path, "r") as f:
        text = f.read()
    cas = cassis.Cas(typesystem=typesystem)

    cas.sofa_string = text
    cas.sofa_mime = "text"


    DocumentMetaData = typesystem.get_type("de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData")
    DocumentAnnotation = typesystem.get_type("org.texttechnologylab.annotation.DocumentAnnotation")
    DocumentModification = typesystem.get_type("org.texttechnologylab.annotation.DocumentModification")
    # DocumentMetaData
    document_title = landtag + "-Plenarprotokoll vom " + datum
    document_id = txt_path.split("/")[-1].replace(" ", "_").replace(".txt", ".xmi")
    # DocumentAnnotation
    date_time_obj = datetime.strptime(datum, '%d.%m.%Y')
    author = quelle
    subtitle = subtilte_protocol
    day = int(datum.split(".")[0])
    month = int(datum.split(".")[1])
    year = int(datum.split(".")[2])
    timestamp = int(datetime.timestamp(date_time_obj) * 1000)
    # DocumentModification
    user1 = user1
    user2 = user2
    comment1 = "Download"
    comment2 = "Transformation/Conversion"
    timestamp2 = int(os.path.getmtime(origin_path) * 1000)
    timestamp3 = int(current_milli_time())

    cas.add_all([
        DocumentMetaData(documentTitle=document_title, documentId=document_id),
        DocumentAnnotation(author=author, dateDay=day, subtitle=subtitle,
                           dateMonth=month, dateYear=year, timestamp=timestamp),
        DocumentModification(user=user1, timestamp=timestamp2, comment=comment1),
        DocumentModification(user=user2, timestamp=timestamp3, comment=comment2)
    ])

    cas.to_xmi(save_path + "/" + document_id)

    return


def save_directory_as_xmi(dir_path:str, mask_key:str, typesystem:cassis.TypeSystem):
    """
    Function saves a whole directory of txt-files as xmi. it needs directory path, a typesystem for
    apache uima and a mask_key, which is ja identifier for the parliament of the given txt files.
    :param dir_path:
    :param mask_key:
    :param typesystem:
    :return:
    """
    files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
    files = [file for file in files if os.path.isfile(file)]
    for file in files:
        save_path = MASK[mask_key]["save_path"]
        save_txt_as_xmi(
                        txt_path=file,
                        landtag=MASK[mask_key]["landtag"],
                        datum=MASK[mask_key]["date_func"](file),
                        typesystem=typesystem,
                        user1=MASK[mask_key]["user1"],
                        user2=MASK[mask_key]["user2"],
                        origin_path=MASK[mask_key]["origin_path"],
                        quelle=MASK[mask_key]["quelle"],
                        subtilte_protocol=MASK[mask_key]["subtitle"](file),
                        save_path=save_path
                        )




def main():
    with open('/home/s5935481/work4/parliament_crawler/src/convert_and_clean/TypeSystem.xml', 'rb') as f:
        typesystem = cassis.load_typesystem(f)

    file = "/vol/s5935481/parlamentary_reichstag_text/1867 - 1895/1. Leg.-Periode/1871,1/22. Sitzung 25.04.1871.txt"
    save_txt_as_xmi(
        file,
        MASK["Reichstag"]["landtag"], MASK["Reichstag"]["date_func"](file), typesystem,
        MASK["Reichstag"]["user1"], MASK["Reichstag"]["user2"], MASK["Reichstag"]["origin_path"],
        MASK["Reichstag"]["quelle"], MASK["Reichstag"]["subtitle"](file),
        "/vol/s5935481/BIN")

if __name__ == "__main__":
    main()