import glob
import re
import stanza
import pandas as pd

ONTONOTES_PATH = 'ontonotes_trees/'

# We're interested in the WSJ subdirectory and the Selected Web Sentences subdirectory
subdirectories = ['nw/wsj', 'wb/sel', 'wb/eng', 'bn/abc', 'bn/cnn', 'bn/mnb', 'bn/nbc', 'bn/pri', 'bn/voa']

# We're interested in the .parse files at any level of the subdirectories
file_pattern = '**/*.parse'

# We're interested in bracket trees that contain "not" or "n't" followed by "or"
match_pattern = r"\bn[o']?t\b.*?\bor\b"

# Initialize a pandas dataframe to store the matching parse trees and associated sentences
results = pd.DataFrame(columns=['filename', 'treeno', 'tree', 'sentence'])

# Initialize a pandas dataframe for summary stats of each subcorpus
summary = pd.DataFrame(columns=['subcorpus', 'num_files', 'num_trees', 'num_linear_matches'])

# For each of the relevant subdirectories, iterate through the .parse files and find the sentences that match the pattern
for subdir in subdirectories:
    print("--------------------")
    files = glob.glob(ONTONOTES_PATH + subdir + '/' + file_pattern, recursive=True)
    print("Number of .parse files in " + subdir + ": " + str(len(files)))
    file_count = 0
    tree_count = 0
    match_count = 0
    trees_col = []
    filename_col = []
    treeno_col = []
    for file_path in files:
        file_count += 1
        treeno = 0
        with open(file_path, 'r') as file:
            file_data = file.read()
            for tree in file_data.split("\n\n"):
                # Remove all newlines and tab sequences from the tree
                tree = re.sub(r"\n\n+", " ", tree)
                tree = re.sub(r"\s\s+", "", tree)
                if len(tree) > 0:
                    treeno += 1
                    tree_count += 1
                    trees_col.append(tree)
                    # store filename excluding the .parse extension and the ONTONOTES_PATH
                    filename_col.append(file_path[len(ONTONOTES_PATH):-6])
                    treeno_col.append(treeno)
    print("Number of trees in " + subdir + ": " + str(tree_count))
    # Create an array of parses from the `tree` column of the dataframe 
    parses_col = stanza.models.constituency.tree_reader.read_trees("\n".join(trees_col))
    sents_col = []
    matches_col = []
    for parse in parses_col:
        words = parse.leaf_labels()
        full_sentence = " ".join(words)
        sents_col.append(full_sentence)
        if re.search(match_pattern, full_sentence, re.IGNORECASE):
            matches_col.append(1)
            match_count += 1
        else:
            matches_col.append(0)
    # Create a pandas dataframe with the columns `filename`, `treeno`, `tree`, `sentence`, and `match`
    df = pd.DataFrame({'filename': filename_col, 'treeno': treeno_col, 'tree': trees_col, 'sentence': sents_col, 'match': matches_col})
    print("Number of sentences in " + subdir + " that match the pattern: " + str(match_count))
    # Append dataframe rows with match = 1 to the results dataframe
    results = pd.concat([results, df[df['match'] == 1]])
    # Append a row to the summary dataframe
    summary = pd.concat([summary, pd.DataFrame([[subdir, file_count, tree_count, match_count]], columns=['subcorpus', 'num_files', 'num_trees', 'num_linear_matches'])])

# Save the results to a CSV file. Drop the 'match' column before saving.
results.drop(columns=['match']).to_csv('results_not_or.csv', index=False)
summary.to_csv('summary_not_or.csv', index=False)