import sys
import requests
from typing import List
import xml.etree.ElementTree as ET

def is_empty(text:str) -> bool:
    return text is None or text == ""


class appender:
    def __init__(self):
        self.text:str = ""
    
    def __str__(self):
        return self.text
    
    def print(self, text:str = ""):
        self.write(text + "\n")

    def write(self, text:str = ""):
        self.text = self.text + text

class TableGroupTable:
    def __init__(self, caption:str, title:str):
        self.caption=caption
        self.title=title
        self.columns:List[str] = []
        self.rows:List[List[str]] = []
    
    def set_columns(self, columns:List[str]):
        self.columns:List[str]=columns

    def add_row(self, row:List[str]):
        self.rows += [row]

class SchedulePart:
    def __init__(self):
        pass

class Schedule:
    def __init__(self, label:str):
        self.label = label
        self.parts:List[SchedulePart] = []
    
    def add_part(self, part:SchedulePart):
        self.parts +=  [part]

class Provision(SchedulePart):
    def __init__(self, text:str):
        self.text = text

class BilingualGroupSchedule(SchedulePart):
    def __init__(self, items_en:List[str], items_fr:List[str]):
        self.items_en=items_en
        self.items_fr=items_fr
        pass

class Heading(SchedulePart):
    def __init__(self, title:str, heading_label:str, heading_title:str):
        self.title=title
        self.heading_title=heading_title
        self.heading_label=heading_label

class TableGroup(SchedulePart):
    def __init__(self, label:str, title:str):
        self.tables = []
        self.label=label
        self.title=title

    def add_table(self, table:TableGroupTable):
        self.tables += [table]

class FormSchedule(SchedulePart):
    def __init__(self, title:str, form_label:str, form_title:str, form_content:str):
        self.title = title
        self.form_label=form_label
        self.form_title=form_title
        self.form_content=form_content

class Subparagraph:
    def __init__(self, label:str, text:str):
        self.label:str = label
        self.text:str = text

    def __str__(self):
        return f"{self.label} {self.text}"

class Paragraph:
    def __init__(self, label:str, text:str):
        self.label:str = label
        self.text:str = text
        self.repealed:str = None
        self.subparagraph:List[Subparagraph] = []

    def __str__(self):
        if not is_empty(self.repealed):
            return f"{self.repealed}"
        else:
            return f"{self.label} {self.text}"

    def add_subparagraph(self, subparagraph:Subparagraph):
        self.subparagraph += [subparagraph]
    
    def set_repealed(self, repealed:str):
        self.repealed = repealed

class Definition:
    def __init__(self, term_en:str, term_fr:str, text:str):
        self.term_en:str = term_en
        self.term_fr:str = term_fr
        self.text:str = text
        self.paragraphs:List[Paragraph] = []
        self.repealed:str = ""

    def __str__(self):
        return f"{self.term_en} {self.text}"
    
    def set_repealed(self, repealed:str):
        self.repealed = repealed

    def add_paragraph(self, paragraph:Paragraph):
        self.paragraphs += [paragraph]


class Subsection:
    def __init__(self, label:str, text:str):
        self.label:str = label
        self.text:str = text
        self.repealed:str = None
        self.paragraphs:List[Paragraph] = []
        self.definitions:List[Definition] = []
    
    def set_repealed(self, repealed:str):
        self.repealed = repealed

    def add_paragraph(self, paragraph:Paragraph):
        self.paragraphs += [paragraph]

    def add_definition(self, definition:Definition):
        self.definitions += [definition]

class Section:
    def __init__(self, label:str, heading:str, marginal_note:str, text:str):
        self.label:str = label
        self.heading:str = heading
        self.marginal_note:str = marginal_note
        self.text:str = text
        self.repealed:str = None
        self.paragraphs:List[Paragraph] = []
        self.subsections:List[Subsection] = []
        self.definitions:List[Definition] = []

    def set_repealed(self, repealed:str):
        self.repealed = repealed

    def add_paragraph(self, paragraph:Paragraph):
        self.paragraphs += [paragraph]
    
    def add_subsection(self, subsection:Subsection):
        self.subsections += [subsection]

    def add_definition(self, definition:Definition):
        self.definitions += [definition]

class Act:
    def __init__(self, short_title:str, long_title:str, chapter:str, consolidated:str, regulation_act:str):
        self.short_title:str = short_title
        self.long_title:str = long_title
        self.chapter:str = chapter
        self.sections:List[Section] = []
        self.schedules:List[Schedule] = []
        self.jurisdiction:str = "Canadian"
        self.consolidated = consolidated
        self.regulation_act = regulation_act

        if self.short_title:
            self.title = self.short_title
        else:
            self.title = self.long_title

    def add_section(self, section:Section):
        self.sections = self.sections + [section]
    
    def add_schedule(self, schedule:Schedule):
        self.schedules += [schedule]

class Formatter:
    def __init__(self):
        pass

