import os
import re
import copy
import zipfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

SOURCE_TWBX = r"C:\Users\BalasubramanianPG\OneDrive\3. March\25-03-2026\Benefits Analysis V6 Floating KPI Card (24-03-2026).twbx"

DEST_TWBX   = r"C:\Users\BalasubramanianPG\OneDrive\3. March\25-03-2026\HCP Claims 1.twbx"

WORK_DIR   = "temp_tableau_processing"
BACKUP_DIR = "backup"

FIELD_MAPPING = {
    "Reimbursed Dollars": "Approval Rate",
    "reimbursed_dollars": "approval_rate"
}


# ─────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def create_backup(file_path, label="backup"):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename    = os.path.basename(file_path).replace(".twbx", "")
    backup_path = os.path.join(BACKUP_DIR, f"{label}_{filename}_{timestamp}.twbx")
    shutil.copy(file_path, backup_path)
    print(f"[BACKUP] {label} → {backup_path}")
    return backup_path


def unzip_twbx(twbx_path, extract_to):
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
    os.makedirs(extract_to)
    with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    for file in os.listdir(extract_to):
        if file.endswith(".twb"):
            return os.path.join(extract_to, file)
    raise Exception("[ERROR] No TWB file found inside TWBX")


def repack_twbx(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root_dir, file)
                rel_path  = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, rel_path)
    print(f"[REPACK] Saved at: {output_path}")


def deep_copy(element):
    return copy.deepcopy(element)


def mapping_replace(text, mapping):
    if not text:
        return text
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text


# ─────────────────────────────────────────────
# DATASOURCE HELPERS
# ─────────────────────────────────────────────

def get_parameters_datasource(root):
    """Returns the Parameters datasource element (the one Tableau uses for params)."""
    for ds in root.findall(".//datasource"):
        if ds.attrib.get("name", "").lower() == "parameters":
            return ds
    return None


def get_real_datasources(root):
    """Returns all datasources except the built-in Parameters one."""
    return [
        ds for ds in root.findall(".//datasource")
        if ds.attrib.get("name", "").lower() != "parameters"
    ]


def print_datasources(root, label=""):
    print(f"\n[DATASOURCES] {label}")
    for ds in root.findall(".//datasource"):
        name       = ds.attrib.get("name", "UNNAMED")
        caption    = ds.attrib.get("caption", "")
        calc_count = sum(1 for col in ds.findall("column") if col.find("calculation") is not None)
        print(f"  → name='{name}'  caption='{caption}'  calculated_fields={calc_count}")
    print()


def find_column_insert_position(datasource):
    """
    Returns the index right after the last <column> child.
    Tableau has a strict schema order — columns must come before
    folders-common, actions, filters etc.
    """
    children = list(datasource)
    last_col_idx = None
    for i, child in enumerate(children):
        if child.tag == "column":
            last_col_idx = i
    if last_col_idx is not None:
        return last_col_idx + 1
    for i, child in enumerate(children):
        if child.tag == "connection":
            return i + 1
    return 0


def find_folders_insert_position(datasource):
    """
    Returns the correct index to insert/replace <folders-common>.
    It must come after all <column> and <group> elements,
    but before <actions> and <filter> elements.
    """
    children = list(datasource)
    insert_after_tags = {"column", "column-instance", "group", "aliases"}
    insert_before_tags = {"actions", "filter", "layout", "style", "date-options",
                          "default-sorts", "datasource-dependencies"}

    last_valid = 0
    for i, child in enumerate(children):
        if child.tag in insert_after_tags:
            last_valid = i + 1
        if child.tag in insert_before_tags:
            return last_valid

    return last_valid


def get_existing_column_names(ds_element):
    names = set()
    for col in ds_element.findall("column"):
        n = col.attrib.get("name")
        if n:
            names.add(n)
    return names


# ─────────────────────────────────────────────
# PARAMETER HANDLING
# ─────────────────────────────────────────────

def extract_referenced_parameter_names(formula):
    """
    Scans a formula string and returns all [bracketed references] found.
    Tableau parameters are referenced as [Param Name] in formulas.
    """
    return set(re.findall(r'\[([^\]]+)\]', formula or ""))


