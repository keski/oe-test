import argparse
from bs4 import BeautifulSoup
import os
import urllib.request
import yaml
import zipfile


def download_owl2vowl():
    """Download and extract OWL2VOWL if not already present."""
    path = "./temp"
    path_to_jar = f"{path}/owl2vowl.jar"
    if not os.path.isfile(path_to_jar):
        path_to_zip = f"{path}/owl2vowl_0.3.7.zip"
        if not os.path.isfile(path_to_zip):
            url = "http://vowl.visualdataweb.org/downloads/owl2vowl_0.3.7.zip"
            urllib.request.urlretrieve(url, path_to_zip)

        with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
            zip_ref.extractall(path)


def generate_vowl(config):
    """Generate VOWL specifications."""
    # Note: The flag "add-opens" below fixes an issue with
    # "InaccessibleObjectException" in later versions of Java
    for ontology in config["ontologies"]:
        source = ontology["source"]
        basename = os.path.basename(source).split(".")[0]
        web_path = ontology["web_path"]
        os.system(f"mkdir -p docs/webvowl/data/{web_path}/")
        os.system(f"""
            java -Dlog4j.configurationFile=log4j2.xml \
                --add-opens java.base/java.lang=ALL-UNNAMED \
                -jar temp/owl2vowl.jar \
                -file {source} \
                -output docs/webvowl/data/{web_path}/{basename}.json > /dev/null
        """)


def copy_ontologies(config):
    """Copy ontologies to web path."""
    for ontology in config["ontologies"]:
        source = ontology["source"]
        web_path = ontology["web_path"]
        os.system(f"mkdir -p docs/{web_path}")
        os.system(f"cp {source} docs/{web_path}")


def create_documentation(config):
    """Generate LODE documentation and instert the VOWL visualization."""
    for ontology in config["ontologies"]:
        web_path = ontology.get("web_path", "")
        os.system(f"mkdir -p docs/{web_path}")
        source = ontology["source"]
        basename = os.path.basename(source).split(".")[0]
        
        # Relative path to the webvowl lib
        rel = "../" * web_path.count("/")
        
        # Note: Using the pyLODE package as a module currently fails, calling it using CLI method instead
        html_file = f"docs/{web_path}/index.html"
        os.system(f"python3 -m pylode {source} -o {html_file}")      
        
        # Insert overview section into documentation with WebVOWL in an iframe
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            overview = BeautifulSoup(f"""
                <div id="overview" class="section">
                    <h2>Overview</h2>
                    <div class="figure">
                        <iframe id="iframe-overview" width="100%" height ="800px" src="{rel}/webvowl/index.html#{web_path}{basename}"></iframe>
                        <div class="caption"><strong>Figure 1:</strong> Ontology overview</div>
                    </div>
                </section>
            """, "html.parser")
            tag = soup.find(id='metadata')
            tag.insert_after(overview)
            
        with open(html_file, "w") as f:
            f.write(str(soup))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.yml")
    
    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    download_owl2vowl()
    generate_vowl(config)
    copy_ontologies(config)
    create_documentation(config)

if __name__ == "__main__":
    main()