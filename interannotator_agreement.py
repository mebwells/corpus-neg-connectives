import pandas as pd
from sklearn.metrics import cohen_kappa_score

# Load annotations from a CSV file
df = pd.read_csv("interannotator_disjunction_annotations.tsv", delimiter="\t")

# Extract the two annotators' labels
annotations_num_1 = df["micaela_num"]
annotations_num_2 = df["brandon_num"]

annotations_num_1 = annotations_num_1.astype(str)
annotations_num_2 = annotations_num_2.astype(str)

# Compute Cohen's Kappa
kappa_num = cohen_kappa_score(annotations_num_1, annotations_num_2)
print(f"Cohen's Kappa Score for number of NDJ: {kappa_num:.3f}")


# Extract the two annotators' labels
annotations_interp_1 = df["micaela_interp"]
annotations_interp_2 = df["brandon_interp"]

annotations_interp_1 = annotations_interp_1.astype(str)
annotations_interp_2 = annotations_interp_2.astype(str)

# Compute Cohen's Kappa
kappa_interp = cohen_kappa_score(annotations_interp_1, annotations_interp_2)
print(f"Cohen's Kappa Score for interpretation of NDJ: {kappa_interp:.3f}")