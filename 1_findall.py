import glob
import re
import stanza
import pandas as pd

ONTONOTES_PATH = 'ontonotes_trees/'

# We're interested in the WSJ subdirectory, parts of the Web subcorpus, and English-language broadcast news
subdirectories = ['nw/wsj', 'wb/sel', 'wb/eng', 'bn/abc', 'bn/cnn', 'bn/mnb', 'bn/nbc', 'bn/pri', 'bn/voa']

# We're interested in the .parse files at any level of the subdirectories
file_pattern = '**/*.parse'

# We're interested in bracket trees that contain "not" or "n't" followed by "or"/"and"
or_match_pattern = r"\bn[o']?t\b.*?\bor\b"
and_match_pattern = r"\bn[o']?t\b.*?\band\b"

# Initialize a pandas dataframe for summary stats of each subcorpus
summary = pd.DataFrame(columns=['subcorpus', 'num_files', 'num_trees', 'num_linear_matches_or', 'num_linear_matches_and'])

for subdir in subdirectories:
    print("--------------------")
    files = glob.glob(ONTONOTES_PATH + subdir + '/' + file_pattern, recursive=True)
    print("Number of .parse files in " + subdir + ": " + str(len(files)))
    file_count = 0
    tree_count = 0
    match_count_or = 0
    match_count_and = 0
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
    matches_col_or = []
    matches_col_and = []
    for parse in parses_col:
        words = parse.leaf_labels()
        full_sentence = " ".join(words)
        sents_col.append(full_sentence)
        if re.search(or_match_pattern, full_sentence, re.IGNORECASE):
            matches_col_or.append(1)
            match_count_or += 1
        else:
            matches_col_or.append(0)
        if re.search(and_match_pattern, full_sentence, re.IGNORECASE):
            matches_col_and.append(1)
            match_count_and += 1
        else:
            matches_col_and.append(0)
    # Create a pandas dataframe with the columns `filename`, `treeno`, `tree`, `sentence`, `match_or`, and `match_and`
    df = pd.DataFrame({'filename': filename_col, 'treeno': treeno_col, 'tree': trees_col, 'sentence': sents_col, 'match_or': matches_col_or, 'match_and': matches_col_and})
    print("Number of sentences in " + subdir + " that match the 'or' pattern: " + str(match_count_or))
    print("Number of sentences in " + subdir + " that match the 'and' pattern: " + str(match_count_and))
    # Create headers for the results_or and results_and CSV files if they don't exist
    if subdir == subdirectories[0]:
        df[df['match_or'] == 1].drop(columns=['match_or', 'match_and']).to_csv('1_results_not_or.csv', mode='w', header=True, index=False)
        df[df['match_and'] == 1].drop(columns=['match_or', 'match_and']).to_csv('1_results_not_and.csv', mode='w', header=True, index=False)
    else:
        # Append dataframe rows with match_or = 1 to the results_or dataframe
        results_or = df[df['match_or'] == 1].drop(columns=['match_or', 'match_and'])
        results_or.to_csv('1_results_not_or.csv', mode='a', header=False, index=False)
        # Append dataframe rows with match_and = 1 to the results_and dataframe
        results_and = df[df['match_and'] == 1].drop(columns=['match_or', 'match_and'])
        results_and.to_csv('1_results_not_and.csv', mode='a', header=False, index=False)
    # Append a row to the summary dataframe
    summary = pd.concat([summary, pd.DataFrame([[subdir, file_count, tree_count, match_count_or, match_count_and]], columns=['subcorpus', 'num_files', 'num_trees', 'num_linear_matches_or', 'num_linear_matches_and'])])

summary.to_csv('1_summary_not.csv', index=False)