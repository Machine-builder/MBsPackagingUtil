import datetime

def generate_release_notes(
        config: dict,
        selected_pack: dict,
        release_type: int,
        version_str: str,
        release_datetime: datetime.datetime,
        text_release_headline: str,
        text_whats_new: str,
        text_fixes: str,
        text_other_notes: str):

    if release_type == 0:
        release_type_text = config["notes"]["type_major"]
    elif release_type == 1:
        release_type_text = config["notes"]["type_minor"]
    elif release_type == 2:
        release_type_text = config["notes"]["type_patch"]
    elif release_type == 3:
        release_type_text = config["notes"]["type_repackage"]
    
    if text_release_headline:
        headline_text = text_release_headline+"\n\n"

    if text_whats_new:
        whats_new_text = "### "+config["notes"]["header_whats_new"]+"\n"+text_whats_new+"\n\n"
    
    if text_fixes:
        fixes_text = "### "+config["notes"]["header_bug_fixes"]+"\n"+text_fixes+"\n\n"
    
    if text_other_notes:
        other_notes_text = "### "+config["notes"]["header_other_notes"]+"\n"+text_other_notes+"\n\n"
    
    result = (
        f"# {selected_pack['packaged_name']} Version {version_str}\n"
        f"**{release_type_text}**\n\n"
        f"{headline_text}"
        f"{whats_new_text}"
        f"{fixes_text}"
        f"{other_notes_text}")

    if config["notes"]["include_ctime"]:
        result += release_datetime.ctime()
    
    return result