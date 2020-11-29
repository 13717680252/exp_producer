from pylatex import Document, LongTable, MultiColumn,Subsection,Section
import yaml
import os
import argparse
def run(args):
    templete_train = "python {} --do_train --yaml_args {} \n"
    templete_test = "python {} --do_test --yaml_args {} \n"
    config_yaml = yaml.load(open(args.yaml))
    random_seeds = args.seeds
    file_list = []
    out_dir = args.out_dir  ## output file for yaml and bash
    out_dir=os.path.abspath(out_dir)
    cli = args.cli
    cli = os.path.abspath(cli)
    out_name = args.exp_name
    log_dir = config_yaml["logging"]["log_dir"]
    for i in map(int,random_seeds):
        config_yaml["training"]["seed"] = i
        cur_name = "{}-{}".format(args.exp_name, i)
        config_yaml["exp_name"] = cur_name
        file_list.append(cur_name)
        yaml.dump(config_yaml, open(os.sep.join([out_dir, cur_name]) + ".yaml", "w"))
    bash_name = os.sep.join([out_dir, out_name]) + ".sh"
    with open(bash_name, "w")as f:
        for fname in file_list:
            f.write(templete_train.format(cli, os.sep.join([out_dir, fname]) + ".yaml"))
            f.write(templete_test.format(cli, os.sep.join([out_dir, fname]) + ".yaml"))
        gather_cli = os.sep.join((os.getcwd(), "gather.py"))
        gather = "python {} {} {} {}".format(gather_cli, log_dir, '"{}"'.format(" ".join(file_list)),
                                             os.sep.join([out_dir, out_name]) + ".tex")
        f.write(gather + "\n")
    return

parser=argparse.ArgumentParser()
parser.add_argument("yaml",type=str,help="base yaml config dir")
parser.add_argument("out_dir", type=str,help="output dir for bash and yaml configs")
parser.add_argument("cli",type=str,help="cli for training and testing")
parser.add_argument("exp_name",type=str,help="exp identifiers")
parser.add_argument("--seeds",type=list,default=[1,11,21,32,42])
args=parser.parse_args()
run(args)





def genenerate_longtabu():
    geometry_options = {
        "margin": "2.54cm",
        "includeheadfoot": True
    }
    results={"f1":{"en":[],"fr":[]}}
    results["acc"]=results["f1"]
    minimum = {"f1": {"en": 11.5, "fr": 32.557}}
    maximum = {"f1": {"en": 22.55, "fr": 32.1}}
    average = {"f1": {"en": 22, "fr": 32}}
    minimum["acc"] = minimum["f1"]
    maximum["acc"] = maximum["f1"]
    average["acc"] = average["f1"]
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
    doc.dump(open("test.txt", "w"))
