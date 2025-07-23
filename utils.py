import shutil
from pathlib import Path

# apply_suggestion() helper for file operations
def apply_suggestion(file_meta: dict, suggestion: dict, root_folder: str = None, auto_confirm: bool = False) -> None:
    original = Path(file_meta['path'])
    base_dir = Path(root_folder) if root_folder else original.parent

    # Delete
    if suggestion.get('delete'):
        if auto_confirm or input(f"Delete {original.name}? [y/N]: ").lower() == 'y':
            try:
                original.unlink()
                print(f"Deleted {original}")
            except Exception as e:
                print(f"Error deleting {original}: {e}")
        return

    # Rename/move
    new_name = suggestion.get('suggested_name', original.name)
    target = suggestion.get('suggested_folder', '')
    dest = base_dir / target if target else base_dir
    dest.mkdir(parents=True, exist_ok=True)
    new_path = dest / new_name

    # Prompt
    actions = []
    if new_name != original.name:
        actions.append(f"rename to '{new_name}'")
    if dest != original.parent:
        actions.append(f"move to '{dest}'")
    prompt = f"Apply to {original.name}: " + ", ".join(actions) + "? [y/N]: "

    if not actions:
        return
    if auto_confirm or input(prompt).lower() == 'y':
        try:
            shutil.move(str(original), str(new_path))
            print(f"Moved {original} -> {new_path}")
        except Exception as e:
            print(f"Error moving {original}: {e}")
    else:
        print(f"Skipped {original}")