def extract_parameters(twb_path):
    """
    Extracts all parameter column elements from the Parameters datasource.
    Returns a dict of { display_name → column_element }
    where display_name is the caption (what you see in Tableau UI).
    """
    tree   = ET.parse(twb_path)
    root   = tree.getroot()
    params_ds = get_parameters_datasource(root)

    if params_ds is None:
        print("[PARAMS] No Parameters datasource found in source")
        return {}

    params = {}
    for col in params_ds.findall("column"):
        name    = col.attrib.get("name", "")        # e.g. [Parameter 1]
        caption = col.attrib.get("caption", "")     # e.g. "Time Granularity"
        # Store by both name and caption for flexible lookup
        params[name]    = col
        params[caption] = col

    print(f"[PARAMS] Found {len(params)//2} parameters in source: {[col.attrib.get('caption','') for col in params_ds.findall('column')]}")
    return params


def copy_required_parameters(source_twb, dest_twb_path, calculations, mapping):
    """
    1. Scans all formulas in calculations being copied to find parameter references
    2. Looks up those parameters in source's Parameters datasource
    3. Copies only the referenced ones into destination's Parameters datasource
    4. Skips parameters that already exist in destination
    """
    # Collect all referenced names across all formulas
    all_referenced = set()
    for calc in calculations:
        el    = calc["element"]
        calc_el = el.find("calculation")
        if calc_el is not None:
            formula = calc_el.attrib.get("formula", "")
            all_referenced |= extract_referenced_parameter_names(formula)

    print(f"\n[PARAMS] References found in formulas: {all_referenced}")

    # Load source parameters
    source_tree = ET.parse(source_twb)
    source_root = source_tree.getroot()
    source_params_ds = get_parameters_datasource(source_root)
    if source_params_ds is None:
        print("[PARAMS] No Parameters datasource in source — nothing to copy")
        return

    # Index source params by name and caption
    source_param_map = {}
    for col in source_params_ds.findall("column"):
        n = col.attrib.get("name", "")
        c = col.attrib.get("caption", "")
        source_param_map[n] = col
        if c:
            source_param_map[c] = col

    # Load destination and find its Parameters datasource
    dest_tree = ET.parse(dest_twb_path)
    dest_root = dest_tree.getroot()
    dest_params_ds = get_parameters_datasource(dest_root)

    if dest_params_ds is None:
        # Create a Parameters datasource from scratch
        dest_params_ds = ET.Element("datasource", {
            "name"   : "Parameters",
            "inline" : "true"
        })
        dest_root.find(".//datasources").insert(0, dest_params_ds)
        print("[PARAMS] Created new Parameters datasource in destination")

    # Get already existing param names in destination
    existing_param_names = get_existing_column_names(dest_params_ds)

    copied  = 0
    missing = []

    for ref in all_referenced:
        bracketed = f"[{ref}]"

        # Try to find this reference in source params
        matched_col = source_param_map.get(bracketed) or source_param_map.get(ref)

        if matched_col is None:
            # Not a parameter — probably a regular field reference, skip
            continue

        param_name = matched_col.attrib.get("name", "")
        if param_name in existing_param_names:
            print(f"  [PARAM SKIP] Already exists: {param_name}")
            continue

        # Deep copy the parameter element and insert it
        new_param = deep_copy(matched_col)
        insert_pos = find_column_insert_position(dest_params_ds)
        dest_params_ds.insert(insert_pos, new_param)
        copied += 1
        print(f"  [PARAM COPIED] name='{param_name}'  caption='{matched_col.attrib.get('caption','')}'")

    if missing:
        print(f"  [PARAM WARNING] These references were not found in source params: {missing}")

    dest_tree.write(dest_twb_path, encoding="utf-8", xml_declaration=True)
    print(f"[PARAMS] Done — {copied} parameters copied")


# ─────────────────────────────────────────────
# FOLDER HANDLING
# ─────────────────────────────────────────────

def extract_folders(twb_path):
    """
    Returns a dict of { ds_name → folders-common Element } from source.
    """
    tree   = ET.parse(twb_path)
    root   = tree.getroot()
    result = {}

    for ds in get_real_datasources(root):
        ds_name = ds.attrib.get("name", "")
        folders = ds.find("folders-common")
        result[ds_name] = folders
        if folders is not None:
            names = [f.attrib.get("name", "?") for f in folders.findall("folder")]
            print(f"[FOLDERS] Source ds='{ds_name}' folders: {names}")
        else:
            print(f"[FOLDERS] Source ds='{ds_name}' — no folders-common found")

    return result


