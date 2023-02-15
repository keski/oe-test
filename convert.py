from bs4 import BeautifulSoup
import os
import urllib.request
import yaml
import zipfile


def download_owl2vowl():
    """Download and extract OWL2VOWL."""
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
    """Generates VOWL specifications fpr ontologies."""
    # Note: The flag "add-opens" fixes an issue with "InaccessibleObjectException"
    # for later versions of Java
    for ontology in config["ontologies"]:
        source = ontology["source"]
        basename = os.path.basename(source).split(".")[0]
        version = ontology["version"]
        
        os.system(f"""
            java --add-opens java.base/java.lang=ALL-UNNAMED \
                -jar temp/owl2vowl.jar \
                -file {source} \
                -output docs/webvowl/data/{basename}-{version}.json
        """)

def create_documentation(config):
    for ontology in config["ontologies"]:
        web_path = ontology.get("web_path", "")
        os.system(f"mkdir -p docs/{web_path}")
        source = ontology["source"]
        basename = os.path.basename(source).split(".")[0]
        version = ontology["version"]
        
        # Note: Using the pyLODE package as a module currently fails, calling it using CLI method instead
        html_file = f"docs/{web_path}/{basename}-{version}.html"
        os.system(f"python3 -m pylode {source} -o {html_file}")      
        
        # Insert overview section into documentation with WebVOWL in an iframe
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            # Dynamically change the reference to webvowl/ when running on localhost
            dynamic_loading = """
            <script>
                window.onload = () => {
                    if (location.hostname === "localhost" || location.hostname === "127.0.0.1"){
                        let iframe = document.getElementById("iframe-overview");
                        let src = iframe.src;
                        src = src.substr(src.indexOf(location.host) + location.host.length);
                        iframe.src = "/docs" + src;
                    }
                }
            </script>"""
            overview = BeautifulSoup(f"""
                {dynamic_loading}
                <div id="overview" class="section">
                    <h2>Overview</h2>
                    <div class="figure">
                        <iframe id="iframe-overview" width="100%" height ="800px" src="/webvowl/index.html#{basename}-{version}"></iframe>
                        <div class="caption"><strong>Figure 1:</strong> Ontology overview</div>
                    </div>
                </section>
            """, "html.parser")
            tag = soup.find(id='metadata')
            tag.insert_after(overview)
            
        
        with open(html_file, "w") as f:
            f.write(str(soup))


def main(config):
    download_owl2vowl()
    generate_vowl(config)
    create_documentation(config)


if __name__ == "__main__":
    with open('config.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    main(config)