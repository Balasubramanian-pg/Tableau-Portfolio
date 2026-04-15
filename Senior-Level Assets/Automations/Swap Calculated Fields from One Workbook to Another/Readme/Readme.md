# What this code does?

## IMPORTS (Lines 1–7)

```python
import os
```
Gives access to file system operations — creating folders, joining paths, checking if files exist.

```python
import re
```
Regular expressions. Used specifically to scan formula strings for `[bracketed references]` to find parameter dependencies.

```python
import copy
```
Used for `copy.deepcopy()` — when we copy an XML element, we need a fully independent clone. Without this, modifying the copy would modify the original too, because Python passes objects by reference.

```python
import zipfile
```
`.twbx` files are literally ZIP archives. This library lets us unzip them to get the `.twb` inside, and rezip them after we're done editing.

```python
import shutil
```
Higher-level file operations — copying files, deleting entire directories recursively.

```python
import xml.etree.ElementTree as ET
```
Python's built-in XML parser. The entire `.twb` file is XML, so every read, search, and write goes through this. We alias it `ET` to avoid typing the full name every time.

```python
from datetime import datetime
```
Used only for generating timestamps in backup filenames so you never accidentally overwrite a previous backup.

## CONFIGURATION (Lines 14–24)

```python
SOURCE_TWBX = r"C:\Users\..."
```
The workbook you're copying calculated fields **from**. The `r` prefix means raw string — backslashes are treated literally, not as escape characters. Without `r`, `\U` would be interpreted as a Unicode escape and crash.

```python
DEST_TWBX = r"C:\Users\..."
```
The workbook you're copying calculated fields **into**. This file gets modified. Everything else in it is preserved.

```python
WORK_DIR = "temp_tableau_processing"
```
A temporary folder created at runtime. Both workbooks get unzipped into subdirectories here (`temp_tableau_processing/source/` and `temp_tableau_processing/dest/`). Deleted and recreated fresh on every run.

```python
BACKUP_DIR = "backup"
```
Where backup copies of the destination workbook are saved before any modifications are made. Your safety net.

```python
FIELD_MAPPING = {
    "Reimbursed Dollars": "Approval Rate",
    "reimbursed_dollars": "approval_rate"
}
```
A dictionary of text substitutions applied to every formula being copied. Key = what to find, Value = what to replace it with. Used when the field names differ between the two workbooks. If you don't need any substitutions, leave it as an empty dict `{}`.

## UTILITY FUNCTIONS (Lines 31–72)

### `create_backup` (Line 31)
```python
def create_backup(file_path, label="backup"):
```
Takes the file path to back up and an optional label string (we pass `"dest"` so backup filenames are clearly identifiable).

```python
    os.makedirs(BACKUP_DIR, exist_ok=True)
```
Creates the `backup/` folder if it doesn't exist. `exist_ok=True` means it won't throw an error if the folder is already there.

```python
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
```
Generates a string like `20260325_143022` — year, month, day, hour, minute, second. This makes every backup uniquely named.

```python
    filename = os.path.basename(file_path).replace(".twbx", "")
```
`os.path.basename` strips the directory path, leaving just the filename. `.replace(".twbx", "")` removes the extension so we can rebuild the name cleanly.

```python
    backup_path = os.path.join(BACKUP_DIR, f"{label}_{filename}_{timestamp}.twbx")
```
Constructs a full path like `backup/dest_HCP Claims 1_20260325_143022.twbx`.

```python
    shutil.copy(file_path, backup_path)
```
Actually copies the file. Everything above was just preparing the destination path.

---

### `unzip_twbx` (Line 41)
```python
def unzip_twbx(twbx_path, extract_to):
```
Takes a `.twbx` path and a folder to extract into.

```python
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
```
If the temp folder already exists from a previous run, delete it entirely. This prevents stale files from a previous run mixing with the current one.

```python
    os.makedirs(extract_to)
```
Create the fresh empty extraction folder.

```python
    with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
```
Opens the `.twbx` as a ZIP file in read mode (`'r'`) and extracts everything into the target folder. The `.twbx` contains a `.twb` file (the actual XML workbook) and optionally a `Data/` folder with extracts.

```python
    for file in os.listdir(extract_to):
        if file.endswith(".twb"):
            return os.path.join(extract_to, file)
```
Scans the extracted contents, finds the `.twb` file, and returns its full path. That's what the rest of the code actually parses.

```python
    raise Exception("[ERROR] No TWB file found inside TWBX")
```
If somehow no `.twb` is found (corrupted archive, wrong file type), crash immediately with a clear message rather than silently failing later.