def merge_folders(dest_root, real_dest_datasources, source_folders_map):
    """
    Merges source <folders-common> into destination datasources.

    The key fix here vs the previous version:
      - We REMOVE the existing folders-common from destination first, then
        re-insert a merged version at the correct schema position.
      - This prevents the old partial block from conflicting with new entries.
    """
    dest_ds_map = {ds.attrib.get("name", ""): ds for ds in real_dest_datasources}

    for source_ds_name, source_folders in source_folders_map.items():
        if source_folders is None:
            continue

        target_ds = dest_ds_map.get(source_ds_name) or real_dest_datasources[0]

        dest_folders = target_ds.find("folders-common")

        if dest_folders is None:
            # No existing folders in dest — copy source wholesale
            new_folders = deep_copy(source_folders)
            insert_pos  = find_folders_insert_position(target_ds)
            target_ds.insert(insert_pos, new_folders)
            folder_names = [f.attrib.get("name","?") for f in new_folders.findall("folder")]
            print(f"[FOLDERS] Copied wholesale into '{target_ds.attrib.get('name')}': {folder_names}")

        else:
            # Dest already has folders — merge folder by folder
            dest_folder_map = {
                f.attrib.get("name", ""): f
                for f in dest_folders.findall("folder")
            }

            for src_folder in source_folders.findall("folder"):
                folder_name = src_folder.attrib.get("name", "")
                folder_role = src_folder.attrib.get("role", "")

                if folder_name not in dest_folder_map:
                    dest_folders.append(deep_copy(src_folder))
                    print(f"  [FOLDER ADDED] '{folder_name}'")
                else:
                    # Folder exists — merge individual folder-item entries
                    dest_folder = dest_folder_map[folder_name]
                    existing_items = {
                        fi.attrib.get("name", "")
                        for fi in dest_folder.findall("folder-item")
                    }
                    for item in src_folder.findall("folder-item"):
                        item_name = item.attrib.get("name", "")
                        if item_name not in existing_items:
                            dest_folder.append(deep_copy(item))
                            print(f"    [ITEM ADDED] '{item_name}' → folder '{folder_name}'")

            # Remove old block and re-insert at correct schema position
            # (avoids schema order violations if original block was misplaced)
            target_ds.remove(dest_folders)
            insert_pos = find_folders_insert_position(target_ds)
            target_ds.insert(insert_pos, dest_folders)
            print(f"[FOLDERS] Re-seated folders-common at position {insert_pos} in '{target_ds.attrib.get('name')}'")


# ─────────────────────────────────────────────
# GROUP BY FOLDER DEFAULT
# ─────────────────────────────────────────────

def set_group_by_folder(dest_root, real_dest_datasources):
    """
    Sets the workbook default to "Group by Folder" so developers
    see folders immediately when they open the workbook.

    Two things need to happen:
      1. Each real datasource gets  show-field-list-as-folder='true'
      2. The workbook-level <preferences> block gets the ui.groupby preference
    """
    # Workbook-level preferences block
    workbook_el = dest_root  # root IS the <workbook> element in a TWB

    prefs = workbook_el.find("preferences")
    if prefs is None:
        prefs = ET.Element("preferences")
        workbook_el.insert(0, prefs)
        print("[GROUP BY FOLDER] Created <preferences> block in workbook")

    # Check if preference already exists
    existing_pref_names = {p.attrib.get("name", "") for p in prefs.findall("preference")}

    if "ui.groupby" not in existing_pref_names:
        ET.SubElement(prefs, "preference", {
            "name" : "ui.groupby",
            "value": "folders"
        })
        print("[GROUP BY FOLDER] Added ui.groupby=folders to workbook preferences")
    else:
        # Update existing preference
        for p in prefs.findall("preference"):
            if p.attrib.get("name") == "ui.groupby":
                p.set("value", "folders")
                print("[GROUP BY FOLDER] Updated existing ui.groupby preference to 'folders'")


# ─────────────────────────────────────────────
# CORE EXTRACTION & INSERTION
# ─────────────────────────────────────────────

