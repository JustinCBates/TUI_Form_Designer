from pathlib import Path
from typing import Dict, Any
import yaml


class DefaultsPreprocessor:
    """
    Merges defaults from the main layout's defaults_file and any
    sublayout_defaults referenced by sublayouts into a unified defaults dict.
    """

    def __init__(self, layouts_dir: Path):
        self.layouts_dir = Path(layouts_dir)

    def _load_defaults(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
                return data.get("defaults", {})
        except FileNotFoundError:
            return {}

    def merge_defaults(
        self,
        layout_path: Path,
        layout_data: Dict[str, Any],
        save_unified: bool = False,
        output_path: Path = None,
    ) -> Dict[str, Any]:
        unified: Dict[str, Any] = {}

        main_defaults_rel = layout_data.get("defaults_file")
        if main_defaults_rel:
            main_path = (layout_path.parent / main_defaults_rel).resolve()
            unified.update(self._load_defaults(main_path))

        for step in layout_data.get("steps", []):
            sub = step.get("sublayout")
            if sub:
                sub_path = (layout_path.parent / sub).resolve()
                try:
                    with open(sub_path, "r") as sf:
                        sub_data = yaml.safe_load(sf) or {}
                    sub_defaults_rel = sub_data.get("sublayout_defaults")
                    if sub_defaults_rel:
                        sub_defaults_path = (sub_path.parent / sub_defaults_rel).resolve()
                        unified.update(self._load_defaults(sub_defaults_path))
                except FileNotFoundError:
                    continue

        if save_unified and output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as out:
                yaml.safe_dump({"defaults": unified}, out, default_flow_style=False, sort_keys=False)

        return {"defaults": unified}