---

### `repack_twbx` (Line 53)
```python
def repack_twbx(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
```
Creates a new ZIP file at `output_path` in write mode. `ZIP_DEFLATED` means compress the contents (as opposed to `ZIP_STORED` which is no compression).

```python
        for root_dir, _, files in os.walk(folder_path):
```
`os.walk` recursively traverses the entire folder tree. `root_dir` is the current directory being walked, `_` is subdirectories (we don't need those directly), `files` is the list of files in that directory.

```python
            for file in files:
                full_path = os.path.join(root_dir, file)
                rel_path  = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, rel_path)
```
For each file found: `full_path` is the absolute path on disk. `rel_path` is the path relative to the extraction root — this is critical because ZIP archives store relative paths. Without this, the archive would store `C:\Users\...\temp_tableau_processing\dest\file.twb` instead of just `file.twb`, and Tableau wouldn't be able to open it.

---

### `deep_copy` (Line 63)
```python
def deep_copy(element):
    return copy.deepcopy(element)
```
A thin wrapper around Python's `copy.deepcopy`. When we copy an XML element from source to destination, we need a completely independent copy — not a reference to the same object. If we used a reference, modifying the element in destination would also modify it in source. `deepcopy` recursively copies the element and all its children, attributes, and text.

---

### `mapping_replace` (Line 67)
```python
def mapping_replace(text, mapping):
    if not text:
        return text
```
Guard clause — if the formula is `None` or empty string, return it as-is immediately. Avoids calling `.replace()` on None which would crash.

```python
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text
```
Iterates over every key-value pair in `FIELD_MAPPING` and applies each substitution to the formula string sequentially. Simple string replacement — no regex here (which means it will do partial matches; worth keeping in mind if field names are substrings of each other).

---

## DATASOURCE HELPERS (Lines 79–151)

### `get_parameters_datasource` (Line 79)
```python
def get_parameters_datasource(root):
    for ds in root.findall(".//datasource"):
        if ds.attrib.get("name", "").lower() == "parameters":
            return ds
    return None
```
Tableau's XML always has a special datasource named literally `"Parameters"` that stores all parameter definitions. This function finds and returns it. `.lower()` handles case inconsistencies. Returns `None` if it doesn't exist — callers check for this.

---

### `get_real_datasources` (Line 87)
```python
def get_real_datasources(root):
    return [
        ds for ds in root.findall(".//datasource")
        if ds.attrib.get("name", "").lower() != "parameters"
    ]
```
List comprehension that returns every datasource **except** the Parameters one. This is the fix for the original bug where we were accidentally inserting calculated fields into the Parameters datasource (which Tableau ignores for rendering). `.//datasource` means "find all `datasource` elements anywhere in the XML tree".

---

### `print_datasources` (Line 95)
```python
def print_datasources(root, label=""):
```
A debug/logging function. Every time it's called it prints a summary of all datasources in a workbook — name, caption, and how many calculated fields each one has. Helps you verify that the right datasource is being targeted before and after operations.

```python
    calc_count = sum(1 for col in ds.findall("column") if col.find("calculation") is not None)
```
Counts only direct `<column>` children (not nested ones) that have a `<calculation>` child element. The `sum(1 for ...)` pattern is a memory-efficient way to count items matching a condition in a generator.

---

### `find_column_insert_position` (Line 105)
This function exists because of one of our earlier crashes — Tableau enforces a strict order of child elements inside `<datasource>`. You cannot just `append()` to the end.

```python
    children = list(datasource)
```
Converts the datasource element's children into a plain Python list so we can enumerate with an index.

```python
    last_col_idx = None
    for i, child in enumerate(children):
        if child.tag == "column":
            last_col_idx = i
```
Walks through all children tracking the index of the last `<column>` element found. After the loop, `last_col_idx` holds the position of the last existing column.

```python
    if last_col_idx is not None:
        return last_col_idx + 1
```
Insert position is one after the last column — so our new column gets appended right after all existing columns, before `<folders-common>`, `<actions>`, `<filter>` etc.

```python
    for i, child in enumerate(children):
        if child.tag == "connection":
            return i + 1
    return 0
```
Fallback for datasources with no columns yet — insert after `<connection>` if it exists, otherwise at position 0 (top of the datasource).

---

### `find_folders_insert_position` (Line 124)
Same concept but for the `<folders-common>` block specifically.

```python
    insert_after_tags = {"column", "column-instance", "group", "aliases"}
    insert_before_tags = {"actions", "filter", "layout", "style", ...}
```
Two sets that define the schema boundary. `folders-common` must go after all column/group/alias elements, but before actions/filters/layout.

```python
    last_valid = 0
    for i, child in enumerate(children):
        if child.tag in insert_after_tags:
            last_valid = i + 1      # Keep pushing the boundary forward
        if child.tag in insert_before_tags:
            return last_valid       # Hit a "must come after" tag — stop here
    return last_valid
```
Scans children left to right. Every time we see an `insert_after_tags` element, we update `last_valid` to be right after it. The moment we see an `insert_before_tags` element, we've gone too far — return the last safe position. If we never hit a boundary tag, return whatever the last valid position was.

---

### `get_existing_column_names` (Line 145)
```python
def get_existing_column_names(ds_element):
    names = set()
    for col in ds_element.findall("column"):   # Direct children only
        n = col.attrib.get("name")
        if n:
            names.add(n)
    return names
```
Returns a Python `set` of all `name` attribute values for `<column>` direct children of a datasource. Used to check for duplicates before inserting. We use a `set` (not a list) because membership check `if x in set` is O(1) vs O(n) for a list — doesn't matter at this scale but it's the right instinct. Note `findall("column")` with no `//` prefix — only direct children, not nested ones inside connections.

---

## PARAMETER HANDLING (Lines 158–264)

### `extract_referenced_parameter_names` (Line 158)
```python
def extract_referenced_parameter_names(formula):
    return set(re.findall(r'\[([^\]]+)\]', formula or ""))
```
This regex `\[([^\]]+)\]` breaks down as:
- `\[` — literal opening bracket
- `([^\]]+)` — capture group: one or more characters that are NOT a closing bracket
- `\]` — literal closing bracket

So given a formula like `IF [Time Granularity] = "week" THEN [Claim Date] END`, it returns `{'Time Granularity', 'Claim Date'}`. This catches every bracketed reference — parameters AND regular fields. The caller then checks which ones are actually parameters.

---

### `extract_parameters` (Line 166)
```python
    params[name]    = col   # e.g. "[Parameter 1]" → element
    params[caption] = col   # e.g. "Time Granularity" → element
```
Stores each parameter under two keys — its internal `name` (bracket format like `[Parameter 1]`) AND its `caption` (human readable like `"Time Granularity"`). This double-indexing is deliberate: formulas reference parameters by caption in brackets like `[Time Granularity]`, but the XML stores them by internal name. By indexing both ways we can look up a match regardless of which format the formula uses.

---

### `copy_required_parameters` (Line 192)
```python
    all_referenced = set()
    for calc in calculations:
        el      = calc["element"]
        calc_el = el.find("calculation")
        if calc_el is not None:
            formula = calc_el.attrib.get("formula", "")
            all_referenced |= extract_referenced_parameter_names(formula)
```
Loops through every calculated field being copied. For each one, digs into its `<calculation>` child element, extracts the formula string, runs the regex on it, and unions (`|=`) the results into `all_referenced`. After this loop, `all_referenced` contains every single bracketed name mentioned across all formulas.

```python
    source_params_ds = get_parameters_datasource(source_root)
```
Re-parses the source TWB to get the Parameters datasource. We do this separately from the main extraction because parameters live in a different datasource than the calculated fields.

```python
    dest_params_ds = get_parameters_datasource(dest_root)
    if dest_params_ds is None:
        dest_params_ds = ET.Element("datasource", {"name": "Parameters", "inline": "true"})
        dest_root.find(".//datasources").insert(0, dest_params_ds)
```
If the destination has no Parameters datasource at all (unlikely but possible), creates one from scratch and inserts it at position 0 inside the `<datasources>` container — which is where Tableau expects it.

```python
    matched_col = source_param_map.get(bracketed) or source_param_map.get(ref)
    if matched_col is None:
        continue   # Not a parameter — just a regular field reference
```
For each reference found in formulas, tries to look it up first as `[ref]` (bracketed format) then as `ref` (plain). If neither matches anything in the Parameters datasource, it's just a regular field reference — skip it, don't try to copy anything.

```python
    new_param = deep_copy(matched_col)
    insert_pos = find_column_insert_position(dest_params_ds)
    dest_params_ds.insert(insert_pos, new_param)
```
Deep copies the parameter element from source and inserts it into the destination's Parameters datasource at the correct position.

```python
    dest_tree.write(dest_twb_path, encoding="utf-8", xml_declaration=True)
```
Writes the modified tree back to disk. This is critical — `copy_required_parameters` runs before `insert_calculations`, so the parameters must be persisted to disk before the next step re-parses the file.

---

## FOLDER HANDLING (Lines 293–360)

### `extract_folders` (Line 293)
```python
    for ds in get_real_datasources(root):
        ds_name = ds.attrib.get("name", "")
        folders = ds.find("folders-common")
        result[ds_name] = folders
```
For each real datasource, looks for a direct child element called `<folders-common>`. This is the block that controls the folder organization in Tableau's data pane. Stores it in a dict keyed by datasource name. If a datasource has no folders, `folders` is `None` and that's stored too — the caller handles `None` gracefully.

---

### `merge_folders` (Line 302)
```python
    target_ds = dest_ds_map.get(source_ds_name) or real_dest_datasources[0]
```
Tries to match the source datasource by name in the destination. Falls back to the first real destination datasource if no name match is found. The `or` means: "if `.get()` returns `None` (key not found), use `real_dest_datasources[0]` instead".

```python
    if dest_folders is None:
        new_folders = deep_copy(source_folders)
        insert_pos  = find_folders_insert_position(target_ds)
        target_ds.insert(insert_pos, new_folders)
```
Clean case — destination has no folders at all. Deep copy the entire source `<folders-common>` block and insert it at the correct schema position.

```python
    else:
        dest_folder_map = {
            f.attrib.get("name", ""): f
            for f in dest_folders.findall("folder")
        }
```
Destination already has folders. Build a lookup dict of existing folder elements by name.

```python
        for src_folder in source_folders.findall("folder"):
            folder_name = src_folder.attrib.get("name", "")
            if folder_name not in dest_folder_map:
                dest_folders.append(deep_copy(src_folder))
```
For each folder in source: if it doesn't exist in destination, append it wholesale.

```python
            else:
                dest_folder = dest_folder_map[folder_name]
                existing_items = {fi.attrib.get("name","") for fi in dest_folder.findall("folder-item")}
                for item in src_folder.findall("folder-item"):
                    if item.attrib.get("name","") not in existing_items:
                        dest_folder.append(deep_copy(item))
```
If the folder already exists, merge at the `<folder-item>` level. Each `<folder-item>` references a field by its internal `name`. Only add items that don't already exist in the destination folder.

```python
        target_ds.remove(dest_folders)
        insert_pos = find_folders_insert_position(target_ds)
        target_ds.insert(insert_pos, dest_folders)
```
After merging, remove the `<folders-common>` block from wherever it was and re-insert it at the mathematically correct schema position. This is the fix that makes folders actually stick — without this, if the block was misplaced in the original XML, it stays misplaced after merging.

---

## GROUP BY FOLDER (Lines 367–399)

### `set_group_by_folder` (Line 367)
```python
    workbook_el = dest_root   # In a TWB, the root element IS the <workbook>
```
The root of the parsed XML tree is the `<workbook>` element itself.

```python
    prefs = workbook_el.find("preferences")
    if prefs is None:
        prefs = ET.Element("preferences")
        workbook_el.insert(0, prefs)
```
Looks for an existing `<preferences>` block. If none exists, creates one and inserts it at position 0 inside the workbook element.

```python
    existing_pref_names = {p.attrib.get("name", "") for p in prefs.findall("preference")}
    if "ui.groupby" not in existing_pref_names:
        ET.SubElement(prefs, "preference", {"name": "ui.groupby", "value": "folders"})
```
Checks if `ui.groupby` preference already exists. If not, creates a `<preference name="ui.groupby" value="folders"/>` child element inside `<preferences>`. This is what tells Tableau to default to the folder view when the workbook opens.

```python
    else:
        for p in prefs.findall("preference"):
            if p.attrib.get("name") == "ui.groupby":
                p.set("value", "folders")
```
If the preference already exists (maybe set to `"datasource"`), just update its value to `"folders"`.

---

## CORE EXTRACTION & INSERTION (Lines 406–475)

### `extract_calculated_fields` (Line 406)
```python
    for ds in get_real_datasources(root):
        ds_name = ds.attrib.get("name", "")
        for column in ds.findall("column"):        # Direct children only
            if column.find("calculation") is not None:
```
For every real datasource, iterates over its direct `<column>` children only. The presence of a `<calculation>` child is what distinguishes a calculated field from a regular data source column.

```python
                caption = column.attrib.get("caption", column.attrib.get("name", ""))
```
Gets the `caption` (display name). Falls back to `name` (internal ID) if caption is missing. This fallback matters because some calcs don't have a separate caption if the display name matches the internal name.

```python
                calculations.append({
                    "element"  : column,     # The actual XML element for deep copy later
                    "name"     : ...,
                    "caption"  : ...,
                    "source_ds": ds_name
                })
```
Stores the raw XML element itself (not a copy) — we copy it at insert time. Also stores which datasource it came from so we can target the correct datasource in destination.

---

### `insert_calculations` (Line 431)
```python
    dest_ds_map = {ds.attrib.get("name", ""): ds for ds in real_datasources}
```
Dictionary comprehension — builds a lookup of `{ datasource_name → datasource_element }` so we can find the right target datasource in O(1) instead of looping every time.

```python
    target_ds = dest_ds_map.get(source_ds) or real_datasources[0]
```
Single line that handles both cases: exact name match (uses it) or no match (falls back to first real datasource). The `or` short-circuits — Python only evaluates the right side if the left side is falsy (i.e., `None`).

```python
    if field_name in get_existing_column_names(target_ds):
        skipped += 1
        continue
```
Duplicate guard. If a column with this internal name already exists in the target datasource, skip it entirely. `continue` jumps to the next iteration of the `for calc in calculations` loop.

```python
    new_column = deep_copy(calc["element"])
```
This is the key difference from earlier broken versions. Instead of constructing a new `ET.Element` with only a few hardcoded attributes, we deep copy the entire source element — preserving `caption`, `datatype`, `role`, `type`, any other attributes Tableau added, and all child elements.

```python
    calc_el = new_column.find("calculation")
    if calc_el is not None:
        calc_el.set("formula", mapping_replace(calc_el.attrib.get("formula", ""), mapping))
```
After copying, applies the field name mapping to the formula. We do this on the copy, not the original — so source is never modified.

```python
    insert_pos = find_column_insert_position(target_ds)
    target_ds.insert(insert_pos, new_column)
```
Calculates the correct insertion index and inserts the element there. `ET.Element.insert(index, element)` works like `list.insert()`.

```python
    tree.write(dest_twb_path, encoding="utf-8", xml_declaration=True)
    return real_datasources
```
Writes the modified XML back to the `.twb` file on disk. Returns the datasource list so the pipeline can pass it directly to `merge_folders` without re-parsing.

---

## EXECUTION PIPELINE (Lines 482–526)

```python
if __name__ == "__main__":
```
Standard Python guard. The code inside this block only runs when you execute the script directly — not when it's imported as a module. Keeps the script safe to import elsewhere.

```python
    create_backup(DEST_TWBX, label="dest")
```
**Step 0.** Backs up the destination file before touching anything. This runs first, unconditionally.

```python
    source_twb = unzip_twbx(SOURCE_TWBX, source_dir)
    dest_twb   = unzip_twbx(DEST_TWBX,   dest_dir)
```
**Step 1.** Both workbooks get unzipped into separate subdirectories. Returns the path to the `.twb` file inside each.

```python
    calculations       = extract_calculated_fields(source_twb)
    source_folders_map = extract_folders(source_twb)
```
**Step 2.** Reads everything we need from source — the calculated fields and the folder structure. Source is never written to after this point.

```python
    copy_required_parameters(source_twb, dest_twb, calculations, FIELD_MAPPING)
```
**Step 3.** Parameters are copied BEFORE calculated fields. This is order-dependent — Tableau validates field references when loading, so parameters must already exist when the calculated fields that reference them are inserted.

```python
    real_dest_datasources = insert_calculations(dest_twb, calculations, FIELD_MAPPING)
```
**Step 4.** Inserts calculated fields. Returns the datasource list.

```python
    dest_tree = ET.parse(dest_twb)
    dest_root = dest_tree.getroot()
    real_dest_datasources = get_real_datasources(dest_root)
```
**Step 5 setup.** Re-parses the destination `.twb` from disk. This is necessary because Step 4 wrote the file to disk via `tree.write()`. If we used the old in-memory tree from Step 4's return value, and Step 3 had already written the file, we'd be working off a partially stale tree. Re-parsing guarantees we're working on the full, current state.

```python
    merge_folders(dest_root, real_dest_datasources, source_folders_map)
    set_group_by_folder(dest_root, real_dest_datasources)
    dest_tree.write(dest_twb, encoding="utf-8", xml_declaration=True)
```
**Steps 5 & 6.** Merge folders and set the group-by-folder preference, then write the final result to disk once — not after each operation.

```python
    repack_twbx(dest_dir, DEST_TWBX)
```
**Step 7.** Zips the entire modified `dest/` directory back into a `.twbx` file, overwriting the destination. At this point the file is ready for Tableau.