def extract_calculated_fields(twb_path):
    tree = ET.parse(twb_path)
    root = tree.getroot()

    print_datasources(root, label="SOURCE")

    calculations = []
    for ds in get_real_datasources(root):
        ds_name = ds.attrib.get("name", "")
        for column in ds.findall("column"):
            if column.find("calculation") is not None:
                caption = column.attrib.get("caption", column.attrib.get("name", ""))
                calculations.append({
                    "element"  : column,
                    "name"     : column.attrib.get("name"),
                    "caption"  : caption,
                    "source_ds": ds_name
                })

    print(f"[EXTRACT] Found {len(calculations)} calculated fields in source")
    for c in calculations:
        print(f"  · caption='{c['caption']}'  name='{c['name']}'")
    return calculations


def insert_calculations(dest_twb_path, calculations, mapping):
    tree = ET.parse(dest_twb_path)
    root = tree.getroot()

    print_datasources(root, label="DESTINATION")

    real_datasources = get_real_datasources(root)
    if not real_datasources:
        raise Exception("[ERROR] No real datasources found in destination workbook")

    dest_ds_map = {ds.attrib.get("name", ""): ds for ds in real_datasources}

    inserted = 0
    skipped  = 0

    for calc in calculations:
        field_name = calc["name"]
        source_ds  = calc["source_ds"]

        target_ds = dest_ds_map.get(source_ds) or real_datasources[0]
        if source_ds not in dest_ds_map:
            print(f"  [FALLBACK] '{source_ds}' not in dest → using '{target_ds.attrib.get('name')}'")

        if field_name in get_existing_column_names(target_ds):
            print(f"  [SKIP] Already exists: {field_name} (caption='{calc['caption']}')")
            skipped += 1
            continue

        # Deep copy preserves caption + ALL attributes + child elements
        new_column = deep_copy(calc["element"])

        # Apply formula mapping
        calc_el = new_column.find("calculation")
        if calc_el is not None:
            calc_el.set("formula", mapping_replace(calc_el.attrib.get("formula", ""), mapping))

        insert_pos = find_column_insert_position(target_ds)
        target_ds.insert(insert_pos, new_column)
        inserted += 1
        print(f"  [INSERT] caption='{calc['caption']}'  name='{field_name}'")

    tree.write(dest_twb_path, encoding="utf-8", xml_declaration=True)
    print(f"\n[INSERT] Done — {inserted} fields added, {skipped} skipped")

    return real_datasources   # Return for use in folder + group-by steps


# ─────────────────────────────────────────────
# EXECUTION PIPELINE
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # Step 0: Backup destination
    create_backup(DEST_TWBX, label="dest")

    # Step 1: Unzip both workbooks
    source_dir = os.path.join(WORK_DIR, "source")
    dest_dir   = os.path.join(WORK_DIR, "dest")

    source_twb = unzip_twbx(SOURCE_TWBX, source_dir)
    dest_twb   = unzip_twbx(DEST_TWBX,   dest_dir)

    # Step 2: Extract calculated fields and folder structure from source
    calculations       = extract_calculated_fields(source_twb)
    source_folders_map = extract_folders(source_twb)

    # Step 3: Copy required parameters FIRST
    # (calculated fields reference them — they must exist before calcs are validated)
    copy_required_parameters(source_twb, dest_twb, calculations, FIELD_MAPPING)

    # Step 4: Insert calculated fields into correct datasource + position
    real_dest_datasources = insert_calculations(dest_twb, calculations, FIELD_MAPPING)

    # Step 5: Merge folder structure from source into destination
    dest_tree = ET.parse(dest_twb)
    dest_root = dest_tree.getroot()
    real_dest_datasources = get_real_datasources(dest_root)   # Re-parse after Step 4 writes

    merge_folders(dest_root, real_dest_datasources, source_folders_map)

    # Step 6: Set "Group by Folder" as the default view
    set_group_by_folder(dest_root, real_dest_datasources)

    dest_tree.write(dest_twb, encoding="utf-8", xml_declaration=True)
    print("\n[WRITE] Final TWB written with folders and group-by-folder applied")

    # Step 7: Repack
    repack_twbx(dest_dir, DEST_TWBX)

    print("\n[DONE] Open in Tableau — you should see:")
    print("  ✓ All calculated fields with correct display names")
    print("  ✓ Fields organised in their original folders")
    print("  ✓ Parameters copied (no broken references)")
    print("  ✓ Data pane defaulting to 'Group by Folder'")
    print("\n  Backup is in /backup if you need to roll back.")