class FormatterMarkdown(Formatter):
    def __init__(self):
        pass
    
    def format(self, act:Act) -> str:
        txt:appender = appender()
        txt.write(self.str_title(act=act))
        
        for section in act.sections:
            txt.write(self.str_section_header(act, section))
            if len(section.paragraphs) > 0:
                for paragraph in section.paragraphs:
                    if len(paragraph.subparagraph) > 0:
                        for subparagraph in paragraph.subparagraph:
                            txt.write(self.str_subparagraph(act=act, section=section, paragraph=paragraph, subparagraph=subparagraph))
                    else:
                        txt.write(self.str_paragraph(act=act, section=section, subsection=None, paragraph=paragraph))
            elif len(section.subsections) > 0:
                for subsection in section.subsections:
                    if len(subsection.paragraphs) > 0:
                        for paragraph in subsection.paragraphs:
                            txt.write(self.str_paragraph(act=act, section=section, subsection=subsection, paragraph=paragraph))
                    elif len(subsection.definitions) > 0:
                        for definition in subsection.definitions:
                            txt.write(self.str_definition(act=act, section=section, subsection=subsection, definition=definition))
                    else:
                        txt.write(self.str_subsection(act=act, section=section, subsection=subsection))
            elif len(section.definitions) > 0:
                for definition in section.definitions:
                    txt.write(self.str_definition(act=act, section=section, subsection=None, definition=definition))
            else:
                txt.write(self.str_section(act, section))

        for schedule in act.schedules:
            txt.write(self.str_schedule(act, schedule))
        return str(txt)
    
    def str_h1(self, text:str) -> str:
        txt = appender()
        txt.print()
        txt.print(text)
        txt.print("=" * len(text))
        txt.print()
        return str(txt)

    def str_h2(self, text:str) -> str:
        txt = appender()
        txt.print()
        txt.print(text)
        txt.print("-" * len(text))
        txt.print()
        return str(txt)

    def str_h3(self, text:str) -> str:
        txt = appender()
        txt.print()
        txt.print("### " +  text)
        txt.print()
        return str(txt)

    def str_title(self, act:Act) -> str:
        txt = appender()
        if act.short_title:
            txt.write(self.str_h1(f"{act.short_title} ({act.long_title}) - {act.chapter}"))
        else:
            txt.write(self.str_h1(f"{act.long_title} - {act.chapter}"))
        txt.print(f"Consolidated on {act.consolidated}")
        txt.print()

        return str(txt)

    def str_section_header(self, act:Act, section:Section) -> str:
        return self.str_h2(f"Section {section.label} : {section.heading} / {section.marginal_note}")

    def str_section(self, act:Act, section:Section):
        txt = appender()
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        if not is_empty(section.repealed):
            txt.print(f"Section {section.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, was repealed: {section.repealed}\n")
        else:
            txt.print(f"Section {section.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                f"    {section.text}\n")
        return str(txt)
    
    def str_definition(self, act:Act, section:Section, subsection:Subsection, definition:Definition)  -> str:
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt = appender()
        if subsection:
            if not is_empty(definition.repealed):
                txt.print(f"The definition for \"{definition.term_en}\" in Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, was repealed: {definition.repealed}\n")
            else:
                if len(definition.paragraphs) > 0:
                    if not is_empty(section.text) and not is_empty(subsection.text) and is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label} {subsection.text}\n> " +
                            f"            {definition.term_en}: {definition.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">                {paragraph.label} {paragraph.text}")
                        txt.print()
                    elif is_empty(section.text) and not is_empty(subsection.text) and not is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label}{subsection.label} {subsection.text}\n> " +
                            f"        {definition.term_en}: {definition.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">            {paragraph.label} {paragraph.text}")
                        txt.print()
                    elif not is_empty(section.text) and is_empty(subsection.text) and not is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label}{definition.term_en}: {definition.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">            {paragraph.label} {paragraph.text}")
                        txt.print()
                    elif not is_empty(section.text) and not is_empty(subsection.text) and is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label} {subsection.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">            {definition.term_en}:{paragraph.label} {paragraph.text}")
                        txt.print()
                    elif is_empty(section.text) and is_empty(subsection.text) and not is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label}{subsection.label}{paragraph.label} {definition.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">        {paragraph.label}{definition.term_en}: {paragraph.text}")
                        txt.print()
                    elif is_empty(section.text) and not is_empty(subsection.text) and is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label}{subsection.label} {subsection.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">        {definition.term_en}:{paragraph.label} {paragraph.text}")
                        txt.print()
                    elif not is_empty(section.text) and is_empty(subsection.text) and is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label} {section.text}")
                        for paragraph in definition.paragraphs:
                            txt.print(f">        {subsection.label}{definition.term_en}: {paragraph.label} {paragraph.text}")
                        txt.print()
                    elif is_empty(section.text) and is_empty(subsection.text) and is_empty(definition.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":")
                        for paragraph in definition.paragraphs:
                            txt.print(f">    {section.label}{subsection.label}{definition.term_en}: {paragraph.label} {paragraph.text}")
                        txt.print()
                else:
                    if not is_empty(section.text) and not is_empty(subsection.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label} {subsection.text}\n> " +
                            f"            {definition.term_en}: {definition.text}\n")
                    elif is_empty(section.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label}{subsection.label} {subsection.text}\n> " +
                            f"        {definition.term_en}: {definition.text}\n")
                    elif is_empty(subsection.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label}{definition.term_en}: {definition.text}\n")
                    else:
                        txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                            f"    {section.label}{subsection.label}{definition.term_en}: {definition.text}\n")
            if not is_empty(definition.term_fr):
                txt.print()
                txt.print(f"According to Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, \"{definition.term_en}\" translate to French as \"{definition.term_fr}\".")
                txt.print()
        else:
            if definition.repealed:
                txt.print(f"The definition for \"{definition.term_en}\" in Section {section.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, was repealed: {definition.repealed}\n")
            else:
                if not is_empty(section.text):
                    txt.print(f"Section {section.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                        f"    {section.label} {section.text}\n> " +
                        f"        {definition.term_en}: {definition.text}\n")
                else:
                    txt.print(f"Section {section.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} defines \"{definition.term_en}\":\n> " +
                        f"    {section.label}{definition.term_en}: {definition.text}\n")
            if not is_empty(definition.term_fr):
                txt.print()
                txt.print(f"According to Section {section.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, \"{definition.term_en}\" translate to French as \"{definition.term_fr}\".")
                txt.print()
                    
        return str(txt)

    def str_paragraph(self, act:Act, section:Section, subsection:Subsection, paragraph:Paragraph):
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt = appender()
        if subsection:
            if not is_empty(paragraph.repealed):
                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, was repealed: {paragraph.repealed}\n")
            else:
                if len(paragraph.subparagraph) > 0:
                    n_minus_one = max(0, len(paragraph.subparagraph) - 1 - 1)
                    if paragraph.subparagraph[n_minus_one].text.endswith(" and") or paragraph.subparagraph[n_minus_one].text.endswith(" or"):
                        if not is_empty(section.text) and not is_empty(subsection.text) and is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label} {section.text}\n> " +
                                f"        {subsection.label} {subsection.text}\n> " +
                                f"            {paragraph.label} {paragraph.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">                {subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif is_empty(section.text) and not is_empty(subsection.text) and not is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label}{subsection.label} {subsection.text}\n> " +
                                f"        {paragraph.label} {paragraph.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">            {subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif not is_empty(section.text) and is_empty(subsection.text) and not is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label} {section.text}\n> " +
                                f"        {subsection.label}{paragraph.label} {paragraph.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">            {subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif not is_empty(section.text) and not is_empty(subsection.text) and is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label} {section.text}\n> " +
                                f"        {subsection.label} {subsection.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">            {paragraph.label}{subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif is_empty(section.text) and is_empty(subsection.text) and not is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label}{subsection.label}{paragraph.label} {paragraph.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">        {subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif is_empty(section.text) and not is_empty(subsection.text) and is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label}{subsection.label} {subsection.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">        {paragraph.label}{subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif not is_empty(section.text) and is_empty(subsection.text) and is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                f"    {section.label} {section.text}")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">        {subsection.label}{paragraph.label}{subparagraph.label} {subparagraph.text}")
                            txt.print()
                        elif is_empty(section.text) and is_empty(subsection.text) and is_empty(paragraph.text):
                            txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:")
                            for subparagraph in paragraph.subparagraph:
                                txt.print(f">    {section.label}{subsection.label}{paragraph.label}{subparagraph.label} {subparagraph.text}")
                            txt.print()
                    else:
                        # split
                        for subparagraph in paragraph.subparagraph:

                            if not is_empty(section.text) and not is_empty(subsection.text) and not is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label} {section.text}\n> " +
                                    f"        {subsection.label} {subsection.text}\n> " +
                                    f"            {paragraph.label} {paragraph.text}\n> " + 
                                    f"                {subparagraph.label} {subparagraph.text}\n")
                            elif is_empty(section.text) and not is_empty(subsection.text) and not is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label}{subsection.label} {subsection.text}\n> " +
                                    f"        {paragraph.label} {paragraph.text}\n> " + 
                                    f"            {subparagraph.label} {subparagraph.text}\n")
                            elif not is_empty(section.text) and is_empty(subsection.text) and not is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label} {section.text}\n> " +
                                    f"        {subsection.label}{paragraph.label} {paragraph.text}\n> " + 
                                    f"            {subparagraph.label} {subparagraph.text}\n")
                            elif not is_empty(section.text) and not is_empty(subsection.text) and is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label} {section.text}\n> " +
                                    f"        {subsection.label} {subsection.text}\n> " +
                                    f"            {paragraph.label}{subparagraph.label} {subparagraph.text}\n")
                            elif is_empty(section.text) and is_empty(subsection.text) and not is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label}{subsection.label}{paragraph.label} {paragraph.text}\n> " + 
                                    f"        {subparagraph.label} {subparagraph.text}\n")
                            elif is_empty(section.text) and not is_empty(subsection.text) and is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label}{subsection.label} {subsection.text}\n> " +
                                    f"        {paragraph.label}{subparagraph.label} {subparagraph.text}\n")
                            elif not is_empty(section.text) and is_empty(subsection.text) and is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label} {section.text}\n> " +
                                    f"        {subsection.label}{paragraph.label}{subparagraph.label} {subparagraph.text}\n")
                            elif is_empty(section.text) and is_empty(subsection.text) and is_empty(paragraph.text):
                                txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                                    f"    {section.label}{subsection.label}{paragraph.label}{subparagraph.label} {subparagraph.text}\n")
                else:
                    if not is_empty(section.text) and not is_empty(subsection.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label} {subsection.text}\n> " +
                            f"            {paragraph.label} {paragraph.text}\n")
                    elif is_empty(section.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                            f"    {section.label}{subsection.label} {subsection.text}\n> " +
                            f"        {paragraph.label} {paragraph.text}\n")
                    elif is_empty(subsection.text):
                        txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                            f"    {section.label} {section.text}\n> " +
                            f"        {subsection.label}{paragraph.label} {paragraph.text}\n")
                    else:
                        txt.print(f"Section {section.label}, subsection {subsection.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                            f"    {section.label}{subsection.label}{paragraph.label} {paragraph.text}\n")
        else:
            if paragraph.repealed:
                txt.print(f"Section {section.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, was repealed: {paragraph.repealed}\n")
            else:
                if not is_empty(section.text):
                    txt.print(f"Section {section.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                        f"    {section.label} {section.text}\n> " +
                        f"        {paragraph.label} {paragraph.text}\n")
                else:
                    txt.print(f"Section {section.label}, paragraph {paragraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                        f"    {section.label}{paragraph.label} {paragraph.text}\n")
        return str(txt)

    def str_subparagraph(self, act:Act, section:Section, paragraph:Paragraph, subparagraph:Subparagraph) -> str:
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt = appender()
        if not is_empty(section.text) and not is_empty(paragraph.text):
            txt.print(f"Section {section.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                f"    {section.label} {section.text}\n> " +
                f"        {paragraph.label} {paragraph.text}\n> " + 
                f"            {subparagraph.label} {subparagraph.text}\n")
        elif is_empty(section.text):
            txt.print(f"Section {section.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                f"    {section.label}{paragraph.label} {paragraph.text}\n> " + 
                f"            {subparagraph.label} {subparagraph.text}\n")
        elif is_empty(paragraph.text):
            txt.print(f"Section {section.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                f"    {section.label} {section.text}\n> " +
                f"        {paragraph.label}{subparagraph.label} {subparagraph.text}\n")
        else:
            txt.print(f"Section {section.label}, paragraph {paragraph.label}, subparagraph {subparagraph.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                f"    {section.label}{paragraph.label}{subparagraph.label} {subparagraph.text}\n")
        return str(txt)

    def str_subsection(self, act:Act, section:Section, subsection:Subsection) -> str:
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt = appender()
        if subsection.repealed:
            txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}, was repealed: {subsection.repealed}\n")
        else:
            if not is_empty(section.text):
                txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                    f"    {section.label} {section.text}\n> " +
                    f"        {subsection.label} {subsection.text}\n")
            else:
                txt.print(f"Section {section.label}, subsection {subsection.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} states:\n> " +
                    f"    {section.label}{subsection.label} {subsection.text}\n")
        return str(txt)
    
    def str_schedule_form(self, act:Act, schedule:Schedule, part:FormSchedule) -> str:
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt = appender()
        txt.print()
        txt.print(f"{schedule.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} provides the following form:")
        txt.print()
        txt.print(f"Form Id: {part.form_label}")
        txt.print(f"Form Title: {part.form_title}")
        txt.print(f"Form Content:")
        txt.print(f"{part.form_content}")
        return str(txt)

    def str_schedule_provision(self, act:Act, schedule:Schedule, part:Provision) -> str:
        txt = appender()
        txt.print()
        txt.print(f"{part.text}")
        return str(txt)

    def str_schedule_table_group(self, act:Act, schedule:Schedule, part:TableGroup) -> str:
        txt = appender()
        for table in part.tables:
            txt.write(self.str_schedule_table_group_table(
                act=act,
                schedule=schedule,
                table_group=schedule,
                table=table))
        return str(txt)

    def str_schedule_table_group_table(self, act:Act, schedule:Schedule, table_group:TableGroup, table:TableGroupTable) -> str:
        txt = appender()
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt.write(self.str_h3(f"{table_group.label} of the {act.title}: {table.caption} - {table.title}"))

        txt.print()
        txt.print(f"{schedule.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by} provides the following table:")
        txt.print()
        txt.print(f"| {' | '.join(table.columns)} |")
        txt.print(f"| {' | '.join(['-' * len(col) for col in table.columns])} |")

        for row in table.rows:
            for j, entry in enumerate(row):
                txt.write(f"| {entry} ")
            txt.write(f"|\n")
        txt.print()
        return str(txt)

    def str_schedule_heading(self, act:Act, schedule:Schedule, part:Heading):
        txt = appender()
        txt.write(self.str_h3(f"{schedule.label} of the {act.title}: {part.heading_label}"))
        txt.print(f"{part.heading_title}")
        return str(txt)

    def str_schedule_bilingual_group(self, act:Act, schedule:Schedule, part:BilingualGroupSchedule):
        txt = appender()
        enacted_by = f" enactedby the \"{act.regulation_act}\"" if act.regulation_act else ""
        txt.write(self.str_h2(f"{schedule.label} of the {act.jurisdiction} \"{act.title}\"{enacted_by}"))

        txt.print("|        |")
        txt.print("| ------ |")
        for entry in part.items_en:
            txt.print(f"| {entry} |")
        return str(txt)

    def str_schedule(self, act:Act, schedule:Schedule):
        txt = appender()
        txt.write(self.str_h2(schedule.label))
        for part in schedule.parts:
            txt.write(self.str_schedule_part(act=act, schedule=schedule, part=part))
        return str(txt)

    def str_schedule_part(self, act:Act, schedule:Schedule, part:SchedulePart):
        if isinstance(part, BilingualGroupSchedule):
            return self.str_schedule_bilingual_group(act=act, schedule=schedule, part=part)
        elif isinstance(part,Heading):
            return self.str_schedule_heading(act=act, schedule=schedule, part=part)
        elif isinstance(part,TableGroup):
            return self.str_schedule_table_group(act=act, schedule=schedule, part=part)
        elif isinstance(part,FormSchedule):
            return self.str_schedule_form(act=act, schedule=schedule, part=part)
        elif isinstance(part,Provision):
            return self.str_schedule_provision(act=act, schedule=schedule, part=part)
        else:
            raise RuntimeError(f"unexpected schedule part in {act.title} under {schedule.label}: {part}")

class FederalXmlParser:
    def parse_provision(self, elem:ET.Element) -> Provision:
        return Provision(text=xml_to_text(elem))

    def parse_repealed(self, elem:ET.Element) -> Heading:
        return Heading(
            title="",
            heading_label="",
            heading_title=xml_to_text(elem)
            )

def xml_to_text(element):
    if element is None:
        return ""
    # Initialize text variable to hold the text of the current element
    text = element.text if element.text else ''
    if element.tag == "Leader" and element.get("leader") == "solid":
        text += "____________"
    if element.tag == "LeaderRightJustified" and element.get("leader") == "solid":
        text += "____________"
    if element.tag == "Label":
        text += " "
    
    # Iterate over child elements recursively
    for child in element:
        # Add text of child element and its descendants
        text += xml_to_text(child)

        # Add tail text of the child element
        if child.tail:
            text += child.tail

    return text


def fetch_and_parse_xml(url) -> ET.Element:
    try:
        # Fetch the XML document from the URL
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the XML document
            xml_tree = ET.fromstring(response.content)
            return xml_tree
        else:
            print("Failed to fetch XML document from the URL. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None


def process_document(url:str) -> Act:
    document = fetch_and_parse_xml(url)

    short_title_elem = document.find('Identification/ShortTitle') 
    long_title_element = document.find('Identification/LongTitle')
    chapter_element = document.find('Identification/Chapter')
    consolidation_elem = document.find('Identification/ConsolidationDate/Date')
    enabling_authority_elem = document.find('Identification/EnablingAuthority')
     
    if consolidation_elem is None:
        consolidation_elem = document.find('Identification/BillHistory/Stages[@stage="consolidation"]/Date')

    consolidation_date_yyyy = xml_to_text(consolidation_elem.find('YYYY'))
    consolidation_date_mm = xml_to_text(consolidation_elem.find('MM'))
    if len(consolidation_date_mm) == 1:
        consolidation_date_mm = "0" + consolidation_date_mm
    consolidation_date_dd = xml_to_text(consolidation_elem.find('DD'))
    if len(consolidation_date_dd) == 1:
        consolidation_date_dd = "0" + consolidation_date_dd
    consolidation_date = f"{consolidation_date_yyyy}-{consolidation_date_mm}-{consolidation_date_dd}"


    if chapter_element is None:
        chapter_element = document.find('Identification/InstrumentNumber')
        chapter = f"{xml_to_text(chapter_element)}"
    else:
        chapter = f"R.S.C., 1985, c. {xml_to_text(chapter_element)}"
        
    
    act:Act = Act(
        short_title=xml_to_text(short_title_elem),
        long_title=xml_to_text(long_title_element),
        chapter=chapter,
        consolidated=consolidation_date,
        regulation_act=xml_to_text(enabling_authority_elem).title()
        )

    title_elem = short_title_elem if short_title_elem is not None else long_title_element

    body = document.find('Body')
    for elem in body:
        if elem.tag == "Heading":
            heading = elem
        elif elem.tag == "Section":
            label = elem.find("Label")
            heading_elem = heading.find("TitleText")
            marginal_note_elem = elem.find("MarginalNote")

            section_text_elem = elem.find("Text")
            paragraph_elems = elem.findall("Paragraph")
            repealed_elem = section_text_elem.find("Repealed") if section_text_elem is not None else None
            subsection_elems = elem.findall("Subsection")
            definition_elems = elem.findall("Definition")

            section:Section = Section(
                label=xml_to_text(label),
                heading=xml_to_text(heading_elem),
                marginal_note=xml_to_text(marginal_note_elem),
                text=xml_to_text(section_text_elem)
            )
            act.add_section(section)

            if repealed_elem is not None:
                section.set_repealed(xml_to_text(repealed_elem))

            elif paragraph_elems is not None and len(paragraph_elems) > 0:
                for par in paragraph_elems:
                    par_repealed_elem = par.find("Repealed") if section_text_elem is not None else None
                    par_label = par.find("Label")
                    par_text_elem = par.find("Text")
                    paragraph:Paragraph = Paragraph(
                        label=xml_to_text(par_label),
                        text=xml_to_text(par_text_elem)
                        )
                    section.add_paragraph(paragraph)
                    if par_repealed_elem is not None:
                        paragraph.set_repealed(xml_to_text(par_repealed_elem))
                    else:
                        subpar_elems = par.findall("Subparagraph")
                        if subpar_elems is not None and len(subpar_elems) > 0:
                            for subpar_elem in subpar_elems:
                                subpar_label_elem = subpar_elem.find("Label")
                                subpar_text_elem = subpar_elem.find("Text")
                                subparagraph:Subparagraph = Subparagraph(
                                    label=xml_to_text(subpar_label_elem), 
                                    text=xml_to_text(subpar_text_elem)
                                    )
                                paragraph.add_subparagraph(subparagraph)
            elif subsection_elems is not None and len(subsection_elems) > 0:
                for subsect in subsection_elems:
                    subsect_repealed_elem = subsect.find("Repealed") if section_text_elem is not None else None
                    subsect_label = subsect.find("Label")
                    subsect_text_elem = subsect.find("Text")
                    subsection:Subsection = Subsection(
                        label=xml_to_text(subsect_label),
                        text=xml_to_text(subsect_text_elem)
                    )
                    section.add_subsection(subsection)
                    if subsect_repealed_elem is not None:
                        subsection.set_repealed(xml_to_text(subsect_repealed_elem))

                    subsect_paragraph_elems = subsect.findall("Paragraph")
                    if subsect_paragraph_elems is not None and len(subsect_paragraph_elems) > 0:
                        for par in subsect_paragraph_elems:
                            par_repealed_elem = par.find("Repealed") if section_text_elem is not None else None
                            par_label = par.find("Label")
                            par_text_elem = par.find("Text")

                            paragraph:Paragraph = Paragraph(
                                label=xml_to_text(par_label),
                                text=xml_to_text(par_text_elem)
                            )
                            subsection.add_paragraph(paragraph)

                            if par_repealed_elem is not None:
                                paragraph.set_repealed(xml_to_text(par_repealed_elem))
                            else:
                                subpar_elems = par.findall("Subparagraph")
                                if subpar_elems is not None and len(subpar_elems) > 0:
                                    for subpar_elem in subpar_elems:
                                        subpar_label_elem = subpar_elem.find("Label")
                                        subpar_text_elem = subpar_elem.find("Text")
                                        subparagraph:Subparagraph = Subparagraph(
                                            label=xml_to_text(subpar_label_elem),
                                            text=xml_to_text(subpar_text_elem)
                                        )
                                        paragraph.add_subparagraph(subparagraph)
                    definition_elems = subsect.findall("Definition")
                    if definition_elems is not None and len(definition_elems) > 0:
                        for definition_elem in definition_elems:
                            text_elem = definition_elem.find("Text")
                            def_repealed_elem = text_elem.find("Repealed") if section_text_elem is not None else None
                            term_en_elem = text_elem.find("DefinedTermEn")
                            term_fr_elem = text_elem.find("DefinedTermFr")

                            definition:Definition = Definition(
                                term_en=xml_to_text(term_en_elem),
                                term_fr=xml_to_text(term_fr_elem),
                                text=xml_to_text(text_elem)
                            )
                            subsection.add_definition(definition)

                            if def_repealed_elem is not None:
                                definition.set_repealed(xml_to_text(def_repealed_elem))
                            else:
                                par_definition_elems = definition_elem.findall("Paragraph")
                                if par_definition_elems is not None and len(par_definition_elems) > 0:
                                    for par_definition_elem in par_definition_elems:
                                        par_label_elem = par_definition_elem.find("Label")
                                        spar_text_elem = par_definition_elem.find("Text")
                                        paragraph:Paragraph = Paragraph(
                                            label=xml_to_text(par_label_elem),
                                            text=xml_to_text(spar_text_elem)
                                        )
                                        definition.add_paragraph(paragraph)
            elif definition_elems is not None and len(definition_elems) > 0:
                for definition_elem in definition_elems:
                    text_elem = definition_elem.find("Text")
                    def_repealed_elem = text_elem.find("Repealed") if section_text_elem is not None else None
                    term_en_elem = text_elem.find("DefinedTermEn")
                    term_fr_elem = text_elem.find("DefinedTermFr")

                    definition:Definition = Definition(
                        term_en=xml_to_text(term_en_elem),
                        term_fr=xml_to_text(term_fr_elem),
                        text=xml_to_text(text_elem)
                    )
                    section.add_definition(definition)

                    if def_repealed_elem is not None:
                        definition.set_repealed(xml_to_text(def_repealed_elem))
                    else:
                        par_definition_elems = definition_elem.findall("Paragraph")
                        if par_definition_elems is not None and len(par_definition_elems) > 0:
                            for par_definition_elem in par_definition_elems:
                                par_label_elem = par_definition_elem.find("Label")
                                spar_text_elem = par_definition_elem.find("Text")
                                paragraph:Paragraph = Paragraph(
                                    label=xml_to_text(par_label_elem),
                                    text=xml_to_text(spar_text_elem)
                                )
                                definition.add_paragraph(paragraph)

    for schedule_elem in document.findall('Schedule'):
        label_elem = schedule_elem.find("ScheduleFormHeading/Label")
        titletext_elem = schedule_elem.find("ScheduleFormHeading/TitleText")
        schedule:Schedule = Schedule(label=xml_to_text(label_elem))
        act.add_schedule(schedule)

        if label_elem is None:
            label_elem = titletext_elem
            titletext_elem = ""
        
        for elem in schedule_elem:
            if elem.tag == "ScheduleFormHeading":
                continue
            elif elem.tag == "RegulationPiece":
                # todo maybe
                continue
            elif elem.tag == "HistoricalNote":
                continue
            elif elem.tag == "FormGroup":
                form_label_elem = elem.find("ScheduleFormHeading/Label")
                form_title_elem = elem.find("ScheduleFormHeading/TitleText")

                def print_form_content(elem, indent):
                    str = ""
                    for form_elem in elem:
                        if form_elem.tag == "Provision":
                            str += print_form_content(form_elem, indent + 1)
                        elif form_elem.tag == "Label":
                            str += f"\n{'  ' * indent}{xml_to_text(form_elem)} " + print_form_content(form_elem, indent)
                        elif form_elem.tag == "Text":
                            str += f"{xml_to_text(form_elem)} " + print_form_content(form_elem, indent) + f"\n{'  ' * indent}"
                    return str

                form_content_schedule:FormSchedule = FormSchedule(
                    title=xml_to_text(title_elem),
                    form_label=xml_to_text(form_label_elem),
                    form_title=xml_to_text(form_title_elem),
                    form_content=print_form_content(elem, 1)
                )
                schedule.add_part(form_content_schedule)
                continue
            elif elem.tag == "TableGroup":
                caption_text = ""
                caption_elem = None
                table_group_schedule:TableGroup = TableGroup(
                    label=xml_to_text(label_elem),
                    title=xml_to_text(title_elem),
                )
                schedule.add_part(table_group_schedule)

                for table_elem in elem:
                    if table_elem.tag == "Caption":
                        caption_elem = table_elem
                        caption_text = f" with caption \"{xml_to_text(caption_elem)}\""
                    elif table_elem.tag == "table":
                        table_title_elem = table_elem.find("title")
                        if table_title_elem is None:
                            table_title_elem = titletext_elem

                        if not is_empty(xml_to_text(table_title_elem)):
                            table_title = f", titled \"{xml_to_text(table_title_elem)}\""
                        else:
                            table_title = ""
                        
                        table_group_schedule_table:TableGroupTable = TableGroupTable(
                            caption=xml_to_text(caption_elem),
                            title=xml_to_text(table_title_elem)
                        )
                        table_group_schedule.add_table(table_group_schedule_table)

                        table_group_elems = table_elem.findall("tgroup")
                        for table_group_elem in table_group_elems:
                            thead_elem = table_group_elem.find("thead")
                            if thead_elem:
                                thead_row_elems = thead_elem .findall("row")
                                cols = [''] * len(thead_row_elems[0])
                                for i, thead_row_elem in enumerate(thead_row_elems):
                                    for j, thead_row_entry_elem in enumerate(thead_row_elem.findall("entry")):
                                        if is_empty(cols[j]):
                                            cols[j] = xml_to_text(thead_row_entry_elem)
                                        else:
                                            cols[j] = f"{cols[j]} - {xml_to_text(thead_row_entry_elem)}"
                            else:
                                tbody_elem = table_group_elem.find("tbody")
                                tbody_row_elems = tbody_elem.findall("row")
                                cols = [''] * len(tbody_row_elems[0])
                                for i in range(0, len(cols)):
                                    cols[i] = f"Column {i+1}"
                            table_group_schedule_table.set_columns(cols)
                            

                            tbody_elem = table_group_elem.find("tbody")
                            tbody_row_elems = tbody_elem.findall("row")
                            i = 0
                            entries = [''] * len(cols)
                            vspan = [0] * len(cols)
                            headers = [{} for i in range(0, len(cols))]
                            while i < len(tbody_row_elems):
                                for vsi in range(0, len(vspan)):
                                    vspan[vsi] = vspan[vsi] - 1

                                tbody_row_elem = tbody_row_elems[i]
                                entry_elems = tbody_row_elem.findall("entry")
                                has_more_rows = False
                                is_header = False
                                if len(entry_elems) == len(cols):
                                    entries = [''] * len(cols)
                                    for j, tbody_row_entry_elem in enumerate(tbody_row_elem.findall("entry")):
                                        colname = tbody_row_entry_elem.get("colname")
                                        has_more_rows = has_more_rows or (tbody_row_entry_elem.get("morerows") is not None and tbody_row_entry_elem.get("morerows") != 0)
                                        is_header = is_header or (tbody_row_entry_elem.get("th-id") is not None and not is_empty(tbody_row_entry_elem.get("th-id")))

                                        if colname is not None:
                                            index = int(colname) - 1
                                        else:
                                            index = j

                                        if tbody_row_entry_elem.get("morerows") is not None:
                                            vspan[index] = int(tbody_row_entry_elem.get("morerows"))
                                        else:
                                            vspan[index] = 0

                                        if tbody_row_entry_elem.get("th-id") is not None:
                                            headers[index][tbody_row_entry_elem.get("th-id")] = xml_to_text(tbody_row_entry_elem)
                                        else:
                                            headers[index][""] = xml_to_text(tbody_row_entry_elem)

                                        entries[index] = xml_to_text(tbody_row_entry_elem)

                                    if is_header == False:
                                        table_group_schedule_table.add_row(entries)
                                else:
                                    full_text = [''] * len(cols)
                                    for j in range(0, len(cols)):
                                        if vspan[j] >= 0:
                                            full_text[j] = entries[j]
                                    for j, tbody_row_entry_elem in enumerate(tbody_row_elem.findall("entry")):
                                        colname = tbody_row_entry_elem.get("colname")
                                        has_more_rows = has_more_rows or (tbody_row_entry_elem.get("morerows") is not None and tbody_row_entry_elem.get("morerows") != 0)
                                        is_header = is_header or (tbody_row_entry_elem.get("th-id") is not None and not is_empty(tbody_row_entry_elem.get("th-id")))

                                        if colname is not None:
                                            index = int(colname) - 1
                                        else:
                                            index = 0
                                            while index < len(cols) and vspan[index] >= 0:
                                                index = index + 1
                                            for k in range(0, j):
                                                index = index + 1
                                                while index < len(cols) and vspan[index] >= 0:
                                                    index = index + 1

                                        if tbody_row_entry_elem.get("th-id") is not None:
                                            headers[index][tbody_row_entry_elem.get("th-id")] = xml_to_text(tbody_row_entry_elem)
                                        else:
                                            headers[index][""] = xml_to_text(tbody_row_entry_elem)

                                        if tbody_row_entry_elem.get("th-headers") is not None:
                                            for part in tbody_row_entry_elem.get("th-headers").split():
                                                if is_empty(full_text[index]):
                                                    if part in headers[index]:
                                                        full_text[index] = f"{headers[index][part]}"
                                                    else:
                                                        full_text[index] = f""
                                                else:
                                                    if part in headers[index]:
                                                        full_text[index] = f"{headers[index][part]} {full_text[index]}"
                                                    else:
                                                        full_text[index] = f"{full_text[index]}"
                                            if is_empty(full_text[index]):
                                                full_text[index] = f"{xml_to_text(tbody_row_entry_elem)}"
                                            else:
                                                full_text[index] = f"{full_text[index]} {xml_to_text(tbody_row_entry_elem)}"
                                        else:
                                            full_text[index] = xml_to_text(tbody_row_entry_elem)

                                    if is_header == False:
                                        table_group_schedule_table.add_row(full_text)
                                i = i+1
                continue
            elif elem.tag == "Heading":
                heading_label_elem = elem.find("Label")
                heading_title_elem = elem.find("TitleText")
                heading_schedule:Heading = Heading(
                    title=xml_to_text(title_elem),
                    heading_label=xml_to_text(heading_label_elem),
                    heading_title=xml_to_text(heading_title_elem),
                )
                schedule.add_part(heading_schedule)
                continue

            elif elem.tag == "BilingualGroup":
                bilingual_group:BilingualGroupSchedule = BilingualGroupSchedule(
                    items_en=[xml_to_text(entry) for entry in elem.findall('BilingualItemEn')],
                    items_fr=[xml_to_text(entry) for entry in elem.findall('BilingualItemFr')],
                )
                schedule.add_part(bilingual_group)
                continue
            elif elem.tag == "BillPiece":
                continue
            elif elem.tag == "Provision":
                provision = FederalXmlParser().parse_provision(elem)
                schedule.add_part(provision)
            elif elem.tag == "Repealed":
                provision = FederalXmlParser().parse_repealed(elem)
                schedule.add_part(provision)
            else:
                raise RuntimeError(f"Unexepected tag: {elem.tag} while parsing {act.title}")
    return act

def change_extension(filename, newext):
    import os
    base_name, _ = os.path.splitext(filename)
    return base_name + f".{newext}"

