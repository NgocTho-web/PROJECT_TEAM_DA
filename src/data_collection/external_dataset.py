import kagglehub

# Download latest version
path = kagglehub.dataset_download("arthurio/books-from-blackwells-bookshop",
                                  output_dir=r"D:/PROJECT_TEAM_DA/PROJECT_TEAM_DA/data/raw/external_dataset.csv")

print("Path to dataset files:", path)