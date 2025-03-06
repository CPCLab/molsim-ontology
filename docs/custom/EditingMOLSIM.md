## Opening the Ontology

You can open and explore molsim using Protégé, a free, open-source ontology editor. Protégé is available in both desktop and web versions.

### IMPORTANT! 
To edit (adding/removing new terms) in MOLSIM, please only do so in the `src/ontology/molsim-edit.owl` file. 
The rest should be taken care of with ODK commands.

For importing new terms or adding components that are not covered by imports, please refer to the custom import or adding components manual, respectively. 

### Desktop Version

1. Download and install Protégé desktop from: https://protege.stanford.edu/
2. Launch Protégé
3. Go to File > Open
4. Navigate to the location of the `src/ontology/molsim-edit.owl` file and open it
5. Go to Protégé > Settings, on the Preferences window, go to the "New entities" tab, and set the parameters to the following values:
   
     ![protege_preferences.png](images/protege_preferences.png)
      

### Web Version - not recommended

1. Visit WebProtégé: https://webprotege.stanford.edu/
2. Create an account or log in
3. Click on "Create Project" or "Upload Project"
4. Upload the `molsim-edit.owl` file

Note: WebProtégé does not support reasoner. Please use the desktop version instead to ensure proper logical checks.

## Contributing

We welcome contributions to improve and expand molsim. Please feel free to submit issues or pull requests to our repository.

## License

https://creativecommons.org/licenses/by-nc-sa/4.0/

## Contact

f.musyaffa (at) fz-juelich (dot) de
