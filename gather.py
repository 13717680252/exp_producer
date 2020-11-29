import os
import collections
import json
from pylatex import Document, LongTable, MultiColumn,Section
import argparse
def get_result(base_dir, fnames, output_dir):
    get_dict = lambda: collections.defaultdict(list)
    results = collections.defaultdict(get_dict)
    for name in fnames:
        cur_dir = os.sep.join(base_dir, name)
        cur_data = json.loads(open(cur_dir, "r", encoding="utf-8").read())
        for k in cur_data.keys():
            for lang in cur_data[k].keys():
                results[k][lang].append(cur_data[k][lang])
        average = collections.defaultdict(dict)
        minimum = collections.defaultdict(dict)
        maximum = collections.defaultdict(dict)
        for k in results.keys():
            for lang in results[k].keys():
                average[k][lang] = sum(results[k][lang]) / len(results[k][lang])
                minimum[k][lang] = min(results[k][lang])
                maximum[k][lang] = max(results[k][lang])
        geometry_options = {
            "margin": "2.54cm",
            "includeheadfoot": True
        }
        doc = Document(page_numbers=True, geometry_options=geometry_options)
        for idx, k in enumerate(results.keys()):
            with doc.create(Section("result for {}".format(k))):
                with doc.create(LongTable(" ".join(["l"] * (len(results[k]) + 1)))) as data_table:
                    data_table.add_hline()
                    langs = list(results[k].keys())
                    data_table.add_row([k] + langs)
                    data_table.add_hline()
                    data_table.end_table_header()
                    data_table.add_row(["min"] + ["%.2f" % minimum[k][lang] for lang in langs])
                    data_table.add_row(["max"] + ["%.2f" % maximum[k][lang] for lang in langs])
                    data_table.add_row(["avg"] + ["%.2f" % average[k][lang] for lang in langs])
                    data_table.end_table_footer()
        doc.dump(open(output_dir, "w"))


parser=argparse.ArgumentParser()
parser.add_argument("base_dir",type=str)
parser.add_argument("file_names", type=list)
parser.add_argument("output_dir",type=str)
args=parser.parse_args()
get_result(args.base_dir,args.file_names,args.output_dir)

