""" Flaski companion package"""

import os
os.environ["PYFLASKI"] = "1"

import pyflaski.circularbarplots
import pyflaski.david
import pyflaski.cellplot
import pyflaski.dendrogram
import pyflaski.heatmap
import pyflaski.histogram
import pyflaski.scatterplot
import pyflaski.violinplot
import pyflaski.gseaplot
import pyflaski.kegg
import pyflaski.lifespan
import pyflaski.mds
import pyflaski.pca
import pyflaski.tsne
import pyflaski.venndiagram
import pyflaski.lineplot

import json


def read_session(session_file):
    session={}
    if session_file.rsplit('.', 1)[1].lower() != "json"  :
        error_msg="The file you have uploaded is not a session file. Please make sure you upload a session file with the correct `ses` extension."
        return None, error_msg

    with open(session_file, "r") as f:
        session=json.load(f)

    FLASKI_version=session["APP_VERSION"]
    PYFLASKI_version=session["PYFLASKI_VERSION"]
    APP=list(session["session_data"]["app"].keys())[0]
    session=session["session_data"]["app"][APP]
    session_keys=list(session.keys())
    session_keys=", ".join(session_keys)

    print(f"- Session info -\nFlaski: {FLASKI_version}\npyflaski: {PYFLASKI_version}\nApp: {APP}\nItems: {session_keys}")
    # if session_["ftype"]!="session":
    #     error_msg="The file you have uploaded is not a session file. Please make sure you upload a session file."
    #     return None, error_msg

    # if session_["app"]!=app:
    #     error_msg="The file was not loaded as it is associated with the '%s' and not with this app." %session_["app"]
    #     return None, error_msg

    #del(session_["ftype"])
    #del(session_["COMMIT"])
    # for k in list(session_.keys()):
    #     session[k]=session_[k]

    return session, None
