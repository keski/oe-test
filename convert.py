from bs4 import BeautifulSoup
import os
import urllib.request
import zipfile


def download_owl2vowl():
    """Download and unzip OWL2VOWL."""
    os.system("mkdir -p temp/")
    path = "./temp"
    path_to_jar = f"{path}/owl2vowl.jar"
    if not os.path.isfile(path_to_jar):
        path_to_zip = f"{path}/owl2vowl_0.3.7.zip"
        if not os.path.isfile(path_to_zip):
            url = "http://vowl.visualdataweb.org/downloads/owl2vowl_0.3.7.zip"
            urllib.request.urlretrieve(url, path_to_zip)

        with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
            zip_ref.extractall(path)


def ontologies_to_vowl(ontologies=None):
    """Converts the provided set of ontologies into the VOWL."""
    # Note: The flag "add-opens" fixes an issue with "InaccessibleObjectException" for later versions of Java
    for ontology in ontologies:
        path = ontology["path"]
        filename = path.split("/")[-1].split(".")[0]
        version = ontology["version"]
        os.system(f"""
            java --add-opens java.base/java.lang=ALL-UNNAMED \
                -jar temp/owl2vowl.jar \
                -file {path} \
                -output docs/webvowl/data/{filename}-{version}.json
        """)

def create_documentation(ontologies):
    for ontology in ontologies:
        path = ontology["path"]
        filename = path.split("/")[-1].split(".")[0]
        version = ontology["version"]
        #os.system("mkdir -p temp/")
        
        # Note: Using the pyLODE package as a module directly does not work correctly, calling it using CLI instead 
        os.system(f"python3 -m pylode {path} -o docs/{filename}-{version}.html")
        with open(f"docs/{filename}-{version}.html") as f:
            soup = BeautifulSoup(f, "html.parser")
            vowl = BeautifulSoup("")
            overview = BeautifulSoup(f"""
                <div id="overview" class="section">
                    <h2>Overview</h2>
                    <div class="figure">
                        <iframe width="100%" height ="800px" src="webvowl/index.html#{filename}-{version}"></iframe>
                        <div class="caption"><strong>Figure 1:</strong> Ontology overview</div>
                    </div>
                </section>
            """, "html.parser")
            tag = soup.find(id='metadata')
            tag.insert_after(overview)
        
        with open(f"docs/{filename}-{version}.html", "w") as f:
            f.write(str(soup))

def main():
    ontologies = [
        {"path": "ontology/ce-graph.owl", "version": "1.0" },
        {"path": "ontology/ce-graph.owl", "version": "1.1" }
    ]

    download_owl2vowl()
    ontologies_to_vowl(ontologies)
    create_documentation(ontologies)


if __name__ == "__main__":
    main()