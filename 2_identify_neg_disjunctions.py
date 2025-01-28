import pandas as pd
import stanza
from stanza.server import CoreNLPClient

# Open the CSV file containing sentences that match the linear query
results = pd.read_csv('results_not_or.csv')

parses = stanza.models.constituency.tree_reader.read_trees("\n".join(results['tree']))

tregex_pattern = '(__ < (__ < (/^[Nn][o\']t$/ > (RB $.. (__ << /^or$/) & !$ (/^or$/ $-- /whether/)) | > (RB >: (ADVP $.. (__ << /^or$/) & !$ (/^or$/ $-- /whether/))))))'

with CoreNLPClient(preload=False, memory='16G') as client:
    matches = client.tregex(trees=parses,
                           pattern=tregex_pattern)
    matches = [i for i in matches['sentences'] if i]
    flattened_matches = [value for m in matches for value in m.values()]
    query_df = pd.DataFrame(flattened_matches).drop('namedNodes', axis=1)   

# Merge the query results with the original results dataframe.
# query_df has a 'sentIndex' column that corresponds to the index of the sentence in the original dataframe.
results = results.merge(query_df, left_index=True, right_on='sentIndex', how='left')
results.drop(columns=['sentIndex'], inplace=True)

# If there are no matches, fill the cell with "NA"
results['match'] = results['match'].fillna("NA")
# If there is no spanString, fill the cell with "NA"
results['spanString'] = results['spanString'].fillna("NA")

# Strip newlines and multiple whitespace from the 'match' column
results['match'] = results['match'].str.replace("\n", " ", regex=True)
results['match'] = results['match'].str.replace("\s\s+", " ", regex=True)

results.to_csv('2_tregex_query_matches.csv', index=False)

# Create a summary dataframe of the number of matches per sentence. If the only match is "NA", it is not counted. Keep the 'filename', 'treeno', and 'sentence' columns.
summary = results.groupby(['filename','treeno','sentence'])['match'].apply(lambda x: x[x != "NA"].count()).reset_index(name='num_matches')
summary.to_csv('2_tregex_counts.csv', index=False)