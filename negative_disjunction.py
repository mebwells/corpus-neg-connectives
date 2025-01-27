import stanza

from stanza.server import CoreNLPClient

import re
import csv
import pandas as pd
import glob

ONTONOTES_PATH = 'ontonotes_trees'

file_pattern = "**/*.parse"  # Matches .parse files in all subdirectories
files = glob.glob(file_pattern, recursive=True)

# Initialize a string to store all file contents
combined_data = ""

# Process each .parse file and append its content to the combined_data
for file_path in files:
    with open(file_path, 'r') as file:
        combined_data += file.read() + "\n"

parse_data_processed = re.sub(r"\n\n", "aaaaa", combined_data)
parse_data_processed = re.sub(r"\n", " ", parse_data_processed)
parse_data_processed = re.sub(r"\s\s+", "", parse_data_processed)
parse_data_processed = re.sub(r"aaaaa", "\n", parse_data_processed)

pattern = r"\bn[o']t\b.*?\bor\b"
not_or = ""

for line in parse_data_processed.split("\n"):
    if re.search(pattern, line, re.IGNORECASE):
        not_or += line + "\n"

not_or.split('\n')

print("The full data set has " + str(len(parse_data_processed.split('\n'))) + " sentences.")
print(str(len(not_or.split('\n'))) + " include 'not' followed by 'or'.")

full_parse = stanza.models.constituency.tree_reader.read_trees(parse_data_processed)
not_or_parse = stanza.models.constituency.tree_reader.read_trees(not_or)

not_or_df = pd.DataFrame(columns=['Sentence', 'PTBParse', 'NegDJ?', 'TregexCaught?'])

for tree in not_or_parse:
        words = tree.leaf_labels()
        full_sentence = " ".join(words)
        not_or_df.loc[len(not_or_df)] = [full_sentence, tree, "", ""]
not_or_df.to_csv('not_or.tsv', sep='\t')


def run_corenlp(start_port=9050, max_port=9150):
    port = start_port
    result = None
    while result is None:
        try:
            with CoreNLPClient(preload=False, endpoint=f'http://localhost:{port}', memory='16G') as client:
                result = client.tregex(trees=not_or_parse,
                                       pattern='(__ < (__ < (/^[Nn][o\']t$/ > (RB $.. (__ << /^or$/) & !$ (/^or$/ $-- /whether/)) | > (RB >: (ADVP $.. (__ << /^or$/) & !$ (/^or$/ $-- /whether/))))))')

                # Remove empty dictionaries from the list - comment out with 92 to see all empty matches too
                result['sentences'] = [entry for entry in result['sentences'] if entry]
                sentList = result['sentences']

            # Write results to a data frame and create it as a .tsv file
            ndj_df = pd.DataFrame(columns=['sentIndex', 'Neg DJ', 'PTB Match'])

            i = 0
            for sent in sentList:
                sentIndex = sent.get("0").get('sentIndex')
                negDJ = sent.get("0").get('spanString')
                ptbMatch = sent.get("0").get('match')
                ndj_df.loc[i] = [sentIndex, negDJ, ptbMatch]
                i += 1

            for index, row in not_or_df.iterrows():
                if index in set(ndj_df["sentIndex"]):
                    not_or_df.at[index, "TregexCaught?"] = "Y"
                else:
                    not_or_df.at[index, "TregexCaught?"] = "N"

            not_or_df.to_csv('not_or.tsv', sep='\t')
            ndj_df.to_csv('ndj_df.tsv', sep='\t', index=False)


        except Exception as e:
            print(f"Port {port} failed. Trying the next port. Error: {e}")
            port += 1  # Increment port after an exception

    return result['sentences']  # comment out ['sentences'] with 64-65 to see all empty matches too

run_corenlp(9050)