import parse_fedxml as fed

src = [
    "https://laws-lois.justice.gc.ca/eng/XML/P-4.xml",
    "https://laws-lois.justice.gc.ca/eng/XML/SOR-2019-251.xml"
]
for url in src:
    act = fed.process_document(url)
    file_name = f"out/{act.title} - {act.chapter.replace('/', '-')}.md"

    with open(file_name, "w", encoding="utf-8") as f:
        formatter = fed.FormatterMarkdown(f)
        formatter.format(act)

