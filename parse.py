import parse_fedxml as fed

src = [
    "https://laws-lois.justice.gc.ca/eng/XML/P-4.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/SOR-2019-251.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/C-42.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/SOR-2023-24.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/I-9.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/SOR-2018-120.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/T-13.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/SOR-2018-227.xml"
]
for url in src:
    act = fed.process_document(url)
    file_name = f"out/{act.title} - {act.chapter.replace('/', '-')}.md"

    with open(file_name, "w", encoding="utf-8") as f:
        formatter = fed.FormatterMarkdown(f)
        formatter.format(act)

for url in ["https://s3.ca-central-1.amazonaws.com/manuels-manuals-opic-cipo/MOPOP_English.html"]:
    import requests
    import html2text
    import os
    def html_to_markdown(url):
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Convert HTML to Markdown
            converter = html2text.HTML2Text()
            converter.body_width = 0  # Set to 0 for no line wrapping
            markdown_content = converter.handle(response.text)
            
            return markdown_content
        else:
            print(f"Failed to fetch content from {url}. Status code: {response.status_code}")
            return None
    
    md = html_to_markdown(url)
    file_name = url.split("/")[-1]
    file_name, _ = os.path.splitext(file_name)
    file_name = f"out/{file_name}.md"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(md)
