import sys
def main(filename):
    import json
    exports = {}
    selectors = {}
    modules = {}
    import re
    from pathlib import Path
    from bs4 import BeautifulSoup
    import sys

    node_modules_folder = r"/mnt/c/Users/yorke/Documents/GitHub/Orbital/src/orbital-designer/node_modules/"
    source_folder = r"/mnt/c/Users/yorke/Documents/GitHub/Orbital/src/orbital-designer/src"
    for a_file in Path(node_modules_folder).rglob("index.metadata.json"):
        try:
            with open(a_file) as outfile:
                data = json.load(outfile)
                component_name = None
                
                for aModule in data['metadata'].keys():
                    try:
                        exports[aModule] = [theItem['name'] for theItem in data['metadata'][aModule]['decorators'][0]['arguments'][0]['exports']]
                    except KeyError:
                        pass
                    try:
                        selectors[aModule] = [theItem.strip() for theItem in data['metadata'][aModule]['decorators'][0]['arguments'][0]['selector'].split(",")]
                    except KeyError:
                        pass
                    try:
                        if (data['metadata'][aModule]['decorators'][0]['expression']['name'] == "NgModule"):
                            modules[aModule] = []
                            component_name = aModule
                        else:
                            modules[component_name].append(aModule)
                    except KeyError:
                        pass
        except:
            pass

    def extract_selector(selectors, exports, selector_to_lookup):
        for selector in selectors.keys():
            if (selector_to_lookup in selectors[selector]):
                for export in exports.keys():
                    if (selector in exports[export]):
                        return export

    def get_local_selector(test_str):
        regex = r"selector: '(.\S+)',"
        matches = re.finditer(regex, test_str, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                return match.group(groupNum)

    def get_local_class(test_str):
        regex = r"export class (.\S+)"
        matches = re.finditer(regex, test_str, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                return match.group(groupNum)

    local_selectors = {}
    local_selectors_file_names = {}
    for a_file in Path(source_folder).rglob("*.ts"):
        with open(a_file, 'r') as outfile:
            file_content = outfile.read()
            if (get_local_class(file_content) is not None and get_local_selector(file_content) is not None):
                local_selectors[get_local_selector(file_content)] = get_local_class(file_content)
                local_selectors_file_names[get_local_selector(file_content)] = a_file


    def extract_all_selectors(filePath):
        selectors_to_use = []
        source_code = None
        with open(filePath, 'r') as file:
            source_code = file.read()

        soup = BeautifulSoup(source_code, features="html.parser")

        for tag in soup.findChildren():
            tmp = extract_selector(selectors, exports, tag.name)
            if tmp is not None:
                selectors_to_use.append(tmp)

        for tag in soup.findChildren():
            for attr in tag.attrs.keys():
                # TODO: hack, automatically import ngmodel using heuristics
                if (str(attr) == "[(ngmodel)]"):
                    tmp = ["FormsModule", "BrowserModule"]
                    # do something
                else:
                    tmp = extract_selector(selectors, exports, attr)
                if tmp is not None:
                    selectors_to_use.extend(tmp)
        return soup, selectors_to_use

    declarations_to_use = []

    def run(filename):
        soup, selectors_to_use = extract_all_selectors(filename)
        for tag in soup.findChildren():
            if tag.name in local_selectors:
                declarations_to_use.append(local_selectors[tag.name])
                tmp, useful = extract_all_selectors(str(local_selectors_file_names[tag.name]).replace(".ts", ".html"))
                selectors_to_use.extend(useful)
        return selectors_to_use

    selectors_to_use = run(filename)

    return (list(set(selectors_to_use)), list(set(declarations_to_use)), local_selectors_file_names)
selectors_to_use, declarations_to_use, selectors_file_names = main(sys.argv[1])

from stringcase import pascalcase, snakecase, spinalcase
final_selectors = selectors_to_use
final_declarations = declarations_to_use
def extract_selectors(declarations_to_use, selectors_file_names):
    for a_declaration in declarations_to_use:
        selector = 'app-' + spinalcase(a_declaration.replace("Component", ""))
        filename_for_selector = str(selectors_file_names[selector])
        new_selectors_to_use, new_declarations_to_use, new_selectors_filenames = main(filename_for_selector.replace(".ts", ".html"))
        final_selectors.extend(new_selectors_to_use)
        final_declarations.extend(new_declarations_to_use)
        extract_selectors(new_declarations_to_use, new_selectors_filenames)

extract_selectors(declarations_to_use, selectors_file_names)
# TODO: hack, not all components will use the app-component-name -> ComponentName syntax
print(list(set(final_selectors)))
print("=======")
print(list(set(final_declarations)))
