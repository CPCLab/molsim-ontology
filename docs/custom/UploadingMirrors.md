# Uploading mirrors of large ontology files

Some mirror files can not be uploaded to GitHub due to file size, such as CHEBI, which breaks the automated validation pipeline. One workaraound is the option to use the import files as mirror files on GitHub. To achieve this, follow the steps outlined below.

1. On your local machine, move all files in your `src/ontology/mirror/` directory outside of the git directory.
2. Copy all `<ontology>_import.owl` files from your `src/ontology/imports/` directory into the `src/ontology/mirror/` directory.
3. Rename the files inside the `src/ontology/mirror/` directory from `<ontology>_import.owl` to `<ontology>.owl`.
4. Add, commit, and push your changes to GitHub. Now, the validation pipeline should run through successfully.
5. On your local machine, delete the files in your `src/ontology/mirror/` directory again, and move the original mirrors that are now located outside of the git directory back into the `src/ontology/mirror/` directory.
6. Run the git command `git update-index --assume-unchanges src/ontology/mirror/` to make sure on the next commit, the file changes in the `src/ontology/mirror/` directory are not pushed to GitHub.
7. These steps need to be repeated every time any of the ontology files in ``src/ontology/imports/` change or if a new ontology is added.